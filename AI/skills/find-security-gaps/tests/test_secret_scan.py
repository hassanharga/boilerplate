from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "secret-scan.py"
SPEC = importlib.util.spec_from_file_location("secret_scan", SCRIPT)
assert SPEC and SPEC.loader
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)

# Values used only inside the test process. The whole point of the assertions
# below is that none of them ever reaches stdout.
# Deliberately not AWS's published EXAMPLE keys: those trip the placeholder
# heuristic, which is correct behaviour and would make these tests vacuous.
AWS_KEY = "AKIAQ7Z3JW5TN2RVD4KC"
LIVE_LOOKING = "wJalrXUtnFEMI2K7MDENGbPxRfiCYzQ9tLpVm3Xs"
GITHUB_TOKEN = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"


def run(argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = scanner.main(argv)
    return code, buffer.getvalue()


def write_tree(files: dict[str, str]) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    for name, content in files.items():
        path = Path(tmp.name) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp


class FingerprintTest(unittest.TestCase):
    def test_is_twelve_hex_chars(self) -> None:
        value = scanner.fingerprint(LIVE_LOOKING)
        self.assertRegex(value, r"^[0-9a-f]{12}$")

    def test_is_stable(self) -> None:
        self.assertEqual(
            scanner.fingerprint(LIVE_LOOKING), scanner.fingerprint(LIVE_LOOKING)
        )

    def test_differs_between_values(self) -> None:
        self.assertNotEqual(
            scanner.fingerprint("one-secret"), scanner.fingerprint("two-secret")
        )

    def test_does_not_contain_the_value(self) -> None:
        self.assertNotIn(LIVE_LOOKING[:8], scanner.fingerprint(LIVE_LOOKING))


class PlaceholderTest(unittest.TestCase):
    def test_obvious_placeholders(self) -> None:
        for value in (
            "your-api-key-here", "changeme", "xxxxxxxxxxxx", "<your-token>",
            "${API_TOKEN}", "example-secret-value", "REDACTED",
        ):
            self.assertTrue(scanner.looks_like_placeholder(value), value)

    def test_credible_value_is_not_a_placeholder(self) -> None:
        self.assertFalse(scanner.looks_like_placeholder(LIVE_LOOKING))


class DetectionTest(unittest.TestCase):
    def test_detects_aws_key_id(self) -> None:
        found = scanner.scan_text(f'const k = "{AWS_KEY}"', "a.ts")
        self.assertTrue(any(f["rule"] == "aws-access-key-id" for f in found))

    def test_detects_private_key_header(self) -> None:
        found = scanner.scan_text("-----BEGIN RSA PRIVATE KEY-----", "id_rsa")
        self.assertEqual(found[0]["rule"], "private-key")

    def test_detects_github_token(self) -> None:
        found = scanner.scan_text(f"token: {GITHUB_TOKEN}", "ci.yml")
        self.assertTrue(any(f["rule"] == "github-token" for f in found))

    def test_detects_secret_assignment(self) -> None:
        found = scanner.scan_text(f'password = "{LIVE_LOOKING}"', "conf.py")
        rules = {f["rule"] for f in found}
        self.assertIn("secret-assignment", rules)

    def test_url_credentials_fingerprint_only_the_password(self) -> None:
        found = scanner.scan_text(
            "DB=postgres://admin:sup3rs3cr3tvalue@db.internal:5432/x", "env.ts"
        )
        entry = next(f for f in found if f["rule"] == "url-embedded-credentials")
        self.assertEqual(entry["fingerprint"], scanner.fingerprint("sup3rs3cr3tvalue"))

    def test_records_line_numbers(self) -> None:
        found = scanner.scan_text(f"line one\nline two\nk='{AWS_KEY}'", "a.ts")
        self.assertEqual(found[0]["line"], 3)

    def test_clean_text_yields_nothing(self) -> None:
        self.assertEqual(scanner.scan_text("const total = a + b;", "a.ts"), [])


class OutputSafetyTest(unittest.TestCase):
    """The output must never contain a matched value. This is the point."""

    def test_table_output_omits_every_secret(self) -> None:
        tree = write_tree({
            "src/config.ts": f'export const key = "{AWS_KEY}";\n',
            "src/db.ts": f'const pw = "{LIVE_LOOKING}";\n',
            ".github/ci.yml": f"token: {GITHUB_TOKEN}\n",
        })
        with tree:
            code, out = run([tree.name, "--no-gitleaks"])
        self.assertEqual(code, 1)
        for secret in (AWS_KEY, LIVE_LOOKING, GITHUB_TOKEN):
            self.assertNotIn(secret, out)
        self.assertIn("config.ts", out)

    def test_json_output_omits_every_secret(self) -> None:
        tree = write_tree({"a.ts": f'const k = "{AWS_KEY}";\n'})
        with tree:
            code, out = run([tree.name, "--no-gitleaks", "--json"])
        self.assertEqual(code, 1)
        self.assertNotIn(AWS_KEY, out)
        payload = json.loads(out)
        self.assertEqual(payload["credible_count"], 1)
        for entry in payload["candidates"]:
            self.assertEqual(set(entry), {"path", "line", "rule",
                                          "fingerprint", "status"})
            self.assertRegex(entry["fingerprint"], r"^[0-9a-f]{12}$")

    def test_no_long_random_looking_token_survives_in_output(self) -> None:
        tree = write_tree({"a.ts": f'const k = "{AWS_KEY}";\n'})
        with tree:
            _, out = run([tree.name, "--no-gitleaks"])
        for token in re.findall(r"[A-Za-z0-9_\-]{16,}", out):
            self.assertNotIn(token, AWS_KEY)


class ScanBehaviourTest(unittest.TestCase):
    def test_skips_ignored_directories(self) -> None:
        tree = write_tree({"node_modules/pkg/index.js": f'k="{AWS_KEY}"\n'})
        with tree:
            code, out = run([tree.name, "--no-gitleaks"])
        self.assertEqual(code, 0)
        self.assertIn("No credential candidates", out)

    def test_placeholders_are_suppressed_by_default(self) -> None:
        tree = write_tree({".env.example": 'API_KEY="your-api-key-here"\n'})
        with tree:
            code, out = run([tree.name, "--no-gitleaks"])
        self.assertEqual(code, 0)
        self.assertIn("suppressed", out)

    def test_placeholders_can_be_listed(self) -> None:
        tree = write_tree({".env.example": 'API_KEY="your-api-key-here"\n'})
        with tree:
            code, out = run([tree.name, "--no-gitleaks",
                             "--include-placeholders"])
        self.assertEqual(code, 0)
        self.assertIn("likely-placeholder", out)

    def test_clean_tree_exits_zero(self) -> None:
        tree = write_tree({"a.ts": "export const sum = (a, b) => a + b;\n"})
        with tree:
            code, out = run([tree.name, "--no-gitleaks"])
        self.assertEqual(code, 0)
        self.assertIn("not proof of absence", out)

    def test_missing_path_errors(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = scanner.main(["/nonexistent/path/xyz", "--no-gitleaks"])
        self.assertEqual(code, 2)

    def test_binary_and_large_files_are_skipped(self) -> None:
        tree = write_tree({"logo.png": f"binary {AWS_KEY}\n"})
        with tree:
            code, _ = run([tree.name, "--no-gitleaks"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
