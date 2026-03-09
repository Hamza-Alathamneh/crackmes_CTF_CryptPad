# CryptPad - CTF Reverse Engineering Challenge

[![Difficulty](https://img.shields.io/badge/Difficulty-3.0%2F5-orange)]()
[![Quality](https://img.shields.io/badge/Quality-4.0%2F5-brightgreen)]()

A reverse engineering challenge featuring custom RC4 encryption with additional obfuscation layers.

## Overview

**CryptPad** is a reverse engineering CTF challenge created by crudd that tests your ability to analyze and reverse a multi-layered encryption scheme. The challenge involves decrypting a flag that has been encrypted using RC4 along with custom XOR operations.

## Challenge Files

- `cryptpad.exe` - Windows executable (binary challenge)
- `CTF_2026.cpp` - C++ solution source code
- `flag.enc` - Encrypted flag file (64 bytes)
- `README.md` - This documentation

## Challenge Description

The objective is to reverse engineer the encryption scheme used to protect a flag stored in `flag.enc`. The encryption uses a combination of:
- RC4 stream cipher
- XOR obfuscation layers
- Custom footer structure containing metadata

**Difficulty**: 3.0/5  
**Quality**: 4.0/5

## Solution

### Encryption Scheme Analysis

The flag is encrypted using a three-layer approach:

1. **XOR Layer 1**: The plaintext is XORed with an 8-byte key (repeating pattern)
2. **RC4 Encryption**: The result is encrypted using RC4 with the same 8-byte key
3. **XOR Layer 2**: The RC4 output is XORed again with the same key
4. **Footer**: A 13-byte footer is appended containing:
   - 4 bytes: Original plaintext length (little-endian)
   - 8 bytes: The encryption key
   - 1 byte: Separator/padding

### File Structure

```
flag.enc structure:
[Encrypted Data (51 bytes)] + [Footer (13 bytes)]

Footer format:
- Bytes 0-3:   Original length (uint32_t, little-endian)
- Bytes 4-11:  8-byte encryption key
- Byte 12:     Separator
```

### Decryption Steps

1. **Extract Footer**: Read the last 13 bytes to retrieve:
   - Original plaintext length
   - 8-byte encryption key

2. **Extract Ciphertext**: Everything before the footer is the encrypted data

3. **First XOR**: XOR the ciphertext with the repeating 8-byte key

4. **RC4 Decryption**: Initialize RC4 with the key and process the data

5. **Second XOR**: XOR the RC4 output with the repeating key again

6. **Truncate**: Use the original length to extract the correct plaintext

### Solution Code

The solution is implemented in `CTF_2026.cpp`. Here's the breakdown:

```cpp
// Read encrypted file
ifstream file("flag.enc", ios::binary);
vecto...