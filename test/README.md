# Test Vectors for CryptPad CTF

This folder contains known plaintext / ciphertext pairs and a validation script
to verify that both the C++ and Python solvers work correctly.

## Files

| File | Description |
|------|-------------|
| `validate.py` | Python validation script – runs all test vectors |

## Running the Tests

```bash
# From the project root:
python test/validate.py
```

Expected output:
```
CryptPad CTF – Validation Tests
==================================================
  [PASS] plaintext='flag{hello_world_test}'    key=b'testkey1'
  [PASS] plaintext='short'                     key=b'AAAAAAAA'
  [PASS] plaintext='AAAA...'                   key=b'\x01\x02\x03...'
  [PASS] plaintext='CTF{sample_flag_1234}'     key=b'ctfctfct'
==================================================
Results: 4 passed, 0 failed
```

## Known Test Vectors

| Plaintext | Key (hex) | Notes |
|-----------|-----------|-------|
| `flag{hello_world_test}` | `74657374 6b657931` | ASCII key `testkey1` |
| `short` | `41414141 41414141` | Key of all `A`s |
| 50× `A` | `01020304 05060708` | Long plaintext |
| `CTF{sample_flag_1234}` | `63746663 74666374` | ASCII key `ctfctfct` |
