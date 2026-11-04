from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "contrast.py"
SPEC = importlib.util.spec_from_file_location("contrast", SCRIPT)
assert SPEC and SPEC.loader
contrast = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contrast)


class ContrastTests(unittest.TestCase):
    def capture(self, function, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = function(*args)
        return result, stdout.getvalue(), stderr.getvalue()

    def pair_file(self, data) -> str:
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        with handle:
            json.dump(data, handle)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return handle.name

    def test_parse_hex_and_format(self):
        self.assertEqual(contrast.parse_hex("#abc"), (170, 187, 204))
        self.assertEqual(contrast.parse_hex(" #00Ff7f "), (0, 255, 127))
        self.assertEqual(contrast.to_hex((-2.0, 127.6, 300.0)), "#0080FF")

        for value in (None, "ffffff", "#12", "#12345678", "#GGGGGG"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                contrast.parse_hex(value)
        with self.assertRaises(ValueError):
            contrast.to_hex((1, 2))

    def test_luminance_contrast_and_verdicts(self):
        self.assertEqual(contrast.luminance((0, 0, 0)), 0.0)
        self.assertAlmostEqual(contrast.contrast((0, 0, 0), (255, 255, 255)), 21.0)
        self.assertAlmostEqual(
            contrast.contrast((255, 255, 255), (0, 0, 0)), 21.0
        )
        with self.assertRaises(ValueError):
            contrast.luminance((1, 2))

        self.assertEqual(contrast.verdict(2.9, "ui"), "FAIL")
        self.assertEqual(contrast.verdict(3.1, "ui"), "AA")
        self.assertEqual(contrast.verdict(4.6, "body"), "AA")
        self.assertEqual(contrast.verdict(7.1, "body"), "AAA")
        with self.assertRaises(ValueError):
            contrast.threshold("unknown")

    def test_oklab_round_trip_and_gamut_mapping(self):
        source = (43, 92, 230)
        lab = contrast.rgb_to_oklab(source)
        rebuilt = contrast.oklab_to_rgb(lab)
        for actual, expected in zip(rebuilt, source):
            self.assertAlmostEqual(actual, expected, delta=0.01)

        lightness, chroma, hue = contrast.rgb_to_oklch(source)
        in_gamut = contrast.oklch_to_rgb(lightness, chroma, hue)
        out_of_gamut = contrast.oklch_to_rgb(0.95, 0.5, hue)
        self.assertEqual(len(in_gamut), 3)
        self.assertTrue(all(0 <= channel <= 255 for channel in out_of_gamut))
        self.assertLess(contrast._cbrt(-8), 0)

    def test_target_and_step_validation(self):
        contrast.validate_target(1)
        contrast.validate_target(21)
        for target in (0.99, 21.01):
            with self.subTest(target=target), self.assertRaises(ValueError):
                contrast.validate_target(target)

        self.assertEqual(contrast.parse_steps("900, 100, 500,500"), [100, 500, 900])
        for steps in ("", "100", "-1,100", "one,two"):
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                contrast.parse_steps(steps)

    def test_pair_command(self):
        args = argparse.Namespace(fg="#000", bg="#fff")
        result, output, error = self.capture(contrast.cmd_pair, args)
        self.assertEqual(result, 0)
        self.assertIn("21.00:1", output)
        self.assertIn("ui     AA 3.0:1  PASS", output)
        self.assertNotIn("ui     AA 3.0:1  PASS   AAA", output)
        self.assertEqual(error, "")

    def test_load_pairs_accepts_supported_shapes(self):
        pair = {"name": "body", "fg": "#000", "bg": "#fff", "kind": "body"}
        list_path = self.pair_file([pair])
        dict_path = self.pair_file({"pairs": [pair]})
        self.assertEqual(contrast._load_pairs(list_path), [pair])
        self.assertEqual(contrast._load_pairs(dict_path), [pair])

    def test_load_pairs_rejects_bad_schema(self):
        bad_values = (
            {"wrong": []},
            ["not an object"],
            [{"fg": "#000"}],
            [{"fg": "#000", "bg": "#fff", "kind": "unknown"}],
        )
        for data in bad_values:
            path = self.pair_file(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                contrast._load_pairs(path)

    def test_check_command_pass_and_fail(self):
        path = self.pair_file(
            [
                {"name": "pass", "fg": "#000", "bg": "#fff", "kind": "body"},
                {"name": "fail", "fg": "#777", "bg": "#fff", "kind": "body"},
            ]
        )
        result, output, _ = self.capture(
            contrast.cmd_check, argparse.Namespace(file=path)
        )
        self.assertEqual(result, 1)
        self.assertIn("2 pairs, 1 failing", output)

        empty_path = self.pair_file([])
        result, output, _ = self.capture(
            contrast.cmd_check, argparse.Namespace(file=empty_path)
        )
        self.assertEqual(result, 0)
        self.assertIn("0 pairs, 0 failing", output)

    def test_find_and_fix_foreground(self):
        already = contrast.find_compliant_foreground(
            (0, 0, 0), (255, 255, 255), 4.5
        )
        self.assertIsNotNone(already)
        adjusted = contrast.find_compliant_foreground(
            (119, 119, 119), (255, 255, 255), 4.5
        )
        self.assertIsNotNone(adjusted)
        assert adjusted
        self.assertGreaterEqual(adjusted[1], 4.5)
        impossible = contrast.find_compliant_foreground(
            (119, 119, 119), (119, 119, 119), 7
        )
        self.assertIsNone(impossible)

        args = argparse.Namespace(fg="#000", bg="#fff", target=4.5)
        result, output, _ = self.capture(contrast.cmd_fix, args)
        self.assertEqual(result, 0)
        self.assertIn("already meets", output)

        args = argparse.Namespace(fg="#777", bg="#fff", target=4.5)
        result, output, _ = self.capture(contrast.cmd_fix, args)
        self.assertEqual(result, 0)
        self.assertIn("->", output)

        args = argparse.Namespace(fg="#777", bg="#777", target=7)
        result, output, _ = self.capture(contrast.cmd_fix, args)
        self.assertEqual(result, 1)
        self.assertIn("cannot reach", output)

    def test_ramp_command_and_bounds(self):
        args = argparse.Namespace(
            base="#2B5CE6", steps="100,500,900", min_l=0.2, max_l=0.97
        )
        result, output, _ = self.capture(contrast.cmd_ramp, args)
        self.assertEqual(result, 0)
        self.assertIn("base #2B5CE6", output)
        self.assertIn("gamut boundary", output)

        args.min_l = 1
        with self.assertRaises(ValueError):
            contrast.cmd_ramp(args)

    def test_main_success_and_handled_errors(self):
        result, output, error = self.capture(
            contrast.main, ["pair", "#000", "#fff"]
        )
        self.assertEqual(result, 0)
        self.assertIn("21.00:1", output)
        self.assertEqual(error, "")

        result, _, error = self.capture(
            contrast.main, ["pair", "#00000000", "#fff"]
        )
        self.assertEqual(result, 2)
        self.assertIn("composite alpha first", error)

        result, _, error = self.capture(
            contrast.main, ["check", "/path/that/does/not/exist.json"]
        )
        self.assertEqual(result, 2)
        self.assertIn("error:", error)

        bad_json = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        )
        with bad_json:
            bad_json.write("{")
        self.addCleanup(Path(bad_json.name).unlink, missing_ok=True)
        result, _, error = self.capture(contrast.main, ["check", bad_json.name])
        self.assertEqual(result, 2)
        self.assertIn("error:", error)

    def test_parser_requires_command(self):
        parser = contrast.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args([])

    def test_module_entry_point(self):
        original = sys.argv
        try:
            sys.argv = [str(SCRIPT), "pair", "#000", "#fff"]
            with self.assertRaises(SystemExit) as raised:
                with contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(SCRIPT), run_name="__main__")
            self.assertEqual(raised.exception.code, 0)
        finally:
            sys.argv = original


if __name__ == "__main__":
    unittest.main()
