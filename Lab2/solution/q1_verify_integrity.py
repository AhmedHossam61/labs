#!/usr/bin/env python3
"""
CSE 532 - Lab 2, Question 1: SHA-256 File Integrity Verification
================================================================

Goal
----
A software publisher distributes the SHA-256 hash of the *legitimate* binary
over a trusted channel. The user re-computes the hash of each downloaded file
and keeps only the one whose hash matches the published value.

This script re-computes SHA-256 over every candidate .exe file in a directory
and reports which one matches the reference hash in Q1hash.txt.

Safety
------
The candidate files are NEVER executed. They are opened in binary read mode and
streamed through the hash function only. Streaming (fixed-size chunks) keeps
memory usage constant regardless of file size.

Usage
-----
    python -I q1_verify_integrity.py <Q1files_dir>

If no directory is given, it defaults to ../Lab2files/Q1files relative to this
script.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHUNK_SIZE = 65536  # 64 KiB streaming blocks


def sha256_of_file(path: Path) -> str:
    """Return the lowercase hex SHA-256 digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def load_reference_hash(hash_file: Path) -> str:
    """Read and normalise the published reference hash."""
    text = hash_file.read_text(encoding="utf-8").strip().lower()
    # Tolerate an optional "sha256:" prefix or surrounding whitespace.
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise ValueError(f"Reference hash is not a valid SHA-256 hex string: {text!r}")
    return text


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_dir = script_dir.parent / "Lab2files" / "Q1files"
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_dir

    hash_file = target_dir / "Q1hash.txt"
    if not hash_file.is_file():
        print(f"[ERROR] Q1hash.txt not found in {target_dir}", file=sys.stderr)
        return 2

    reference = load_reference_hash(hash_file)
    print(f"Reference SHA-256 (published): {reference}\n")

    candidates = sorted(target_dir.glob("*.exe"))
    if not candidates:
        print(f"[ERROR] No .exe files found in {target_dir}", file=sys.stderr)
        return 2

    print(f"{'File':<24} {'SHA-256':<64} Match")
    print("-" * 96)

    legitimate: list[str] = []
    for exe in candidates:
        computed = sha256_of_file(exe)
        matched = computed == reference
        if matched:
            legitimate.append(exe.name)
        print(f"{exe.name:<24} {computed:<64} {'<== MATCH' if matched else ''}")

    print("-" * 96)
    if len(legitimate) == 1:
        print(f"\nRESULT: The legitimate (authentic) program file is: {legitimate[0]}")
        return 0
    elif not legitimate:
        print("\nRESULT: No file matched the published hash. Integrity check FAILED for all files.")
        return 1
    else:
        print(f"\nRESULT: Unexpected - multiple files matched: {legitimate}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
