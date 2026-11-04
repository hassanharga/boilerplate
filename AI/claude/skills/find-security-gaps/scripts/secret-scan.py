#!/usr/bin/env python3
"""Locate credential candidates without ever emitting their value.

The hardest rule in this skill is that a possible secret must never reach terminal
output, chat, a report, or command history. Prose cannot enforce that; this can.
Every code path here reports only four safe fields:

    repository-relative path, line number, detector rule, redacted fingerprint

The fingerprint is a truncated SHA-256 of the matched value. It is stable, so the same
credential is recognisable across runs and files, and it is not reversible, so it is
safe to paste into a report.

Prefers an already-installed Gitleaks (invoked with redaction forced on) and falls back
to built-in detectors. It never installs anything and never contacts a provider to check
whether a credential is live.

Usage:
    secret-scan.py [PATH] [--json] [--no-gitleaks] [--include-placeholders]

Exit status: 1 when at least one credible candidate is found, 0 when none, 2 on error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "coverage",
    ".next", ".nuxt", ".output", ".cache", ".turbo", ".venv", "venv",
    "__pycache__", "vendor", ".terraform", ".gradle",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".zip",
    ".gz", ".tar", ".bz2", ".xz", ".7z", ".mp4", ".mov", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".otf", ".eot", ".class", ".jar", ".so",
    ".dylib", ".dll", ".exe", ".bin", ".wasm", ".pyc",
}
MAX_BYTES = 2_000_000

DETECTORS: list[tuple[str, re.Pattern[str], int]] = [
    ("private-key", re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"), 0),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), 0),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), 0),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b"), 0),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), 0),
    ("jwt", re.compile(
        r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), 0),
    ("url-embedded-credentials", re.compile(
        r"\b[a-z][a-z0-9+.\-]*://[^/\s:@]+:([^/\s:@]{3,})@"), 1),
    ("secret-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|credential|private[_-]?key)"
        r"\b\s*[:=]\s*[\"']([^\"'\n]{8,})[\"']"), 1),
]

PLACEHOLDER_HINTS = re.compile(
    r"(?i)(example|sample|dummy|placeholder|changeme|change[_-]me|your[_-]?|"
    r"redacted|xxxx+|\*\*\*\*|fake|test[_-]?(?:key|token|secret)|<[^>]+>|"
    r"\$\{[^}]+\}|\{\{[^}]+\}\}|^process\.env|^os\.environ)"
)


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def looks_like_placeholder(value: str) -> bool:
    if PLACEHOLDER_HINTS.search(value):
        return True
    stripped = value.strip()
    if len(set(stripped)) <= 2:
        return True
    return False


def should_skip(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    try:
        if path.stat().st_size > MAX_BYTES:
            return True
    except OSError:
        return True
    return False


def walk(root: Path):
    if root.is_file():
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            candidate = Path(dirpath) / name
            if not should_skip(candidate):
                yield candidate


def scan_text(text: str, rel: str) -> list[dict]:
    found: list[dict] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if len(line) > 4000:
            line = line[:4000]
        for rule, pattern, group in DETECTORS:
            for match in pattern.finditer(line):
                value = match.group(group) if group else match.group(0)
                if not value:
                    continue
                found.append({
                    "path": rel,
                    "line": line_no,
                    "rule": rule,
                    "fingerprint": fingerprint(value),
                    "status": "likely-placeholder"
                    if looks_like_placeholder(value) else "candidate",
                })
    return found


def scan_builtin(root: Path) -> list[dict]:
    results: list[dict] = []
    base = root if root.is_dir() else root.parent
    for path in walk(root):
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        try:
            rel = str(path.relative_to(base))
        except ValueError:
            rel = str(path)
        results.extend(scan_text(text, rel))
    return results


def scan_gitleaks(root: Path) -> list[dict] | None:
    """Run an already-installed Gitleaks with redaction forced on."""
    binary = shutil.which("gitleaks")
    if binary is None:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        command = [
            binary, "detect", "--no-banner", "--redact",
            "--source", str(root),
            "--report-format", "json", "--report-path", str(report),
        ]
        try:
            subprocess.run(command, capture_output=True, timeout=300, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if not report.exists():
            return None
        try:
            raw = json.loads(report.read_text(encoding="utf-8") or "[]")
        except (json.JSONDecodeError, OSError):
            return None

    results: list[dict] = []
    for item in raw if isinstance(raw, list) else []:
        # Gitleaks with --redact already masks Secret; never echo it regardless.
        identity = str(item.get("Fingerprint") or item.get("RuleID", ""))
        results.append({
            "path": str(item.get("File", "")),
            "line": int(item.get("StartLine", 0) or 0),
            "rule": str(item.get("RuleID", "unknown")),
            "fingerprint": fingerprint(identity),
            "status": "candidate",
        })
    return results


def report(results: list[dict], as_json: bool, show_placeholders: bool) -> int:
    shown = [r for r in results
             if show_placeholders or r["status"] == "candidate"]
    credible = [r for r in results if r["status"] == "candidate"]
    suppressed = len(results) - len(shown)

    if as_json:
        print(json.dumps({
            "candidates": shown,
            "credible_count": len(credible),
            "suppressed_placeholders": suppressed,
            "note": "values are never included; fingerprint is a truncated SHA-256",
        }, indent=2))
        return 1 if credible else 0

    if not shown:
        print("No credential candidates found in the scanned scope.")
        if suppressed:
            print(f"({suppressed} likely placeholder(s) suppressed; "
                  f"use --include-placeholders to list them.)")
        print("A clean scan bounds what was searched. It is not proof of absence.")
        return 0

    width = max(len(f"{r['path']}:{r['line']}") for r in shown)
    width = max(width, 8)
    print(f"{'location'.ljust(width)}  {'rule':<26} {'fingerprint':<14} status")
    print("-" * (width + 55))
    for item in sorted(shown, key=lambda r: (r["path"], r["line"])):
        location = f"{item['path']}:{item['line']}"
        print(f"{location.ljust(width)}  {item['rule']:<26} "
              f"{item['fingerprint']:<14} {item['status']}")

    print(f"\n{len(credible)} credible candidate(s), "
          f"{len(shown) - len(credible)} likely placeholder(s) shown.")
    if suppressed:
        print(f"{suppressed} likely placeholder(s) suppressed.")
    print("\nValues were never read into this output. Before reporting one as exposed,")
    print("confirm it is a live credential from configuration and ownership evidence —")
    print("never by using it. A confirmed exposure needs rotation plus history review;")
    print("deleting the current line is not remediation.")
    return 1 if credible else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--no-gitleaks", action="store_true")
    parser.add_argument("--include-placeholders", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    results = None if args.no_gitleaks else scan_gitleaks(root)
    if results is None:
        results = scan_builtin(root)

    return report(results, args.as_json, args.include_placeholders)


if __name__ == "__main__":
    sys.exit(main())
