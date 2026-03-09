#!/usr/bin/env python3
"""
test/validate.py – Validation script for the CryptPad CTF solvers.

Creates a known plaintext/ciphertext pair using encrypt_flag.cpp,
then verifies that decrypt_flag.py recovers the original plaintext.

Usage:
    python test/validate.py
"""

import sys
import os
import struct
import subprocess
import tempfile

# ---------------------------------------------------------------------------
# Ensure the project root is on the path so we can import decrypt_flag
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from decrypt_flag import RC4, xor_with_key, decrypt  # noqa: E402


# ---------------------------------------------------------------------------
# Inline encryption (mirrors encrypt_flag.cpp) so the test has no external deps
# ---------------------------------------------------------------------------

def encrypt(plaintext: str, key: bytes) -> bytes:
    data = bytearray(plaintext.encode())
    # XOR layer 1
    for i, b in enumerate(data):
        data[i] = b ^ key[i % len(key)]
    # RC4
    rc4_out = RC4(bytes(key)).process(bytes(data))
    data = bytearray(rc4_out)
    # XOR layer 2
    for i, b in enumerate(data):
        data[i] = b ^ key[i % len(key)]
    return bytes(data)


def build_enc_file(ciphertext: bytes, key: bytes, orig_len: int) -> bytes:
    footer = struct.pack("<I", orig_len) + key[:8].ljust(8, b"\x00") + b"\x00"
    return ciphertext + footer


# ---------------------------------------------------------------------------
# Test vectors
# ---------------------------------------------------------------------------

TEST_VECTORS = [
    # (plaintext, 8-byte key)
    ("flag{hello_world_test}", b"testkey1"),
    ("short",                  b"AAAAAAAA"),
    ("A" * 50,                 b"\x01\x02\x03\x04\x05\x06\x07\x08"),
    ("CTF{sample_flag_1234}",  b"ctfctfct"),
]


def run_test(plaintext: str, key: bytes) -> bool:
    ciphertext = encrypt(plaintext, key)
    file_data  = build_enc_file(ciphertext, key, len(plaintext))

    with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
        f.write(file_data)
        tmp_path = f.name

    try:
        recovered = decrypt(tmp_path)
        ok = recovered == plaintext
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] plaintext={plaintext!r:<30}  key={key!r}")
        if not ok:
            print(f"         expected: {plaintext!r}")
            print(f"         got:      {recovered!r}")
        return ok
    finally:
        os.unlink(tmp_path)


def main() -> None:
    print("CryptPad CTF – Validation Tests")
    print("=" * 50)

    passed = 0
    failed = 0

    for plaintext, key in TEST_VECTORS:
        if run_test(plaintext, key):
            passed += 1
        else:
            failed += 1

    # Also test decryption of the real flag.enc if present
    real_enc = os.path.join(ROOT, "flag.enc")
    if os.path.isfile(real_enc):
        print(f"\n  [INFO] flag.enc found – running live decryption:")
        try:
            flag = decrypt(real_enc)
            print(f"  [LIVE] Decrypted: {flag!r}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {exc}")
            failed += 1
    else:
        print(f"\n  [SKIP] flag.enc not found, skipping live test")

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
