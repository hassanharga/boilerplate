from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "extract-tokens.py"
SPEC = importlib.util.spec_from_file_location("extract_tokens", SCRIPT)
assert SPEC and SPEC.loader
extract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extract)


def run(argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = extract.main(argv)
    return code, buffer.getvalue()


def write_tree(files: dict[str, str]) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    for name, content in files.items():
        path = Path(tmp.name) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp


class ClassifyTest(unittest.TestCase):
    def test_hex_value_is_color(self) -> None:
        self.assertEqual(extract.classify("--brand-500", "#2B5CE6"), "color")

    def test_oklch_value_is_color(self) -> None:
        self.assertEqual(extract.classify("--accent", "oklch(0.7 0.1 250)"), "color")

    def test_radius_beats_color_name(self) -> None:
        self.assertEqual(extract.classify("--radius-card", "8px"), "radius")

    def test_shadow(self) -> None:
        self.assertEqual(
            extract.classify("--shadow-md", "0 1px 2px rgba(0,0,0,.2)"), "shadow")

    def test_motion(self) -> None:
        self.assertEqual(extract.classify("--duration-fast", "120ms"), "motion")

    def test_typography(self) -> None:
        self.assertEqual(extract.classify("--font-body", "Inter, sans-serif"),
                         "typography")

    def test_spacing(self) -> None:
        self.assertEqual(extract.classify("--space-4", "16px"), "spacing")

    def test_unknown_is_other(self) -> None:
        self.assertEqual(extract.classify("--quux", "42"), "other")

    def test_shadow_name_wins_over_color_value(self) -> None:
        # A shadow whose value starts with a color must not be filed under color.
        self.assertEqual(extract.classify("--shadow-ring", "rgba(0,0,0,.4)"), "shadow")


class CustomPropertyTest(unittest.TestCase):
    def test_extracts_name_value_and_line(self) -> None:
        tree = write_tree({"a.css": ":root {\n  --brand: #2B5CE6;\n}\n"})
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_custom_properties(base, base)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0]["token"], "--brand")
        self.assertEqual(tokens[0]["value"], "#2B5CE6")
        self.assertTrue(tokens[0]["source"].endswith("a.css:2"))

    def test_ignores_var_references(self) -> None:
        tree = write_tree({"a.css": ".x { color: var(--brand); }\n"})
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_custom_properties(base, base)
        self.assertEqual(tokens, [])

    def test_flags_probable_dark_variant(self) -> None:
        css = (":root { --bg: #FFFFFF; }\n"
               "@media (prefers-color-scheme: dark) {\n"
               "  :root { --bg: #0B0B0B; }\n}\n")
        tree = write_tree({"a.css": css})
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_custom_properties(base, base)
        themes = {t["value"]: t["theme"] for t in tokens}
        self.assertEqual(themes["#FFFFFF"], "base")
        self.assertEqual(themes["#0B0B0B"], "dark?")

    def test_skips_node_modules(self) -> None:
        tree = write_tree({"node_modules/x/a.css": ":root{--a:#fff;}"})
        with tree:
            base = Path(tree.name)
            self.assertEqual(extract.collect_custom_properties(base, base), [])

    def test_deduplicates_identical_declarations(self) -> None:
        tree = write_tree({
            "a.css": ":root{--brand:#2B5CE6;}",
            "b.css": ":root{--brand:#2B5CE6;}",
        })
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_custom_properties(base, base)
        self.assertEqual(len(tokens), 1)


class UsageCountTest(unittest.TestCase):
    def test_counts_var_references(self) -> None:
        tree = write_tree({
            "a.css": ":root{--brand:#2B5CE6;}",
            "b.tsx": "const s={color:'var(--brand)'};\nconst t='var(--brand)';",
        })
        with tree:
            counts = extract.count_usages(Path(tree.name))
        self.assertEqual(counts["--brand"], 2)

    def test_unused_token_reported(self) -> None:
        tree = write_tree({"a.css": ":root{--ghost:#fff;}"})
        with tree:
            code, out = run([tree.name, "--unused"])
        self.assertEqual(code, 0)
        self.assertIn("--ghost", out)


class TokensJsonTest(unittest.TestCase):
    def test_flattens_nested_tokens(self) -> None:
        payload = {"color": {"brand": {"500": "#2B5CE6", "DEFAULT": "#1F49C0"}}}
        tree = write_tree({"tokens.json": json.dumps(payload)})
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_json_tokens(base, base)
        names = {t["token"] for t in tokens}
        self.assertIn("color-brand-500", names)
        self.assertIn("color-brand", names)


class TailwindTest(unittest.TestCase):
    def test_reads_simple_theme_pairs(self) -> None:
        config = (
            "module.exports = { theme: { extend: { colors: { "
            "brand: '#2B5CE6', muted: '#64748B' }, "
            "borderRadius: { card: '12px' } } } }\n"
        )
        tree = write_tree({"tailwind.config.js": config})
        with tree:
            base = Path(tree.name)
            tokens = extract.collect_tailwind(base, base)
        names = {t["token"] for t in tokens}
        self.assertIn("colors.brand", names)
        self.assertIn("borderRadius.card", names)

    def test_ignores_unrelated_js(self) -> None:
        tree = write_tree({"other.config.js": "module.exports={colors:{a:'#fff'}}"})
        with tree:
            base = Path(tree.name)
            self.assertEqual(extract.collect_tailwind(base, base), [])


class OutputTest(unittest.TestCase):
    def test_markdown_table_groups_by_category(self) -> None:
        tree = write_tree({
            "a.css": ":root{--brand:#2B5CE6;--space-2:8px;--radius-sm:4px;}",
            "b.tsx": "var(--brand)",
        })
        with tree:
            code, out = run([tree.name])
        self.assertEqual(code, 0)
        self.assertIn("## color", out)
        self.assertIn("## spacing", out)
        self.assertIn("## radius", out)
        self.assertIn("`--brand`", out)

    def test_category_filter(self) -> None:
        tree = write_tree({"a.css": ":root{--brand:#2B5CE6;--space-2:8px;}"})
        with tree:
            code, out = run([tree.name, "--category", "color"])
        self.assertEqual(code, 0)
        self.assertIn("--brand", out)
        self.assertNotIn("--space-2", out)

    def test_json_output_shape(self) -> None:
        tree = write_tree({"a.css": ":root{--brand:#2B5CE6;}", "b.tsx": "var(--brand)"})
        with tree:
            code, out = run([tree.name, "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["tokens"][0]["uses"], 1)

    def test_empty_tree_says_so_without_suggesting_invention(self) -> None:
        tree = write_tree({"readme.md": "# hi"})
        with tree:
            code, out = run([tree.name])
        self.assertEqual(code, 0)
        self.assertIn("No declared design tokens found", out)
        self.assertIn("not evidence", out)


class RepeatedLiteralTest(unittest.TestCase):
    CSS = (
        ".card { border-radius: 8px; padding: 16px; color: #9AA0A6; }\n"
        ".card-alt { border-radius: 8px; padding: 16px; color: #9AA0A6; }\n"
        ".solo { border-radius: 3px; }\n"
    )

    def test_reports_values_repeated_at_least_twice(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            base = Path(tree.name)
            literals = extract.collect_literals(base, base)
        pairs = {(row["property"], row["value"]): row["count"] for row in literals}
        self.assertEqual(pairs[("border-radius", "8px")], 2)
        self.assertEqual(pairs[("color", "#9AA0A6")], 2)

    def test_ignores_values_seen_once(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            base = Path(tree.name)
            literals = extract.collect_literals(base, base)
        self.assertNotIn(("border-radius", "3px"),
                         {(r["property"], r["value"]) for r in literals})

    def test_ignores_declarations_that_use_tokens(self) -> None:
        css = (".a { color: var(--brand); }\n.b { color: var(--brand); }\n")
        tree = write_tree({"a.css": css})
        with tree:
            base = Path(tree.name)
            self.assertEqual(extract.collect_literals(base, base), [])

    def test_ignores_noise_values(self) -> None:
        css = ".a { padding: 0; margin: auto; }\n.b { padding: 0; margin: auto; }\n"
        tree = write_tree({"a.css": css})
        with tree:
            base = Path(tree.name)
            self.assertEqual(extract.collect_literals(base, base), [])

    def test_records_locations(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            base = Path(tree.name)
            literals = extract.collect_literals(base, base)
        row = next(r for r in literals if r["value"] == "#9AA0A6")
        self.assertEqual(len(row["locations"]), 2)
        self.assertTrue(all(":" in loc for loc in row["locations"]))

    def test_surfaced_when_no_tokens_exist(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            code, out = run([tree.name])
        self.assertEqual(code, 0)
        self.assertIn("Observed repeated values", out)
        self.assertIn("not approved", out)

    def test_can_be_disabled(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            code, out = run([tree.name, "--no-literals"])
        self.assertEqual(code, 0)
        self.assertNotIn("Observed repeated values", out)

    def test_included_in_json(self) -> None:
        tree = write_tree({"a.css": self.CSS})
        with tree:
            code, out = run([tree.name, "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertTrue(payload["repeated_literals"])

    def test_missing_path_errors(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = extract.main(["/nonexistent/xyz"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
