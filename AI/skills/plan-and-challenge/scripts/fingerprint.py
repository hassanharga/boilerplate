#!/usr/bin/env python3
"""Exact-byte fingerprints and the plan-approval-v2 execution gate.

fingerprint.py FILE [FILE ...] prints algorithm<TAB>sha256<TAB>path.
fingerprint.py --verify REVIEW --plan PLAN verifies saved approval and review evidence.
Exit 0: verified; 1: gate failed; 2: usage or print-mode I/O error.
This script is read-only. Keep both installed copies byte-identical.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re
import sys

ALGORITHM = 'sha256-exact-bytes-v1'
SCHEMA = 'plan-approval-v2'
STAMP = ('> **Execution gate:** REQUIRED: Before implementation, invoke `implement-plan` '
         'with this plan path. It opens the linked review, requires `APPROVED`, and recomputes '
         'the exact-byte fingerprints. A missing or mismatched approval returns to '
         '`plan-and-challenge`; a valid approval continues with the execution workflow or '
         'routing rule named by this plan.')
ARTIFACTS = (('Task snapshot', 'Task fingerprint'), ('Plan', 'Plan fingerprint'),
             ('Specification', 'Specification fingerprint'))
PROTOCOL_FIELDS = ('mode', 'challenge venue', 'current owner', 'next action',
                   'required review lens', 'round', 'review dispatches used',
                   'reviser dispatches used', 'delegation')
BUDGETS = (('round', 2), ('review dispatches used', 4), ('reviser dispatches used', 2))
# Full mode spends a challenger and a fresh verifier; lightweight spends its one challenger.
REQUIRED_REVIEWS = {'full': 2, 'lightweight': 1, 'local-fallback': 0}


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def concrete(value: str) -> bool:
    return (bool(value.strip()) and value.lower() not in
            {'none', 'pending', 'tbd', 'n/a', 'unknown'} and '<' not in value and '>' not in value)


def visible_lines(text: str) -> list[str]:
    """Exclude fenced examples and HTML comments before interpreting protocol text."""
    text = re.sub(r'<!--.*?(?:-->|\Z)', lambda m: '\n' * m[0].count('\n'), text, flags=re.S)
    lines: list[str] = []
    marker = ''
    length = 0
    for line in text.splitlines():
        fence = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            if fence and fence[1][0] == marker and len(fence[1]) >= length and not fence[2].strip():
                marker = ''
            continue
        if fence:
            marker, length = fence[1][0], len(fence[1])
            continue
        lines.append(line)
    return lines


def section(lines: list[str], heading: str) -> tuple[int, dict[str, str]]:
    matches = [i for i, line in enumerate(lines) if line == heading]
    if not matches:
        raise ValueError(f'missing {heading}')
    start = matches[-1]
    values: dict[str, str] = {}
    for line in lines[start + 1:]:
        if re.match(r'^#{1,6} ', line):
            break
        item = re.fullmatch(r'- ([^:]+):\s*(.*)', line)
        if item:
            key = item[1].strip().lower()
            if key in values:
                raise ValueError(f'duplicate field in {heading}: {key}')
            value = item[2].strip()
            values[key] = value[1:-1] if value.startswith('`') and value.endswith('`') else value
    return start, values


def required(values: dict[str, str], key: str) -> str:
    value = values.get(key.lower(), '')
    if not concrete(value):
        raise ValueError(f'{key}: missing or unfinished value')
    return value


def resolve(raw: str, base: Path) -> Path:
    path = (base / raw).resolve(strict=True)
    if not path.is_file():
        raise ValueError(f'not a file: {path}')
    return path


def artifact(values: dict[str, str], path_key: str, hash_key: str, base: Path,
             optional: bool = False) -> Path | None:
    raw, expected = values.get(path_key.lower(), ''), values.get(hash_key.lower(), '')
    if optional and raw == expected == 'none':
        return None
    required(values, path_key)
    required(values, hash_key)
    if not re.fullmatch(r'[0-9a-f]{64}', expected) or len(set(expected)) == 1:
        raise ValueError(f'{hash_key}: expected a concrete SHA-256 digest')
    path = resolve(raw, base)
    if fingerprint(path) != expected:
        raise ValueError(f'{path_key}: digest mismatch for {path}')
    return path


def validate_decision_history(lines: list[str], run_index: int, run_id: str) -> None:
    """Only Pending/READY may be followed by another decision in the current run."""
    indexes = [i for i in range(run_index + 1, len(lines)) if lines[i] == '## Final Decision']
    previous = None
    allowed = {None: {'Pending', 'READY_FOR_USER_APPROVAL', 'BLOCKED', 'APPROVED'},
               'Pending': {'Pending', 'READY_FOR_USER_APPROVAL', 'BLOCKED', 'APPROVED'},
               'READY_FOR_USER_APPROVAL': {'APPROVED'}, 'BLOCKED': set(), 'APPROVED': set()}
    for position, index in enumerate(indexes):
        end = indexes[position + 1] if position + 1 < len(indexes) else len(lines)
        _, decision = section(lines[index:end], '## Final Decision')
        status = decision.get('status')
        if decision.get('run id') != run_id or status not in allowed[previous]:
            raise ValueError('invalid decision transition or run identity; terminal decisions need a new run')
        if previous == 'READY_FOR_USER_APPROVAL' and decision.get('review mode') != 'local-fallback':
            raise ValueError('READY requires explicit user approval through local-fallback')
        previous = status


def validate_decision_body(lines: list[str], values: dict[str, str]) -> None:
    """The terminal decision contains only schema fields, blanks and ignored examples."""
    keys = {'status', 'approval schema', 'fingerprint algorithm', 'run id', 'review mode',
            'evidence', 'evidence fingerprint', 'open minor findings', 'verdict by', 'recorded by'}
    keys.update(key.lower() for pair in ARTIFACTS for key in pair)
    if values.keys() - keys or any(line.strip() and not re.fullmatch(r'- ([^:]+):\s*(.*)', line)
                                  for line in lines):
        raise ValueError('unexpected content after final decision; review activity needs a new run')


def validate_minors(value: str, plan_text: str) -> None:
    """Zero, or a count followed by unique finding IDs and actionable dispositions."""
    if value.lower() in {'0', 'none'}:
        return
    parts = [part.strip() for part in value.split(';')]
    if not re.fullmatch(r'[1-9][0-9]*', parts[0]) or int(parts[0]) != len(parts) - 1:
        raise ValueError('Open minor findings: use 0/none or count; ID: disposition')
    ids = set()
    for part in parts[1:]:
        item = re.fullmatch(r'(PLAN-[0-9]{3,}): (address in task|leave because) (.+)', part)
        if not item or item[1] in ids or not concrete(item[3]):
            raise ValueError('Open minor findings: each unique PLAN ID needs a task or leave reason')
        ids.add(item[1])
        # ID targets must occur as task declarations, not substrings or prose mentions.
        target = item[3].split()[0]
        if item[2] == 'address in task' and re.fullmatch(r'[A-Za-z]*[0-9][A-Za-z0-9._-]*', target):
            declaration = (r'^\s*(?:#{1,6}\s+|[-*]\s+(?:\[[ xX]\]\s+)?|\|\s*)?'
                           r'(?:Task\s+)?(?:\*\*|`)?' + re.escape(target) +
                           r'(?:\*\*|`)?(?:\s*[:|—–-]\s+|\s*$)')
            if not re.search(declaration, plan_text, re.M | re.I):
                raise ValueError(f'Open minor findings: {item[1]} assigns task {target}, absent from task declarations')


def validate_protocol_state(lines: list[str], mode: str) -> None:
    """The approved run states its own mode and stays inside the documented review budget."""
    _, state = section(lines, '## Protocol State')
    unfilled = [key for key in PROTOCOL_FIELDS if not concrete(state.get(key, ''))]
    if unfilled:
        raise ValueError(f'Protocol State: missing or unfilled {", ".join(unfilled)}')
    if state['mode'] != mode:
        raise ValueError('Protocol State mode does not match the approved review mode')
    used = {}
    for key, limit in BUDGETS:
        counter = re.fullmatch(r'([0-9]+) of ([0-9]+)', state[key])
        if not counter or int(counter[2]) != limit or int(counter[1]) > limit:
            raise ValueError(f'{key}: expected "N of {limit}" within the documented budget')
        used[key] = int(counter[1])
    if not used['round']:
        raise ValueError('Round: an approved run records at least one completed round')
    if used['review dispatches used'] < REQUIRED_REVIEWS[mode]:
        raise ValueError(f'{mode} approval needs at least {REQUIRED_REVIEWS[mode]} '
                         'recorded review dispatches')
    if mode == 'lightweight' and (used['round'] != 1 or
                                  used['review dispatches used'] > 2 or
                                  used['reviser dispatches used'] > 1):
        raise ValueError('lightweight permits one round, two reviews and one revision')
    if mode == 'full' and used['review dispatches used'] < 2 * used['round']:
        raise ValueError('each completed full round needs a challenger and a verifier')


def metadata(lines: list[str], label: str) -> str:
    prefix = f'> **{label}:**'
    candidates = [line for line in lines if line.startswith(prefix)]
    if len(candidates) != 1:
        raise ValueError(f'plan must contain exactly one {label} declaration')
    match = re.fullmatch(re.escape(prefix) + r' `([^`]+)`', candidates[0])
    if not match:
        raise ValueError(f'{label}: expected a literal backtick-delimited path or none')
    return match[1]


def verify(review_arg: str, plan_arg: str) -> int:
    try:
        review = Path(review_arg).resolve(strict=True)
        lines = visible_lines(review.read_text(encoding='utf-8'))
        decision_index, decision = section(lines, '## Final Decision')
        runs = [(i, line.removeprefix('## Run ')) for i, line in enumerate(lines)
                if line.startswith('## Run ')]
        if not runs or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', rid)
                           for _, rid in runs):
            raise ValueError('missing or invalid review run heading; return for a new review')
        if len({rid for _, rid in runs}) != len(runs):
            raise ValueError('review run IDs must be unique')
        run_index, run_id = runs[-1]
        if decision_index < run_index or decision.get('run id') != run_id:
            raise ValueError('the latest run has no matching final decision')
        validate_decision_history(lines, run_index, run_id)
        validate_decision_body(lines[decision_index + 1:], decision)
        if decision.get('approval schema') != SCHEMA:
            raise ValueError(f'approval requires {SCHEMA}; legacy approvals need a new review')
        if decision.get('status') != 'APPROVED':
            raise ValueError('status is not APPROVED')
        if decision.get('fingerprint algorithm') != ALGORITHM:
            raise ValueError(f'fingerprint algorithm must be {ALGORITHM}')
        for key in ('Verdict by', 'Recorded by'):
            required(decision, key)
        base = review.parent
        paths = [artifact(decision, pk, hk, base, optional=pk == 'Specification')
                 for pk, hk in ARTIFACTS]
        task, plan, spec = paths
        if plan is None or task is None:
            raise ValueError('task snapshot and plan are required')
        if plan != Path(plan_arg).resolve(strict=True):
            raise ValueError('approval names a different plan from the supplied plan')
        snapshot = plan.parent / 'task.md'
        if snapshot.is_symlink() or not snapshot.is_file() or task != snapshot.resolve(strict=True):
            raise ValueError('task snapshot must be a regular non-symlink task.md beside the supplied plan')
        plan_lines = visible_lines(plan.read_text(encoding='utf-8'))
        validate_minors(decision.get('open minor findings', ''), '\n'.join(plan_lines))
        stamps = [line for line in plan_lines if line.startswith('> **Execution gate:**')]
        if stamps != [STAMP]:
            raise ValueError('plan requires the single literal execution-gate stamp')
        if resolve(metadata(plan_lines, 'Review'), plan.parent) != review:
            raise ValueError('plan review link does not name the supplied review')
        declaration = metadata(plan_lines, 'Specification')
        declared_spec = None if declaration == 'none' else resolve(declaration, plan.parent)
        if declared_spec != spec:
            raise ValueError('plan specification declaration does not match approval')
        evidence_path = artifact(decision, 'Evidence', 'Evidence fingerprint', base)
        if evidence_path is None:
            raise ValueError('review evidence is required')
        evidence_lines = visible_lines(evidence_path.read_text(encoding='utf-8'))
        if evidence_lines.count('## Review Evidence') != 1:
            raise ValueError('evidence requires exactly one Review Evidence block')
        _, evidence = section(evidence_lines, '## Review Evidence')
        if evidence.get('run id') != run_id:
            raise ValueError('evidence belongs to another review run')
        modes = {'full': ('verifier', 'CLEAR'),
                 'lightweight': ('lightweight-challenger', 'CLEAR'),
                 'local-fallback': ('user', 'APPROVED')}
        mode = required(decision, 'Review mode')
        if mode not in modes or (evidence.get('role'), evidence.get('verdict')) != modes[mode]:
            raise ValueError('review mode requires a qualifying independent verdict or explicit user approval')
        validate_protocol_state(lines[run_index:], mode)
        if required(evidence, 'Reviewer') != decision['verdict by']:
            raise ValueError('verdict reviewer does not match approval')
        if decision['verdict by'] == decision['recorded by']:
            raise ValueError('the recording controller cannot also be the reviewer that cleared the plan')
        if mode == 'local-fallback':
            required(evidence, 'User approval')
            if evidence['reviewer'] != 'user':
                raise ValueError('local fallback must be explicitly approved by the user')
        for (pk, hk), approved_path in zip(ARTIFACTS, paths):
            reviewed_path = artifact(evidence, pk, hk, evidence_path.parent,
                                     optional=pk == 'Specification')
            if reviewed_path != approved_path or evidence.get(hk.lower()) != decision.get(hk.lower()):
                raise ValueError(f'{pk}: saved approval differs from independently reviewed bytes')
        print(f'GATE PASSED: {SCHEMA}, run {run_id}, {plan}')
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'GATE FAILED — return to plan-and-challenge: {exc}', file=sys.stderr)
        return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='*')
    parser.add_argument('--verify', metavar='REVIEW')
    parser.add_argument('--plan', metavar='PLAN')
    args = parser.parse_args(argv[1:])
    if args.verify:
        if args.files or not args.plan:
            parser.error('--verify requires --plan and accepts no positional files')
        return verify(args.verify, args.plan)
    if args.plan or not args.files:
        parser.error('supply files, or --verify REVIEW --plan PLAN')
    try:
        for name in args.files:
            path = Path(name)
            print(f'{ALGORITHM}\t{fingerprint(path)}\t{path}')
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
