#!/usr/bin/env python3
"""
CSE 532 - Lab 2, Question 2: RSA PKCS#1 v1.5 Digital Signature Verification
===========================================================================

Goal
----
A SHA-256 hash alone proves integrity but NOT authenticity: an attacker who can
substitute the published hash can pass off malware as genuine. A digital
signature fixes this. The vendor signs SHA-256(file) with their RSA *private*
key; anyone can verify with the vendor's *public* key (PublicKey.pem).

This script verifies every <name>.exe / <name>.exe.sign pair against the
vendor's public key using RSA PKCS#1 v1.5 with SHA-256, and reports the single
file whose signature is valid.

Why hash-then-sign
------------------
RSA can only sign data smaller than the modulus. The file is first reduced to a
fixed 32-byte SHA-256 digest; the signature is computed over that digest. This
is both efficient and secure (collision resistance of SHA-256 carries over).

Safety
------
Candidate files are NEVER executed - only read as bytes for hashing/verifying.

Usage
-----
    python -I q2_verify_signature.py <Q2files_dir>

Defaults to ../Lab2files/Q2files relative to this script.
"""
from __future__ import annotations

import sys
from pathlib import Path

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_dir = script_dir.parent / "Lab2files" / "Q2files"
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_dir

    key_path = target_dir / "PublicKey.pem"
    if not key_path.is_file():
        print(f"[ERROR] PublicKey.pem not found in {target_dir}", file=sys.stderr)
        return 2

    public_key = RSA.import_key(key_path.read_bytes())
    verifier = pkcs1_15.new(public_key)
    print(f"Loaded vendor public key: RSA-{public_key.size_in_bits()} "
          f"(e={public_key.e})\n")

    # Pair every .exe with its claimed .exe.sign signature file.
    exe_files = sorted(p for p in target_dir.glob("*.exe") if p.suffix == ".exe")
    if not exe_files:
        print(f"[ERROR] No .exe files found in {target_dir}", file=sys.stderr)
        return 2

    print(f"{'File':<22} {'Signature file':<26} Result")
    print("-" * 70)

    valid: list[str] = []
    for exe in exe_files:
        sig_path = exe.with_name(exe.name + ".sign")
        if not sig_path.is_file():
            print(f"{exe.name:<22} {'(missing)':<26} NO SIGNATURE FILE")
            continue

        # Hash the file contents (streamed) and verify the signature over it.
        h = SHA256.new()
        with exe.open("rb") as fh:
            for block in iter(lambda: fh.read(65536), b""):
                h.update(block)
        signature = sig_path.read_bytes()

        try:
            verifier.verify(h, signature)
            valid.append(exe.name)
            print(f"{exe.name:<22} {sig_path.name:<26} VALID  <== authentic")
        except (ValueError, TypeError):
            print(f"{exe.name:<22} {sig_path.name:<26} invalid")

    print("-" * 70)
    if len(valid) == 1:
        print(f"\nRESULT: The correctly signed (authentic) file is: {valid[0]}")
        return 0
    elif not valid:
        print("\nRESULT: No file carried a valid signature.")
        return 1
    else:
        print(f"\nRESULT: Unexpected - multiple valid signatures: {valid}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
