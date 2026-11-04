#!/usr/bin/env python3
"""Inventory the design tokens a project already has.

Scan-and-adopt is this skill's default, and it only works if adopting is cheaper than
inventing. Gathering the existing token set by hand is the expensive step, so this does
it: find the declarations, classify them by role, count who consumes each one, and emit
the adoption table the brief asks for.

Reads CSS custom properties, Tailwind theme configuration, and Style Dictionary or
`tokens.json` files. Usage counts come from `var(--token)` references across the tree,
so a token declared but never referenced shows a count of 0 — usually either dead or
consumed through a framework indirection worth checking.

Usage:
    extract-tokens.py [PATH] [--json] [--category color] [--unused]

Output is a Markdown table by default, ready to paste into the brief's adopted-tokens
section.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "coverage",
    ".next", ".nuxt", ".output", ".cache", ".turbo", ".venv", "venv",
    "__pycache__", "vendor", ".svelte-kit", ".astro",
}
STYLE_SUFFIXES = {".css", ".scss", ".sass", ".less", ".pcss", ".styl"}
MAX_BYTES = 2_000_000

CUSTOM_PROPERTY = re.compile(r"(?<![\w-])(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)")
VAR_REFERENCE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")
DARK_CONTEXT = re.compile(
    r"(?i)(prefers-color-scheme\s*:\s*dark|\[data-theme=[\"']?dark|\.dark\b|:root\.dark)"
)

COLOR_VALUE = re.compile(
    r"(?i)^\s*(#[0-9a-f]{3,8}\b|rgba?\(|hsla?\(|oklch\(|oklab\(|lab\(|lch\(|"
    r"color-mix\(|transparent\b|currentcolor\b)"
)

CATEGORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("radius", re.compile(r"(?i)(radius|rounded|corner)")),
    ("shadow", re.compile(r"(?i)(shadow|elevation)")),
    ("motion", re.compile(r"(?i)(duration|ease|easing|transition|animat|delay)")),
    ("typography", re.compile(
        r"(?i)(font|text-size|leading|line-height|tracking|letter-spacing|weight)")),
    ("spacing", re.compile(
        r"(?i)(space|spacing|gap|margin|padding|inset|gutter|size-\d|width|height)")),
    ("layer", re.compile(r"(?i)(z-index|zindex|layer|elevation-level)")),
    ("border", re.compile(r"(?i)(border|outline|stroke|divider)")),
    ("color", re.compile(
        r"(?i)(color|colour|bg|background|foreground|surface|text|accent|brand|"
        r"primary|secondary|success|warning|danger|error|info|muted|fill)")),
]


def classify(name: str, value: str) -> str:
    if COLOR_VALUE.match(value):
        for category, pattern in CATEGORY_RULES:
            if category in {"color", "border"}:
                continue
            if pattern.search(name):
                return category
        return "color"
    for category, pattern in CATEGORY_RULES:
        if pattern.search(name):
            return category
    return "other"


def walk(root: Path):
    if root.is_file():
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            try:
                if path.stat().st_size > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


def read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def collect_custom_properties(root: Path, base: Path) -> list[dict]:
    tokens: dict[tuple[str, str], dict] = {}
    for path in walk(root):
        if path.suffix.lower() not in STYLE_SUFFIXES:
            continue
        text = read(path)
        if text is None:
            continue
        dark_spans = [m.start() for m in DARK_CONTEXT.finditer(text)]
        for match in CUSTOM_PROPERTY.finditer(text):
            name = match.group(1)
            value = " ".join(match.group(2).split())
            if not value:
                continue
            line = text.count("\n", 0, match.start()) + 1
            # A declaration after a dark-context marker in the same file is very
            # likely the dark variant. Flag rather than assert.
            theme = "dark?" if any(s < match.start() for s in dark_spans) else "base"
            key = (name, value)
            if key in tokens:
                continue
            tokens[key] = {
                "token": name,
                "value": value,
                "category": classify(name, value),
                "source": f"{relative(path, base)}:{line}",
                "theme": theme,
                "origin": "css-custom-property",
            }
    return list(tokens.values())


def relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def flatten(prefix: str, node, out: dict[str, str]) -> None:
    if isinstance(node, dict):
        for key, child in node.items():
            label = key if key == "DEFAULT" else key
            nxt = prefix if key == "DEFAULT" else (
                f"{prefix}-{label}" if prefix else str(label))
            flatten(nxt, child, out)
    elif isinstance(node, (str, int, float)):
        if prefix:
            out[prefix] = str(node)


def collect_json_tokens(root: Path, base: Path) -> list[dict]:
    """Style Dictionary and tokens.json style files."""
    tokens: list[dict] = []
    for path in walk(root):
        if path.name not in {"tokens.json", "design-tokens.json"}:
            continue
        text = read(path)
        if text is None:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        flat: dict[str, str] = {}
        flatten("", data, flat)
        for name, value in flat.items():
            if name.endswith(("-type", "-description", "-comment")):
                continue
            tokens.append({
                "token": name,
                "value": value,
                "category": classify(name, value),
                "source": relative(path, base),
                "theme": "base",
                "origin": "tokens-json",
            })
    return tokens


TAILWIND_SECTIONS = (
    "colors", "spacing", "fontFamily", "fontSize", "borderRadius",
    "boxShadow", "screens", "zIndex", "transitionDuration",
)


def collect_tailwind(root: Path, base: Path) -> list[dict]:
    """Best-effort read of a Tailwind theme block.

    Tailwind configs are executable JavaScript, so this deliberately does not
    evaluate them. It extracts simple `key: 'value'` pairs inside recognised theme
    sections and reports the file so a human can confirm.
    """
    tokens: list[dict] = []
    pair = re.compile(r"[\"']?([A-Za-z0-9_][\w.-]*)[\"']?\s*:\s*[\"']([^\"']+)[\"']")
    for path in walk(root):
        if not re.match(r"^tailwind\.config\.(js|cjs|mjs|ts)$", path.name):
            continue
        text = read(path)
        if text is None:
            continue
        for section in TAILWIND_SECTIONS:
            start = text.find(f"{section}:")
            if start == -1:
                continue
            depth = 0
            end = start
            for index in range(start, len(text)):
                if text[index] == "{":
                    depth += 1
                elif text[index] == "}":
                    depth -= 1
                    if depth == 0:
                        end = index
                        break
            block = text[start:end] if end > start else text[start:start + 2000]
            for match in pair.finditer(block):
                name, value = match.group(1), match.group(2)
                if name == section:
                    continue
                tokens.append({
                    "token": f"{section}.{name}",
                    "value": value,
                    "category": classify(f"{section}-{name}", value),
                    "source": relative(path, base),
                    "theme": "base",
                    "origin": "tailwind-config",
                })
    return tokens


def count_usages(root: Path) -> Counter:
    counts: Counter = Counter()
    for path in walk(root):
        if path.suffix.lower() in {".png", ".jpg", ".woff", ".woff2", ".ttf"}:
            continue
        text = read(path)
        if text is None:
            continue
        for match in VAR_REFERENCE.finditer(text):
            counts[match.group(1)] += 1
    return counts


CATEGORY_ORDER = ["color", "typography", "spacing", "radius", "border",
                  "shadow", "motion", "layer", "other"]

DECLARATION = re.compile(r"(?<![\w-])([a-z-]+)\s*:\s*([^;{}]+)")
LITERAL_PROPERTIES = re.compile(
    r"(?i)^(color|background(-color)?|border(-color|-radius)?|box-shadow|fill|stroke|"
    r"padding(-\w+)?|margin(-\w+)?|gap|row-gap|column-gap|font-size|line-height|"
    r"font-family|letter-spacing|border-width|outline-color)$")
IGNORED_LITERALS = {
    "0", "0px", "none", "inherit", "initial", "unset", "auto", "transparent",
    "currentcolor", "1", "100%", "normal",
}


def collect_literals(root: Path, base: Path) -> list[dict]:
    """Find repeated hardcoded values in stylesheets.

    A project with no token file still has de-facto values. Surfacing the repeats
    gives the brief something concrete to adopt or correct, and it is the evidence
    for calling a value *observed* rather than *approved*.
    """
    seen: dict[tuple[str, str], dict] = {}
    for path in walk(root):
        if path.suffix.lower() not in STYLE_SUFFIXES:
            continue
        text = read(path)
        if text is None:
            continue
        for match in DECLARATION.finditer(text):
            prop, raw = match.group(1), " ".join(match.group(2).split())
            if not LITERAL_PROPERTIES.match(prop):
                continue
            if raw.lower() in IGNORED_LITERALS or "var(" in raw or "--" in raw:
                continue
            value = raw.lower()
            key = (prop, value)
            line = text.count("\n", 0, match.start()) + 1
            entry = seen.setdefault(key, {
                "property": prop,
                "value": raw,
                "category": classify(prop, raw),
                "count": 0,
                "locations": [],
            })
            entry["count"] += 1
            if len(entry["locations"]) < 5:
                entry["locations"].append(f"{relative(path, base)}:{line}")
    return [entry for entry in seen.values() if entry["count"] >= 2]


def emit_literals(literals: list[dict]) -> None:
    if not literals:
        return
    print("## Observed repeated values (no token declared)\n")
    print("These are hardcoded values appearing more than once. They are *observed*, "
          "not approved — an inconsistency repeated twice is not a design rule. "
          "Propose a semantic token only where the repetition reflects a real "
          "shared meaning.\n")
    print("| Property | Value | Times | Seen at |")
    print("| --- | --- | ---: | --- |")
    for row in sorted(literals, key=lambda r: (-r["count"], r["property"])):
        value = row["value"] if len(row["value"]) <= 34 else row["value"][:31] + "..."
        where = ", ".join(row["locations"][:3])
        if row["count"] > len(row["locations"][:3]):
            where += ", …"
        print(f"| `{row['property']}` | `{value}` | {row['count']} | {where} |")
    print()


def emit_markdown(tokens: list[dict], usages: Counter,
                  literals: list[dict] | None = None) -> None:
    if not tokens:
        print("No declared design tokens found in the scanned scope.\n")
        if literals:
            emit_literals(literals)
            print("There is no token system to adopt, but the values above are already "
                  "in use. Reconcile them before proposing anything new.")
        else:
            print("That is evidence there is no existing system to adopt — not "
                  "evidence that one should be invented. Confirm before proposing "
                  "new tokens.")
        return

    by_category: dict[str, list[dict]] = {}
    for token in tokens:
        by_category.setdefault(token["category"], []).append(token)

    print("# Existing token inventory\n")
    print(f"{len(tokens)} declarations across "
          f"{len({t['source'].split(':')[0] for t in tokens})} file(s).\n")

    for category in CATEGORY_ORDER:
        rows = by_category.get(category)
        if not rows:
            continue
        print(f"## {category}\n")
        print("| Token | Value | Source | Uses | Theme |")
        print("| --- | --- | --- | ---: | --- |")
        for row in sorted(rows, key=lambda r: r["token"]):
            uses = usages.get(row["token"], 0)
            uses_text = str(uses) if row["origin"] == "css-custom-property" else "—"
            value = row["value"] if len(row["value"]) <= 40 else row["value"][:37] + "..."
            print(f"| `{row['token']}` | `{value}` | {row['source']} | "
                  f"{uses_text} | {row['theme']} |")
        print()

    unused = [t for t in tokens
              if t["origin"] == "css-custom-property" and not usages.get(t["token"])]
    if unused:
        print(f"{len(unused)} custom propert(ies) have no `var()` reference in this "
              "tree. Check for framework indirection before treating them as dead.\n")

    dark = [t for t in tokens if t["theme"] == "dark?"]
    if dark:
        print(f"{len(dark)} declaration(s) follow a dark-theme marker in their file "
              "and are probably dark variants. Confirm against the source.\n")

    if literals:
        emit_literals(literals)

    print("Values are read from source, not from rendered screens. Verify contrast "
          "pairs with `contrast.py` — this script does not check them.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--category", help="show only one category")
    parser.add_argument("--unused", action="store_true",
                        help="show only tokens with no var() reference")
    parser.add_argument("--no-literals", action="store_true",
                        help="skip the repeated-hardcoded-value scan")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    base = root if root.is_dir() else root.parent
    tokens = (collect_custom_properties(root, base)
              + collect_json_tokens(root, base)
              + collect_tailwind(root, base))
    usages = count_usages(root)
    literals = [] if args.no_literals else collect_literals(root, base)

    if args.category:
        tokens = [t for t in tokens if t["category"] == args.category]
    if args.unused:
        tokens = [t for t in tokens
                  if t["origin"] == "css-custom-property"
                  and not usages.get(t["token"])]

    if args.as_json:
        print(json.dumps({
            "tokens": [dict(t, uses=usages.get(t["token"], 0)) for t in tokens],
            "count": len(tokens),
            "repeated_literals": literals,
        }, indent=2))
        return 0

    emit_markdown(tokens, usages, literals)
    return 0


if __name__ == "__main__":
    sys.exit(main())
