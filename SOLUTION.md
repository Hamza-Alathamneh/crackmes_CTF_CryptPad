# SOLUTION.md – CryptPad CTF Writeup

## Overview

CryptPad is a reverse-engineering challenge created by **crudd** on crackmes.one.
The goal is to recover a flag stored in `flag.enc`, which has been encrypted with a
custom scheme built on RC4 and XOR.

---

## Methodology

### 1. Initial Reconnaissance

Start by gathering basic information about the provided files:

```bash
file cryptpad.exe          # PE32 Windows executable
xxd flag.enc | head -5     # hex dump – look for structure
wc -c flag.enc             # 64 bytes total
```

Key observation: `flag.enc` is exactly **64 bytes**.  
CTF flags are rarely that long, so some of those bytes must be metadata.

### 2. Binary Analysis (Static)

Open `cryptpad.exe` in a disassembler (Ghidra / IDA Free / Cutter):

- Search for string references → finds the path to `flag.enc`
- Identify `ReadFile` / `fread` calls to locate where the file is loaded
- Trace data-flow from the buffer to find XOR loops and the RC4 KSA/PRGA

Key findings in the binary:
- A loop iterating 256 times initialises an array → **RC4 Key Scheduling Algorithm (KSA)**
- Two XOR loops bracket the RC4 call → custom obfuscation layers
- The last 13 bytes of the buffer are treated separately → **footer extraction**

### 3. Footer Structure

From the binary analysis the footer (last 13 bytes) holds:

| Offset | Size | Description |
|--------|------|-------------|
| 0      | 4    | `uint32_t` original plaintext length (little-endian) |
| 4      | 8    | 8-byte RC4 / XOR key |
| 12     | 1    | Separator byte (ignored) |

```python
import struct, sys

data = open("flag.enc", "rb").read()
footer = data[-13:]
orig_len = struct.unpack_from("<I", footer, 0)[0]  # little-endian uint32
key      = footer[4:12]                             # 8-byte key
cipher   = data[:-13]                              # everything before footer
print(f"Key (hex): {key.hex()}")
print(f"Original length: {orig_len}")
```

### 4. Encryption Scheme (Forward Direction)

```
plaintext
   │
   ▼ XOR with 8-byte key (repeating)
   │
   ▼ RC4 encrypt (same 8-byte key)
   │
   ▼ XOR with 8-byte key (repeating)
   │
ciphertext  +  footer (13 bytes)  →  flag.enc
```

### 5. Decryption (Reverse Direction)

Because XOR and RC4 are both self-inverse (applying the same operation twice
restores the original), the decryption mirrors the encryption exactly:

```
ciphertext
   │
   ▼ XOR with 8-byte key (repeating)       ← undo outer XOR
   │
   ▼ RC4 process (same 8-byte key)         ← undo RC4
   │
   ▼ XOR with 8-byte key (repeating)       ← undo inner XOR
   │
plaintext  (take first orig_len bytes)
```

### 6. RC4 Implementation

```cpp
// Key Scheduling Algorithm (KSA)
vector<uint8_t> S(256);
iota(S.begin(), S.end(), 0);
int j = 0;
for (int k = 0; k < 256; ++k) {
    j = (j + S[k] + key[k % 8]) % 256;
    swap(S[k], S[j]);
}

// Pseudo-Random Generation Algorithm (PRGA)
int i = 0; j = 0;
for each byte b in data:
    i = (i + 1) % 256;
    j = (j + S[i]) % 256;
    swap(S[i], S[j]);
    output_byte = b ^ S[(S[i] + S[j]) % 256];
```

### 7. Running the Solver

```bash
# Compile and run the C++ solver
g++ -std=c++17 -O2 -o solver CTF_2026.cpp
./solver        # must be run in the same directory as flag.enc

# Or use the Python solver
python decrypt_flag.py
```

---

## Key Findings and Observations

1. **Self-contained key**: The key is embedded in the file itself – no external
   secret is needed, making this a *self-decrypting* archive pattern.
2. **Symmetric operations**: Both XOR and RC4 are their own inverses, so the same
   code path can encrypt and decrypt.
3. **Footer as metadata**: Appending metadata to the end of the ciphertext is a
   common pattern in custom CTF challenges.
4. **No integrity check**: There is no MAC or checksum, so corrupted files are
   silently mishandled.

---

## Alternative Approaches

### Dynamic Analysis
- Run `cryptpad.exe` in x64dbg / WinDbg
- Set a breakpoint at the `WriteConsoleW` / `printf` call
- Read the flag from the stack/register at that point

### Scripted Extraction
- Use `xxd`/`python` to manually parse the footer and implement RC4 from scratch
- See `decrypt_flag.py` for a clean standalone Python implementation

### Automated Tools
- [CyberChef](https://gchq.github.io/CyberChef/) can perform RC4 and XOR
  operations interactively if you supply the key manually
