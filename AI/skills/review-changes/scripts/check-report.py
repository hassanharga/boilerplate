#!/usr/bin/env python3
"""Check a review report against the output contract before it is shown or posted.

Usage:
  check-report.py <report.md | -> [--snapshot DIR] [--base-snapshot DIR] [--diff diff.patch] [--publish]
                  [--max-design-suggestions N] [--json]

Checks:
  - exactly the six parts, in order: Summary, Review path, Findings, Conflict notes,
    AC coverage, Verdict, and no other level-2 heading;
  - every finding has a `path:line` title anchor and Type, Issue, Impact, Fix fields;
  - Type is one of the five allowed values, and findings are ordered by Type;
  - with --snapshot: each anchored file exists and the line is within the file;
  - with --diff: each anchor overlaps a changed line (an error with --publish, a
    warning otherwise, because chat-only findings may cite outside-diff lines);
  - at most N Suggestions (default 3) unless the user asked for more.

Pass - to read the report from stdin.

Exit 0 when no errors, 1 when errors, 2 on usage problems. Standard library only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

PARTS = ["Summary", "Review path", "Findings", "Conflict notes", "AC coverage", "Verdict"]
TYPES = [
    "Issue - Blocking",
    "Issue - Non-blocking",
    "Question - Non-blocking",
    "Suggestion - Non-blocking",
    "Nitpick - Non-blocking",
]
ANCHOR = re.compile(
    r"^(?:#{3,6}\s*)?(?:\*\*)?(?:\d+[.)]\s*)?(?P<title>.+?):(?:\*\*)?\s*`?(?P<path>[^`\n]+?)"
    r":(?P<start>\d+)(?:-(?P<end>\d+))?`?(?:\*\*)?(?:\s+\[(?P<side>LEFT|RIGHT)\])?\s*$"
)
FIELD = re.compile(r"^(?:\*\*)?(Type|Issue|Impact|Fix):(?:\*\*)?\s*(?P<value>.*)$")


def strip_md(text: str) -> str:
    return text.replace("**", "").replace("`", "").strip()


def split_parts(lines: list[str]) -> tuple[list[tuple[str, int]], dict[str, list[str]]]:
    headings: list[tuple[str, int]] = []
    sections: dict[str, list[str]] = {}
    current = None
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith("## "):
            current = line[3:].strip()
            headings.append((current, i))
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return headings, sections


def parse_findings(body: list[str]) -> list[dict]:
    findings: list[dict] = []
    current = None
    in_code = False
    for line in body:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = ANCHOR.match(stripped)
        if m and not FIELD.match(stripped):
            current = {
                "title": strip_md(m.group("title")),
                "path": m.group("path"),
                "side": m.group("side") or "RIGHT",
                "start": int(m.group("start")),
                "end": int(m.group("end") or m.group("start")),
                "fields": {},
            }
            findings.append(current)
            continue
        f = FIELD.match(stripped)
        if f and current is not None:
            current["fields"].setdefault(f.group(1), strip_md(f.group("value")))
        elif f and current is None:
            findings.append({"title": None, "path": None, "side": "RIGHT", "start": 0, "end": 0,
                             "fields": {f.group(1): strip_md(f.group("value"))}})
            current = findings[-1]
    return findings


spec = importlib.util.spec_from_file_location("diff_anchors", Path(__file__).with_name("diff-anchors.py"))
anchors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(anchors)
changed_lines = anchors.changed_lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--snapshot")
    ap.add_argument("--base-snapshot", help="old-side snapshot; required for LEFT findings")
    ap.add_argument("--diff")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--max-design-suggestions", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.report == "-":
        lines = sys.stdin.read().splitlines()
    else:
        report = Path(args.report)
        if not report.is_file():
            print(f"report not found: {report}", file=sys.stderr)
            return 2
        lines = report.read_text(errors="replace").splitlines()
    errors: list[str] = []
    warnings: list[str] = []

    headings, sections = split_parts(lines)
    names = [h for h, _ in headings]
    extra = [h for h in names if h not in PARTS]
    if extra:
        errors.append(f"extra level-2 headings: {extra}")
    present = [h for h in names if h in PARTS]
    if present != PARTS:
        errors.append(f"parts must be exactly {PARTS} in order; found {names}")

    findings = parse_findings(sections.get("Findings", []))
    findings_text = "\n".join(sections.get("Findings", [])).strip()
    if not findings and findings_text and not re.search(r"no findings", findings_text, re.I):
        errors.append("Findings has content but no finding with a `path:line` title was recognized")

    changed = changed_lines(Path(args.diff)) if args.diff else None
    snapshot = Path(args.snapshot) if args.snapshot else None
    base_snapshot = Path(args.base_snapshot) if args.base_snapshot else None
    if args.publish and (not args.snapshot or not args.diff):
        errors.append("--publish requires --snapshot and --diff")
    order = []
    for n, f in enumerate(findings, 1):
        label = f"finding {n} ({f['title'] or 'untitled'})"
        if f["path"] is None:
            errors.append(f"{label}: missing `path:line` title line")
        for field in ("Type", "Issue", "Impact", "Fix"):
            if not f["fields"].get(field):
                errors.append(f"{label}: missing {field}:")
        t = f["fields"].get("Type")
        if t and t not in TYPES:
            errors.append(f"{label}: Type '{t}' is not one of {TYPES}")
        elif t:
            order.append(TYPES.index(t))
        source = base_snapshot if f["side"] == "LEFT" else snapshot
        if f["side"] == "LEFT" and source is None:
            errors.append(f"{label}: LEFT anchor requires --base-snapshot")
        if f["start"] > f["end"]:
            errors.append(f"{label}: reversed line range")
        if f["path"] and source:
            file = source / f["path"]
            if not file.resolve().is_relative_to(source.resolve()) or file.is_symlink():
                errors.append(f"{label}: anchor escapes the snapshot or targets a symlink")
                continue
            if not file.is_file():
                errors.append(f"{label}: {f['path']} does not exist in the snapshot")
            else:
                count = len(file.read_text(errors="replace").splitlines())
                if f["end"] > count or f["start"] < 1:
                    errors.append(f"{label}: line {f['start']}-{f['end']} outside {f['path']} ({count} lines)")
        if f["path"] and changed is not None:
            lines_changed = changed.get((f["side"], f["path"]), set())
            if not any(l in lines_changed for l in range(f["start"], f["end"] + 1)):
                msg = f"{label}: {f['path']}:{f['start']} is not on a changed line"
                (errors if args.publish else warnings).append(msg)
    if order != sorted(order):
        errors.append("findings are not ordered by Type (blocking, non-blocking, question, suggestion, nitpick)")
    suggestions = sum(1 for f in findings if f["fields"].get("Type") == "Suggestion - Non-blocking")
    if suggestions > args.max_design_suggestions:
        errors.append(f"{suggestions} Suggestions exceed the cap of {args.max_design_suggestions}")

    result = {"ok": not errors, "findings": len(findings), "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("OK" if not errors else "FAIL", f"- {len(findings)} findings")
        for e in errors:
            print(f"  error: {e}")
        for w in warnings:
            print(f"  warning: {w}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
