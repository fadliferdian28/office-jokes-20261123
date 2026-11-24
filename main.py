#!/usr/bin/env python3
"""Copy the one-line office joke from entry.txt to the output directory.

Stdlib only. Verifies the joke's sha256 against the expected value, checks
the make.fun gate (UTF-8, 1-199 characters, not whitespace-only), and writes
it to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt).
"""

import hashlib
import os
import sys

EXPECTED_SHA256 = "5a03011a1dc845fce25cba04b5bbc19f61f023e198ea75a0a9b06ac7130ecb88"

ENTRY_FILENAME = "entry.txt"
MIN_CHARS = 1
MAX_CHARS = 199


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, ENTRY_FILENAME)

    with open(src, "rb") as f:
        raw = f.read()

    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        print(
            f"error: sha256 mismatch for {ENTRY_FILENAME}: "
            f"got {digest}, expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"error: {ENTRY_FILENAME} is not valid UTF-8: {exc}", file=sys.stderr)
        return 1

    # The gate counts the whole file content; strip only the trailing newline
    # for the character check so the file's single line is what is judged.
    line = text.rstrip("\n")
    if "\n" in line or "\r" in line:
        print(f"error: {ENTRY_FILENAME} must be a single line", file=sys.stderr)
        return 1
    if not (MIN_CHARS <= len(line) <= MAX_CHARS):
        print(
            f"error: joke is {len(line)} characters, must be {MIN_CHARS}-{MAX_CHARS}",
            file=sys.stderr,
        )
        return 1
    if not line.strip():
        print(f"error: {ENTRY_FILENAME} is whitespace-only", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, ENTRY_FILENAME)

    if os.path.abspath(src) == os.path.abspath(dst) or (
        os.path.exists(dst) and os.path.samefile(src, dst)
    ):
        raise SameFileError(f"source and destination are the same file: {src}")

    with open(dst, "wb") as f:
        f.write(raw)

    print(f"chars: {len(line)}")
    print(f"sha256: {digest}")
    print(f"wrote: {dst}")
    return 0


class SameFileError(Exception):
    """Raised when the source and destination resolve to the same file."""


if __name__ == "__main__":
    sys.exit(main())
