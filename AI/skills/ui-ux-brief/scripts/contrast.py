#!/usr/bin/env python3
"""WCAG 2.x contrast checks and opaque sRGB color utilities.

Supported colors are #RGB and #RRGGBB. Composite alpha colors against their
rendered background before using this tool.

Examples:
  contrast.py pair "#0B1E2D" "#F7F5F2"
  contrast.py check pairs.json
  contrast.py fix "#7C9CBF" "#FFFFFF" --target 4.5
  contrast.py ramp "#2B5CE6" --steps 100,300,500,700,900

pairs.json:
  {"pairs": [{"name": "body on surface", "fg": "#1A1A1A",
              "bg": "#FFFFFF", "kind": "body"}]}

Kinds: body, large, or ui.
"""

from __future__ import annotations

import argparse
import json
import sys
from math import atan2, copysign, cos, hypot, sin
from pathlib import Path
from typing import Iterable, Sequence

RGB = tuple[int, int, int]
FloatRGB = tuple[float, float, float]


def parse_hex(value: str) -> RGB:
    if not isinstance(value, str):
        raise ValueError("color must be a string")
    raw = value.strip()
    if not raw.startswith("#"):
        raise ValueError(f"color must start with #: {value!r}")
    digits = raw[1:]
    if len(digits) == 3:
        digits = "".join(character * 2 for character in digits)
    elif len(digits) != 6:
        raise ValueError(
            f"expected #RGB or #RRGGBB, got {value!r}; composite alpha first"
        )
    try:
        return tuple(int(digits[index:index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise ValueError(f"invalid hexadecimal color: {value!r}") from exc


def to_hex(rgb: Iterable[float]) -> str:
    channels = tuple(rgb)
    if len(channels) != 3:
        raise ValueError("RGB color must contain three channels")
    return "#" + "".join(
        f"{max(0, min(255, round(channel))):02X}" for channel in channels
    )


def _linear(channel: float) -> float:
    value = channel / 255
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def luminance(rgb: Iterable[float]) -> float:
    channels = tuple(rgb)
    if len(channels) != 3:
        raise ValueError("RGB color must contain three channels")
    red, green, blue = (_linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(foreground: Iterable[float], background: Iterable[float]) -> float:
    first = luminance(foreground)
    second = luminance(background)
    high, low = max(first, second), min(first, second)
    return (high + 0.05) / (low + 0.05)


THRESHOLDS: dict[str, tuple[float, float | None]] = {
    "body": (4.5, 7.0),
    "large": (3.0, 4.5),
    "ui": (3.0, None),
}


def threshold(kind: str) -> tuple[float, float | None]:
    try:
        return THRESHOLDS[kind]
    except KeyError as exc:
        choices = ", ".join(THRESHOLDS)
        raise ValueError(f"unknown kind {kind!r}; expected one of: {choices}") from exc


def verdict(ratio: float, kind: str = "body") -> str:
    aa, aaa = threshold(kind)
    if ratio < aa:
        return "FAIL"
    if aaa is not None and ratio >= aaa:
        return "AAA"
    return "AA"


def _srgb_to_linear(channel: float) -> float:
    value = channel / 255
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(channel: float) -> float:
    if channel <= 0.0031308:
        value = 12.92 * channel
    else:
        value = 1.055 * (channel ** (1 / 2.4)) - 0.055
    return max(0.0, min(1.0, value)) * 255


def _cbrt(value: float) -> float:
    return copysign(abs(value) ** (1 / 3), value)


def rgb_to_oklab(rgb: Iterable[float]) -> tuple[float, float, float]:
    red, green, blue = (_srgb_to_linear(channel) for channel in rgb)
    light = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    medium = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    short = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    light_root, medium_root, short_root = (
        _cbrt(light),
        _cbrt(medium),
        _cbrt(short),
    )
    return (
        0.2104542553 * light_root
        + 0.7936177850 * medium_root
        - 0.0040720468 * short_root,
        1.9779984951 * light_root
        - 2.4285922050 * medium_root
        + 0.4505937099 * short_root,
        0.0259040371 * light_root
        + 0.7827717662 * medium_root
        - 0.8086757660 * short_root,
    )


def oklab_to_linear(lab: Sequence[float]) -> tuple[float, float, float]:
    lightness, green_red, blue_yellow = lab
    light_root = (
        lightness + 0.3963377774 * green_red + 0.2158037573 * blue_yellow
    )
    medium_root = (
        lightness - 0.1055613458 * green_red - 0.0638541728 * blue_yellow
    )
    short_root = (
        lightness - 0.0894841775 * green_red - 1.2914855480 * blue_yellow
    )
    light, medium, short = light_root ** 3, medium_root ** 3, short_root ** 3
    return (
        4.0767416621 * light - 3.3077115913 * medium + 0.2309699292 * short,
        -1.2684380046 * light + 2.6097574011 * medium - 0.3413193965 * short,
        -0.0041960863 * light - 0.7034186147 * medium + 1.7076147010 * short,
    )


def oklab_to_rgb(lab: Sequence[float]) -> FloatRGB:
    return tuple(_linear_to_srgb(channel) for channel in oklab_to_linear(lab))


def rgb_to_oklch(rgb: Iterable[float]) -> tuple[float, float, float]:
    lightness, green_red, blue_yellow = rgb_to_oklab(rgb)
    return lightness, hypot(green_red, blue_yellow), atan2(blue_yellow, green_red)


def oklch_to_rgb(lightness: float, chroma: float, hue: float) -> FloatRGB:
    def lab_for(candidate_chroma: float) -> tuple[float, float, float]:
        return (
            lightness,
            candidate_chroma * cos(hue),
            candidate_chroma * sin(hue),
        )

    lab = lab_for(chroma)
    if all(-1e-4 <= channel <= 1 + 1e-4 for channel in oklab_to_linear(lab)):
        return oklab_to_rgb(lab)

    low, high = 0.0, chroma
    for _ in range(24):
        candidate = (low + high) / 2
        if all(
            -1e-4 <= channel <= 1 + 1e-4
            for channel in oklab_to_linear(lab_for(candidate))
        ):
            low = candidate
        else:
            high = candidate
    return oklab_to_rgb(lab_for(low))


def validate_target(target: float) -> None:
    if not 1.0 <= target <= 21.0:
        raise ValueError("target contrast must be between 1 and 21")


def parse_steps(value: str) -> list[int]:
    try:
        steps = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    except ValueError as exc:
        raise ValueError("steps must be comma-separated integers") from exc
    if len(steps) < 2 or any(step < 0 for step in steps):
        raise ValueError("provide at least two distinct non-negative steps")
    return steps


def cmd_pair(args: argparse.Namespace) -> int:
    foreground, background = parse_hex(args.fg), parse_hex(args.bg)
    ratio = contrast(foreground, background)
    print(f"{to_hex(foreground)} on {to_hex(background)}  ->  {ratio:.2f}:1")
    for kind, (aa, aaa) in THRESHOLDS.items():
        result = "PASS" if ratio >= aa else "FAIL"
        suffix = ""
        if aaa is not None:
            aaa_result = "PASS" if ratio >= aaa else "FAIL"
            suffix = f"   AAA {aaa}:1  {aaa_result}"
        print(f"  {kind:<6} AA {aa}:1  {result}{suffix}")
    return 0


def _load_pairs(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    pairs = data.get("pairs") if isinstance(data, dict) else data
    if not isinstance(pairs, list):
        raise ValueError("pair file must be a list or an object with a pairs list")
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            raise ValueError(f"pair {index} must be an object")
        for field in ("fg", "bg"):
            if field not in pair:
                raise ValueError(f"pair {index} is missing {field!r}")
        threshold(str(pair.get("kind", "body")))
    return pairs


def cmd_check(args: argparse.Namespace) -> int:
    pairs = _load_pairs(args.file)
    width = max((len(str(pair.get("name", ""))) for pair in pairs), default=4)
    failures = 0
    print(f"{'pair'.ljust(width)}  {'fg':<8} {'bg':<8} {'ratio':>7}  {'need':>5}  result")
    print("-" * (width + 40))
    for pair in pairs:
        foreground = parse_hex(str(pair["fg"]))
        background = parse_hex(str(pair["bg"]))
        kind = str(pair.get("kind", "body"))
        ratio = contrast(foreground, background)
        need = threshold(kind)[0]
        result = verdict(ratio, kind)
        failures += result == "FAIL"
        print(
            f"{str(pair.get('name', '')).ljust(width)}  "
            f"{to_hex(foreground):<8} {to_hex(background):<8} "
            f"{ratio:>6.2f}:1  {need:>5}  {result}"
        )
    print(f"\n{len(pairs)} pairs, {failures} failing")
    return 1 if failures else 0


def _candidate_at(lightness, green_red, blue_yellow, damp) -> FloatRGB:
    return oklab_to_rgb(
        (lightness, green_red * damp, blue_yellow * damp)
    )


def find_compliant_foreground(foreground: RGB, background: RGB, target: float):
    validate_target(target)
    start = contrast(foreground, background)
    if start >= target:
        return tuple(float(channel) for channel in foreground), start

    lightness, green_red, blue_yellow = rgb_to_oklab(foreground)
    background_lightness = rgb_to_oklab(background)[0]
    direction = -1.0 if background_lightness > 0.5 else 1.0

    for damp in (1.0, 0.75, 0.5, 0.25, 0.0):
        for index in range(1, 501):
            candidate_lightness = lightness + direction * 0.002 * index
            if not 0.0 <= candidate_lightness <= 1.0:
                break
            candidate = _candidate_at(
                candidate_lightness, green_red, blue_yellow, damp
            )
            ratio = contrast(candidate, background)
            if ratio >= target:
                return candidate, ratio
    return None


def cmd_fix(args: argparse.Namespace) -> int:
    foreground, background = parse_hex(args.fg), parse_hex(args.bg)
    validate_target(args.target)
    start = contrast(foreground, background)
    result = find_compliant_foreground(foreground, background, args.target)
    if result is None:
        print(
            f"cannot reach {args.target}:1 against {to_hex(background)}; "
            "change the foreground or background"
        )
        return 1
    candidate, ratio = result
    if start >= args.target:
        print(
            f"{to_hex(foreground)} already meets {args.target}:1 on "
            f"{to_hex(background)} ({start:.2f}:1)"
        )
        return 0
    print(
        f"{to_hex(foreground)} ({start:.2f}:1)  ->  "
        f"{to_hex(candidate)} ({ratio:.2f}:1) on {to_hex(background)}"
    )
    return 0


def cmd_ramp(args: argparse.Namespace) -> int:
    base = parse_hex(args.base)
    steps = parse_steps(args.steps)
    if not 0.0 <= args.min_l < args.max_l <= 1.0:
        raise ValueError("ramp lightness must satisfy 0 <= min-l < max-l <= 1")

    base_lightness, base_chroma, hue = rgb_to_oklch(base)
    print(f"{'step':>5}  {'hex':<8}  {'L':>5}  {'C':>5}   contrast vs white / black")
    span = steps[-1] - steps[0]
    for step in steps:
        position = (step - steps[0]) / span
        lightness = args.max_l - position * (args.max_l - args.min_l)
        rgb = oklch_to_rgb(lightness, base_chroma, hue)
        actual_chroma = rgb_to_oklch(rgb)[1]
        on_white = contrast(rgb, (255, 255, 255))
        on_black = contrast(rgb, (0, 0, 0))
        print(
            f"{step:>5}  {to_hex(rgb):<8}  {lightness:>5.3f}  "
            f"{actual_chroma:>5.3f}   {on_white:>5.2f}:1 / {on_black:>5.2f}:1"
        )
    print(
        f"\nbase {to_hex(base)}  L {base_lightness:.3f}  "
        f"C {base_chroma:.3f}  hue {hue * 57.2958:.1f}deg"
    )
    print("Chroma is reduced at the sRGB gamut boundary; hue is preserved.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    pair = subcommands.add_parser("pair", help="check one foreground/background pair")
    pair.add_argument("fg")
    pair.add_argument("bg")
    pair.set_defaults(func=cmd_pair)

    check = subcommands.add_parser("check", help="check pairs in a JSON file")
    check.add_argument("file")
    check.set_defaults(func=cmd_check)

    fix = subcommands.add_parser("fix", help="adjust an opaque foreground")
    fix.add_argument("fg")
    fix.add_argument("bg")
    fix.add_argument("--target", type=float, default=4.5)
    fix.set_defaults(func=cmd_fix)

    ramp = subcommands.add_parser("ramp", help="generate an OKLCH lightness ramp")
    ramp.add_argument("base")
    ramp.add_argument("--steps", default="50,100,200,300,400,500,600,700,800,900,950")
    ramp.add_argument("--min-l", type=float, default=0.20, dest="min_l")
    ramp.add_argument("--max-l", type=float, default=0.97, dest="max_l")
    ramp.set_defaults(func=cmd_ramp)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
