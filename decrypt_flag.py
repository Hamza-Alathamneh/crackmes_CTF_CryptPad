#!/usr/bin/env python3
"""
decrypt_flag.py – Python solver for the CryptPad CTF challenge.

Reads flag.enc from the current directory, extracts the embedded key and
original-length metadata from the 13-byte footer, then reverses the three-layer
encryption (XOR → RC4 → XOR) to recover the plaintext flag.

Usage:
    python decrypt_flag.py [path/to/flag.enc]
"""

import sys
import struct
import os


# ---------------------------------------------------------------------------
# RC4 stream cipher
# ---------------------------------------------------------------------------

class RC4:
    """RC4 stream cipher – encrypting and decrypting are the same operation."""

    def __init__(self, key: bytes) -> None:
        # Key Scheduling Algorithm (KSA)
        self._S = list(range(256))
        j = 0
        key_len = len(key)
        for k in range(256):
            j = (j + self._S[k] + key[k % key_len]) % 256
            self._S[k], self._S[j] = self._S[j], self._S[k]

    def process(self, data: bytes) -> bytes:
        """XOR *data* with the RC4 keystream and return the result."""
        S = self._S[:]  # work on a copy so the object stays reusable
        i = j = 0
        out = bytearray(len(data))
        for idx, byte in enumerate(data):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            keystream_byte = S[(S[i] + S[j]) % 256]
            out[idx] = byte ^ keystream_byte
        return bytes(out)


# ---------------------------------------------------------------------------
# XOR helper
# ---------------------------------------------------------------------------

def xor_with_key(data: bytes, key: bytes) -> bytes:
    """XOR *data* with *key* repeated to match len(data)."""
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


# ---------------------------------------------------------------------------
# Main decryption routine
# ---------------------------------------------------------------------------

def decrypt(enc_path: str) -> str:
    """Decrypt the flag stored in *enc_path* and return it as a string."""
    if not os.path.isfile(enc_path):
        raise FileNotFoundError(f"Encrypted file not found: {enc_path}")

    with open(enc_path, "rb") as f:
        file_data = f.read()

    if len(file_data) < 13:
        raise ValueError("File is too short to contain a valid footer (need ≥ 13 bytes).")

    # --- Extract footer (last 13 bytes) ---
    footer = file_data[-13:]
    orig_len = struct.unpack_from("<I", footer, 0)[0]   # 4-byte little-endian uint32
    key      = footer[4:12]                              # 8-byte key
    # footer[12] is the separator byte – ignored

    ciphertext = file_data[:-13]

    if orig_len > len(ciphertext):
        raise ValueError(
            f"Reported original length ({orig_len}) exceeds ciphertext length ({len(ciphertext)})."
        )

    # --- Reverse XOR → RC4 → XOR ---
    step1 = xor_with_key(ciphertext, key)   # undo outer XOR
    step2 = RC4(key).process(step1)         # undo RC4
    step3 = xor_with_key(step2, key)        # undo inner XOR

    plaintext = step3[:orig_len]
    return plaintext.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    enc_path = sys.argv[1] if len(sys.argv) > 1 else "flag.enc"
    try:
        flag = decrypt(enc_path)
        print(flag)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"[!] Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
