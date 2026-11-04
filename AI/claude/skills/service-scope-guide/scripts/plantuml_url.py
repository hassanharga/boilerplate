#!/usr/bin/env python3
"""Encode/decode PlantUML source for the Yassir PlantUML server.

The Notion design guides embed diagrams as plain image URLs of the form
`https://plant-uml.yplatform.dev/svg/<encoded>`, where <encoded> is the standard
PlantUML text encoding: raw DEFLATE, then base64 over PlantUML's own alphabet.

Encoding the URL yourself means the diagram renders in Notion immediately, with no
manual round-trip through the PlantUML web editor. Decoding lets you recover the
source of a diagram that is already in a guide, which is how you diff an existing
domain model against the code instead of guessing what the picture shows.

Usage:
    python3 plantuml_url.py encode diagram.puml [--format svg|png]
    python3 plantuml_url.py decode 'https://plant-uml.yplatform.dev/svg/xLXDR-Cs...'
    cat diagram.puml | python3 plantuml_url.py encode -
"""

import argparse
import base64
import sys
import zlib
from pathlib import Path
from urllib.parse import urlsplit

PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
STANDARD_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
SERVER = "https://plant-uml.yplatform.dev"


def encode(text: str) -> str:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    data = compressor.compress(text.encode("utf-8")) + compressor.flush()

    out = []
    for i in range(0, len(data), 3):
        chunk = data[i : i + 3]
        b1 = chunk[0]
        b2 = chunk[1] if len(chunk) > 1 else 0
        b3 = chunk[2] if len(chunk) > 2 else 0
        out.append(PLANTUML_ALPHABET[b1 >> 2])
        out.append(PLANTUML_ALPHABET[((b1 & 0x3) << 4) | (b2 >> 4)])
        out.append(PLANTUML_ALPHABET[((b2 & 0xF) << 2) | (b3 >> 6)])
        out.append(PLANTUML_ALPHABET[b3 & 0x3F])
    return "".join(out)


def extract_encoded(value: str) -> str:
    """Return the encoded PlantUML segment from a URL or bare value."""
    value = value.strip()
    if "://" in value:
        path = urlsplit(value).path
        if path.endswith("/"):
            raise ValueError("PlantUML URL or encoded value is empty")
        value = path
    encoded = value.rsplit("/", 1)[-1]
    if not encoded:
        raise ValueError("PlantUML URL or encoded value is empty")
    invalid = set(encoded) - set(PLANTUML_ALPHABET)
    if invalid:
        raise ValueError("PlantUML value contains invalid characters")
    return encoded


def decode(value: str) -> str:
    encoded = extract_encoded(value)
    translated = encoded.translate(str.maketrans(PLANTUML_ALPHABET, STANDARD_B64))
    padded = translated + "=" * (-len(translated) % 4)
    try:
        raw = base64.b64decode(padded, validate=True)
        return zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8")
    except (ValueError, zlib.error, UnicodeDecodeError) as error:
        raise ValueError("PlantUML value could not be decoded") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encode", help="PlantUML source file (or - for stdin) -> URL")
    enc.add_argument("source")
    enc.add_argument("--format", default="svg", choices=["svg", "png", "txt"])

    dec = sub.add_parser("decode", help="URL or encoded string -> PlantUML source")
    dec.add_argument("url")

    args = parser.parse_args(argv)

    try:
        if args.cmd == "encode":
            text = (
                sys.stdin.read()
                if args.source == "-"
                else Path(args.source).read_text(encoding="utf-8")
            )
            print(f"{SERVER}/{args.format}/{encode(text)}")
        else:
            sys.stdout.write(decode(args.url))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
