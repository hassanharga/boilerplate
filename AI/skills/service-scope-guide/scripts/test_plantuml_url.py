import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import plantuml_url


SOURCE = "@startuml\nAlice -> Bob: hello\n@enduml\n"
KNOWN_ENCODING = "SoWkIImgAStDuNBCoKnELT2rKt3AJx9Io4ZDoSddSaZDIm790G00"


class PlantUmlUrlTest(unittest.TestCase):
    def test_known_encoding(self) -> None:
        self.assertEqual(plantuml_url.encode(SOURCE), KNOWN_ENCODING)

    def test_unicode_round_trip(self) -> None:
        source = "@startuml\nAlice -> Bob: أهلاً 👋\n@enduml"
        self.assertEqual(plantuml_url.decode(plantuml_url.encode(source)), source)

    def test_decode_accepts_url_query_and_fragment(self) -> None:
        url = f"{plantuml_url.SERVER}/svg/{KNOWN_ENCODING}?cache=1#diagram"
        self.assertEqual(plantuml_url.decode(url), SOURCE)

    def test_extract_encoded_rejects_empty_or_invalid_values(self) -> None:
        for value in ("", "https://plant-uml.yplatform.dev/svg/", "not valid!"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                plantuml_url.extract_encoded(value)

    def test_decode_rejects_malformed_payload(self) -> None:
        with self.assertRaises(ValueError):
            plantuml_url.decode("abcd")

    def test_main_encodes_utf8_file_and_selected_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "diagram.puml"
            source_path.write_text(SOURCE, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                result = plantuml_url.main(["encode", str(source_path), "--format", "png"])

        self.assertEqual(result, 0)
        self.assertEqual(
            output.getvalue(),
            f"{plantuml_url.SERVER}/png/{KNOWN_ENCODING}\n",
        )

    def test_main_reads_stdin(self) -> None:
        output = io.StringIO()
        with patch.object(plantuml_url.sys, "stdin", io.StringIO(SOURCE)):
            with redirect_stdout(output):
                plantuml_url.main(["encode", "-"])
        self.assertEqual(
            output.getvalue(),
            f"{plantuml_url.SERVER}/svg/{KNOWN_ENCODING}\n",
        )

    def test_main_decodes_to_stdout(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = plantuml_url.main(["decode", KNOWN_ENCODING])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), SOURCE)

    def test_main_reports_missing_file(self) -> None:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                plantuml_url.main(["encode", "/definitely/missing/diagram.puml"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
