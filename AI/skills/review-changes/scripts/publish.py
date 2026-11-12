#!/usr/bin/env python3
"""Publish selected, authorized findings; dry-run by default.

Usage: python3 publish.py <plan.json> [--yes] [--json] [--journal path]
Plan: {"repo":"owner/name","pr":123,"commit":"<reviewed SHA>",
       "event":"COMMENT|REQUEST_CHANGES","opener":"one sentence",
       "comments":[{"path":"src/a.ts","line":42,"side":"RIGHT","body":"..."}]}
Optional multiline fields: start_line and start_side. Approval is refused.
Before --yes, refresh/revalidate the diff, checks, and feedback per the publishing
reference. This helper guards state and identity; it cannot judge findings or
user authorization. Writes are sequential, pinned, and journaled. After a lost
response, read destination state before any dependent write. Exit 0: every item
observed; 1: stopped/partial; 2: invalid input. No automatic write retries.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

spec = importlib.util.spec_from_file_location('publication_state', Path(__file__).with_name('publication-state.py'))
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def gh(*args: str, payload: dict | None = None) -> object:
    cmd = ['gh', 'api', *args]
    if payload is not None:
        cmd += ['--input', '-']
    proc = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None,
                          capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"gh api {' '.join(args)} failed: {proc.stderr.strip()}")
    out = proc.stdout.strip()
    if not out:
        return None
    decoder = json.JSONDecoder()
    values = []
    while out:
        value, end = decoder.raw_decode(out)
        values.append(value)
        out = out[end:].lstrip()
    return values[0] if len(values) == 1 else values


def paged(path: str) -> list:
    data = gh('--paginate', path)
    if isinstance(data, list) and data and all(isinstance(x, list) for x in data):
        return [item for page in data for item in page]
    if not isinstance(data, list):
        raise RuntimeError('invalid paginated response')
    return data


def pr_state(repo: str, pr: int) -> dict:
    p = gh(f'repos/{repo}/pulls/{pr}')
    return {'head': p['head']['sha'], 'state': p['state'], 'merged': p.get('merged', False),
            'locked': p.get('locked', False)}


def validate(plan):
    if plan.get('event') not in {'COMMENT', 'REQUEST_CHANGES'}:
        raise ValueError('event is not allowed; approval is refused')
    if not isinstance(plan.get('repo'), str) or len(plan['repo'].split('/')) != 2:
        raise ValueError('repo must be owner/name')
    if type(plan.get('pr')) is not int or plan['pr'] < 1:
        raise ValueError('pr must be a positive integer')
    if not isinstance(plan.get('commit'), str) or not plan['commit']:
        raise ValueError('reviewed commit is required')
    if not isinstance(plan.get('opener'), str) or not plan['opener'].strip():
        raise ValueError('opener is required')
    if not isinstance(plan.get('comments'), list):
        raise ValueError('comments must be a list')
    keys = set()
    for c in plan['comments']:
        if not isinstance(c, dict) or not isinstance(c.get('path'), str) or not c['path']:
            raise ValueError('comment path is required')
        if Path(c['path']).is_absolute() or '..' in Path(c['path']).parts:
            raise ValueError('invalid repository-relative comment path')
        if type(c.get('line')) is not int or c['line'] < 1:
            raise ValueError('line must be a positive integer')
        if not isinstance(c.get('body'), str) or not c['body'].strip():
            raise ValueError('comment body is required')
        side = c.get('side', 'RIGHT')
        if side not in {'LEFT', 'RIGHT'}:
            raise ValueError('invalid comment side')
        if c.get('start_line') is not None:
            if type(c['start_line']) is not int or not 1 <= c['start_line'] <= c['line']:
                raise ValueError('invalid comment range')
            if c.get('start_side', side) != side:
                raise ValueError('mixed-side ranges are unsupported')
        elif 'start_side' in c:
            raise ValueError('start_side requires start_line')
        key = helpers.identity(helpers.comment_payload(c, plan['commit']))
        if key in keys:
            raise ValueError('duplicate comment in plan')
        keys.add(key)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plan')
    ap.add_argument('--yes', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--journal', help='defaults to <plan-stem>.journal.json; retain for resume')
    args = ap.parse_args()
    report = {'dry_run': not args.yes, 'opener': None, 'comments': [], 'stopped': None}

    def finish(code):
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"dry_run={report['dry_run']} stopped={report['stopped']}")
            if not args.yes and 'plan' in report:
                print(json.dumps(report['plan'], indent=2))
            print(f"opener: {report['opener']}")
            for c in report['comments']:
                print(f"comment {c['path']}:{c['line']}: {c['status']} {c.get('url', '')}")
        return code

    try:
        plan = json.loads(Path(args.plan).read_text())
        plan.setdefault('event', 'COMMENT')
        validate(plan)
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        report['stopped'] = str(exc)
        return finish(2)
    repo, pr, commit = plan['repo'], plan['pr'], plan['commit']
    prefix = f'repos/{repo}/pulls/{pr}'

    def guard():
        now = pr_state(repo, pr)
        if now['head'] != commit:
            raise RuntimeError('PR changed before this comment or review: head moved; re-review before writing')
        if now['state'] != 'open' or now['merged'] or now['locked']:
            raise RuntimeError('PR changed before this comment or review; requires open, unmerged, unlocked state')

    try:
        guard()
        actor = gh('user')['login']
        operations = [('reviews', {'commit_id': commit, 'event': plan['event'], 'body': plan['opener']}, None)]
        for c in plan['comments']:
            entry = {'path': c['path'], 'line': c['line'], 'status': 'pending'}
            report['comments'].append(entry)
            operations.append(('comments', helpers.comment_payload(c, commit), entry))

        def lookup(kind, payload):
            matcher = helpers.matches_review if kind == 'reviews' else helpers.matches_comment
            matches = [x for x in paged(prefix + '/' + kind) if matcher(x, payload, actor)]
            if len(matches) > 1:
                raise RuntimeError('multiple matching artifacts; inspect before continuing')
            return matches[0] if matches else None

        if not args.yes:
            report['plan'] = plan
            for kind, payload, entry in operations:
                found = lookup(kind, payload)
                if entry is None:
                    report['opener'] = 'already posted, skipped' if found else f"would submit {plan['event']}"
                else:
                    entry['status'] = 'already posted, skipped' if found else 'would post'
            return finish(0)

        journal_path = Path(args.journal) if args.journal else Path(args.plan).with_suffix('.journal.json')
        report['journal'] = str(journal_path)
        with helpers.Journal(journal_path, plan, actor) as journal:
            for kind, payload, entry in operations:
                guard()
                op = journal.operation(kind, payload)
                found = lookup(kind, payload)
                initially_found = found is not None
                if not found:
                    if op['status'] in {'verified', 'permanent_failure'}:
                        raise RuntimeError('verified artifact disappeared or permanent failure needs inspection')
                    if op['attempts'] >= 2:
                        raise RuntimeError('operation exhausted its two-attempt limit; inspect destination')
                    guard()
                    op['attempts'] += 1
                    journal.record(op, 'attempting')
                    try:
                        gh('-X', 'POST', prefix + '/' + kind, payload=payload)
                    except (RuntimeError, ValueError, OSError) as exc:
                        permanent = any(code in str(exc) for code in ('HTTP 400', 'HTTP 401', 'HTTP 403', 'HTTP 404', 'HTTP 422'))
                        journal.record(op, 'permanent_failure' if permanent else 'ambiguous', error=str(exc))
                    try:
                        found = lookup(kind, payload)
                    except (RuntimeError, ValueError, KeyError, TypeError) as exc:
                        journal.record(op, 'ambiguous', error='destination read unavailable: ' + str(exc))
                        raise RuntimeError('write outcome ambiguous; resume the same plan and journal after inspection') from exc
                    if not found:
                        journal.record(op, 'permanent_failure' if op['status'] == 'permanent_failure' else 'absent_observed')
                        raise RuntimeError('write not verified; stopped without retrying; inspect before resuming')
                journal.record(op, 'verified', remote_id=found.get('id'), url=found.get('html_url'))
                if entry is None:
                    report['opener'] = found.get('html_url') or 'already posted, skipped'
                else:
                    entry.update(status='already posted, skipped' if initially_found else 'posted and verified',
                                 id=found.get('id'), url=found.get('html_url'))
            for kind, payload, _ in operations:
                if not lookup(kind, payload):
                    raise RuntimeError('final verification failed; an intended artifact is missing')
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        report['stopped'] = str(exc)
        return finish(1)
    return finish(0)


if __name__ == '__main__':
    sys.exit(main())
