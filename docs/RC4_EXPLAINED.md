# RC4 Explained

RC4 (Rivest Cipher 4) is a stream cipher designed by Ron Rivest in 1987.
Despite being considered cryptographically weak today, it is frequently studied
in reverse-engineering challenges because of its distinctive code patterns.

---

## How RC4 Works

RC4 operates in two phases:

### Phase 1 – Key Scheduling Algorithm (KSA)

The KSA initialises a 256-byte permutation array **S** using the key:

```
S = [0, 1, 2, ..., 255]   # initialise identity permutation

j = 0
for k in range(256):
    j = (j + S[k] + key[k % len(key)]) % 256
    swap(S[k], S[j])
```

After the KSA, **S** is a pseudo-random permutation of 0–255 derived from the key.

### Phase 2 – Pseudo-Random Generation Algorithm (PRGA)

The PRGA produces a keystream one byte at a time:

```
i = 0
j = 0
for each plaintext byte P:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    swap(S[i], S[j])
    keystream_byte = S[(S[i] + S[j]) % 256]
    ciphertext_byte = P XOR keystream_byte
```

### Visual Diagram

```
Key ──────────────────────────┐
                              ▼
               ┌──────────── KSA ────────────┐
               │   S = permuted [0..255]      │
               └──────────────────────────────┘
                              │
Plaintext ───► XOR ◄── PRGA keystream ◄── S (evolving state)
                │
                ▼
           Ciphertext
```

---

## Properties of RC4

| Property | Value |
|----------|-------|
| Key length | 1–256 bytes (commonly 40–128 bits) |
| State size | 256 bytes + 2 counters |
| Output | 1 byte per cycle |
| Symmetric | Yes – same operation for encrypt & decrypt |
| Security | **Broken** – do not use in production |

---

## Why RC4 is Broken

1. **Biased keystream**: The first bytes of the keystream are statistically biased
   → always discard the first 256+ bytes in real usage (RC4-drop[N]).
2. **Related-key attacks**: RC4 is vulnerable when many messages share related keys
   (exploited in WEP cracking).
3. **Fluhrer-Mantin-Shamir (FMS) attack**: Reveals the key from a large number of
   observed outputs (the basis of `aircrack-ng`).
4. **BEAST and CRIME** attacks exploit RC4 in TLS.

---

## RC4 in This Challenge

The challenge uses a custom XOR → RC4 → XOR wrapper:

```
plaintext
  │
  ▼ XOR(key, repeating 8-byte key)
  │
  ▼ RC4(key)                         ← standard RC4, same 8-byte key
  │
  ▼ XOR(key, repeating 8-byte key)
  │
ciphertext
```

Because XOR is its own inverse and RC4 is symmetric, the **decrypt** function
is identical to the **encrypt** function.

---

## Identifying RC4 in Disassembly

Look for:
- A loop counting **256 iterations** that initialises an array → KSA setup
- A swap of two array elements indexed by derived values → the swap in KSA/PRGA
- XOR of a data byte with an array element → keystream application

Common Ghidra / IDA signatures:
```
; KSA characteristic pattern
MOV  [S + RAX], AL     ; S[k] = k
INC  RAX
CMP  RAX, 256
JNE  ...
```

---

## Further Reading

- [Wikipedia – RC4](https://en.wikipedia.org/wiki/RC4)
- [RFC 4345](https://datatracker.ietf.org/doc/html/rfc4345) – Improved Arcfour Modes
- Fluhrer, Mantin, Shamir – *Weaknesses in the Key Scheduling Algorithm of RC4*
