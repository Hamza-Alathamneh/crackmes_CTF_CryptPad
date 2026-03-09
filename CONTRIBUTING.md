# Contributing to CryptPad CTF

Thank you for your interest in improving this CTF challenge!

## How to Contribute

### Reporting Issues
- Open a GitHub issue describing the problem clearly
- Include your OS, compiler version, and Python version if relevant
- Attach any relevant error messages or screenshots

### Submitting Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes with clear, descriptive commit messages
4. Ensure all code compiles without warnings (`make all`)
5. Run the test suite: `python test/validate.py`
6. Open a pull request against `main` with a description of what you changed and why

### Code Style
- **C++**: follow the style in `CTF_2026.cpp` (K&R-ish braces, `snake_case`)
- **Python**: PEP 8, type hints where helpful, docstrings for public functions
- Keep educational comments in place – this is a learning resource

### What We Welcome
- Bug fixes in the solver or encryption tool
- Improvements to documentation and educational content
- Additional test vectors (plaintext/ciphertext pairs)
- New hint levels in `HINTS.md`
- Better Dockerfile or CI configuration

### What to Avoid
- Revealing the actual CTF flag in committed files
- Removing the intentional obfuscation layers in `encrypt_flag.cpp`
- Breaking cross-platform compatibility

## Code of Conduct
Be respectful and constructive. This project exists to help people learn reverse engineering and cryptography.
