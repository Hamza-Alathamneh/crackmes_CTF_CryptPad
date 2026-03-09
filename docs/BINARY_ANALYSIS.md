# Binary Analysis – cryptpad.exe

This document explains how to analyse the `cryptpad.exe` binary using static
and dynamic techniques to understand the encryption scheme.

---

## Basic Information

```
File:        cryptpad.exe
Format:      PE32 (Windows Portable Executable, 32-bit)
Architecture: x86
```

Verify with:
```bash
file cryptpad.exe
```

---

## Step 1 – String Extraction

```bash
strings cryptpad.exe
```

Interesting output to look for:
- File paths (e.g., references to `flag.enc`)
- Error messages that hint at the algorithm
- Library names (e.g., `msvcrt.dll` → Microsoft C runtime)

---

## Step 2 – Import Table Analysis

The import table lists every Windows API function the binary calls.

In Ghidra: *Window → Imports*  
In IDA: *View → Open subviews → Imports*

Key imports to spot in CryptPad:

| Import | Meaning |
|--------|---------|
| `CreateFileA` / `ReadFile` | File reading |
| `WriteConsoleW` / `printf` | Output (flag display) |
| *(no CryptEncrypt)* | Custom crypto, not Windows API |

The absence of `CryptEncrypt` / `BCryptEncrypt` confirms the encryption is
implemented manually in the binary.

---

## Step 3 – Identifying the RC4 KSA in Disassembly

The RC4 Key Scheduling Algorithm has a recognisable signature:

```asm
; Initialise S[0..255] = 0..255
xor  eax, eax
@@init:
    mov  [S + eax], al
    inc  eax
    cmp  eax, 256
    jl   @@init

; KSA swap loop
xor  ecx, ecx          ; j = 0
xor  eax, eax          ; k = 0
@@ksa:
    movzx edx, byte [S + eax]          ; S[k]
    add   ecx, edx
    movzx edx, byte [key + eax % 8]    ; key[k % keylen]
    add   ecx, edx
    and   ecx, 0xFF                     ; % 256

    ; swap S[k] and S[j]
    movzx edx, byte [S + ecx]
    movzx esi, byte [S + eax]
    mov   [S + eax], dl
    mov   [S + ecx], sl

    inc   eax
    cmp   eax, 256
    jl    @@ksa
```

In Ghidra's decompiled C this typically looks like:

```c
for (k = 0; k < 256; k++) {
    j = (j + S[k] + key[k % key_len]) & 0xFF;
    tmp = S[k]; S[k] = S[j]; S[j] = tmp;
}
```

---

## Step 4 – Identifying the PRGA and XOR Layers

After the KSA you will see another loop with `i`, `j` increments and a final
XOR – that is the PRGA keystream generation.

The surrounding XOR loops (before and after RC4) use the same key with modulo
indexing – look for patterns like:

```asm
mov  al, [data + ecx]
xor  al, [key + ecx % 8]
mov  [data + ecx], al
inc  ecx
```

---

## Step 5 – Footer Extraction Logic

Near the file-reading code you will see arithmetic that computes `file_size - 13`:

```c
footer_start = file_size - 13;
orig_len = *(uint32_t*)(buf + footer_start);       // 4 bytes
key      = buf + footer_start + 4;                 // next 8 bytes
cipher   = buf;  // first (file_size - 13) bytes
```

This is the key insight: **the decryption key is stored inside the file itself**.

---

## Step 6 – Dynamic Analysis Walkthrough

### Using x64dbg (Windows)

1. Open `cryptpad.exe` in x64dbg.
2. Go to *Symbols* → find `main` or entry point.
3. Set a breakpoint just after the final XOR loop (before `printf`/`WriteConsoleW`).
4. Run. When the breakpoint hits, inspect:
   - `RAX`/`EAX` or a stack variable for the flag pointer
   - *Memory dump* window at the pointer address

### Using Ghidra (recommended for static analysis)

1. Import `cryptpad.exe`.
2. Accept auto-analysis defaults.
3. Open *Defined Strings* window → find any path string → double-click → follow xref to `main`.
4. Work forward from the file-open call, renaming variables.
5. The decompiled C will closely match `CTF_2026.cpp`.

---

## Summary of the Algorithm (Reconstructed)

```
flag.enc:
┌─────────────────────────────────────────────┬─────────────────────────┐
│            ciphertext  (51 bytes)            │   footer  (13 bytes)    │
└─────────────────────────────────────────────┴─────────────────────────┘
                                               │ 4B len │ 8B key │ 1B sep│

Decryption:
  key      = footer[4:12]
  orig_len = uint32_le(footer[0:4])
  buf      = file[:51]
  buf      = XOR(buf, key)          // undo outer XOR
  buf      = RC4(key, buf)          // undo RC4
  buf      = XOR(buf, key)          // undo inner XOR
  flag     = buf[:orig_len]
```
