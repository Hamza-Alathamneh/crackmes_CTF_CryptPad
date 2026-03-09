# HINTS.md – Progressive Hints for CryptPad

Work through the levels in order. Only peek at the next level after you're genuinely stuck!

---

## Level 1 – Easy 🟢

<details>
<summary>Click to reveal hint 1</summary>

The encrypted file is not just raw ciphertext – it contains extra data appended at the end.
Try looking at the **last few bytes** of `flag.enc` in a hex editor.

What does the file's total size (64 bytes) tell you about how much is ciphertext vs. metadata?

</details>

---

## Level 2 – Medium 🟡

<details>
<summary>Click to reveal hint 2</summary>

The file ends with a **13-byte footer**:

```
[4 bytes] original plaintext length (little-endian uint32)
[8 bytes] encryption key
[1 byte]  separator / padding
```

That means the last 13 bytes contain everything you need to decrypt the flag – no brute force required!

Extract the key and the original length, then focus on the first `(filesize − 13)` bytes.

</details>

---

## Level 3 – Harder 🔴

<details>
<summary>Click to reveal hint 3</summary>

The decryption is performed in **three steps** applied in reverse order of encryption:

1. **XOR** the ciphertext with the 8-byte key (repeating)
2. **RC4-decrypt** the result using the same 8-byte key
3. **XOR** again with the same 8-byte key (repeating)

RC4 is a symmetric stream cipher, so "encrypting" and "decrypting" are the same operation (just call `process()` with the same key).

After step 3, take only the first `original_length` bytes – that is your flag.

</details>

---

## Spoiler – Full Solution 🚨

<details>
<summary>⚠️ Only open if you have truly given up</summary>

See `SOLUTION.md` for the complete step-by-step walkthrough, or run the provided
solver directly:

```bash
# C++ solver
make solver
./solver

# Python solver
python decrypt_flag.py
```

</details>
