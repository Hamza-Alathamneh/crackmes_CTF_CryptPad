# Reverse Engineering Guide

A step-by-step methodology for approaching reverse-engineering CTF challenges
like CryptPad.

---

## Step 1 – Understand What You Have

Before touching any tools:

1. Read the challenge description carefully.
2. List all provided files and their types:
   ```bash
   file *
   ```
3. Check file sizes – unusual sizes often hint at embedded data.
4. Run `strings` on the binary for readable clues:
   ```bash
   strings cryptpad.exe | grep -i flag
   strings cryptpad.exe | grep -i key
   strings cryptpad.exe | grep -i enc
   ```

---

## Step 2 – Static Analysis

**Goal**: Understand the code without running it.

### Recommended Tools

| Tool | Platform | Notes |
|------|----------|-------|
| [Ghidra](https://ghidra-sre.org/) | Cross-platform | Free, NSA-released |
| [IDA Free](https://hex-rays.com/ida-free/) | Cross-platform | Industry standard |
| [Cutter](https://cutter.re/) | Cross-platform | GUI for radare2 |
| [Binary Ninja](https://binary.ninja/) | Cross-platform | Commercial, trial available |

### Workflow

1. **Import the binary** into Ghidra / IDA.
2. **Identify entry point** – for PE binaries look for `WinMainCRTStartup` → `main`.
3. **Find interesting functions**:
   - Search for cross-references to file-read APIs (`ReadFile`, `fread`, `ifstream`)
   - Look for large constant arrays or loops iterating 256 times (→ RC4 KSA)
4. **Rename variables** as you understand them (`key`, `ciphertext`, `S`, etc.)
5. **Identify the algorithm**:
   - 256-element swap loop → RC4 KSA
   - Keystream XOR → RC4 PRGA
   - Simple byte-by-byte XOR → XOR cipher
6. **Trace data flow** from file read to output/display.

---

## Step 3 – Examine the Encrypted File

```bash
# Size
wc -c flag.enc

# Hex dump – look at beginning and end
xxd flag.enc
xxd flag.enc | tail -4

# Entropy analysis (high entropy → encrypted/compressed)
python3 -c "
import math, collections
d = open('flag.enc','rb').read()
c = collections.Counter(d)
entropy = -sum((v/len(d))*math.log2(v/len(d)) for v in c.values())
print(f'Entropy: {entropy:.4f} bits/byte')
"
```

Key questions:
- Does the file have a known header/magic bytes?
- Is there a readable footer or trailer?
- What is the file's entropy? (7.5–8.0 → likely encrypted)

---

## Step 4 – Understand the Encryption Algorithm

Once you've traced the binary's logic, document the algorithm in pseudocode:

```
read file → split into [ciphertext | footer(13 bytes)]
footer → extract key (8 bytes) and orig_len (4 bytes)
decrypt:
    step1 = XOR(ciphertext, key)
    step2 = RC4_decrypt(key, step1)
    step3 = XOR(step2, key)
    flag  = step3[:orig_len]
```

---

## Step 5 – Implement the Solver

Write a short script to automate decryption. Two options are provided:

```bash
# C++ (same language as original)
g++ -std=c++17 -o solver CTF_2026.cpp
./solver

# Python (cross-platform, faster to iterate)
python3 decrypt_flag.py
```

Validate against known test vectors (see `test/`).

---

## Step 6 – Dynamic Analysis (if needed)

If static analysis is unclear, run the binary in a debugger:

### Windows – x64dbg / WinDbg

1. Open `cryptpad.exe` in x64dbg.
2. Set a breakpoint on `WriteFile` or `printf`/`wprintf`.
3. Run until the breakpoint is hit.
4. Inspect registers and stack for the flag string.

### Linux (Wine) – gdb

```bash
wine cryptpad.exe   # if file is available
# or cross-compile / re-implement in Linux
```

---

## Common Patterns to Watch For

| Pattern | Likely Algorithm |
|---------|-----------------|
| 256-element init loop + swap loop | RC4 KSA |
| Byte XOR with array element | RC4 PRGA or XOR cipher |
| Modular addition/subtraction | Caesar cipher or simple obfuscation |
| S-Box lookups (16×16 table) | AES SubBytes |
| 32-bit rotations + additions | MD5 / SHA-1 / ChaCha20 |
| Magic constants 0x67452301, 0xefcdab89 | MD5 |
| Magic constants 0x6a09e667, 0xbb67ae85 | SHA-256 |

---

## Tips and Tricks

- **Rename aggressively** – every renamed variable makes the code clearer.
- **Use cross-references** – who calls this function? What does the return value feed?
- **Google magic constants** – a hex constant is often a signature.
- **Check library imports** – `CryptEncrypt`, `BCryptEncrypt` point to crypto APIs.
- **Don't reverse-engineer what you can search** – look for known algorithm signatures first.
