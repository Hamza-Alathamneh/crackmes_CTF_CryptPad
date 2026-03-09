# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.0] - 2026-03-09

### Added
- `decrypt_flag.py` – cross-platform Python implementation of the solver
- `encrypt_flag.cpp` – C++ tool to create new encrypted challenges
- `Makefile` – easy `make solver`, `make encrypt`, `make all`, `make clean` targets
- `Dockerfile` – containerised build and run environment
- `SOLUTION.md` – detailed reverse-engineering writeup
- `HINTS.md` – progressive hints for solvers
- `CONTRIBUTING.md` – contributor guidelines
- `LICENSE` – MIT licence
- `requirements.txt` – Python dependency list (stdlib only)
- `docs/RC4_EXPLAINED.md` – educational RC4 algorithm walkthrough
- `docs/REVERSE_ENGINEERING_GUIDE.md` – step-by-step RE methodology
- `docs/BINARY_ANALYSIS.md` – guide to analysing `cryptpad.exe`
- `test/` – sample test cases and a validation script
- `.github/workflows/build.yml` – CI/CD pipeline (Ubuntu + Windows)

### Changed
- Fixed hardcoded absolute path `/home/hamza/Desktop/HTB/Crackmes/flag.enc` in
  `CTF_2026.cpp` to the portable relative path `flag.enc`
- Added `.gitignore` to exclude build artefacts and IDE folders

## [1.1.0] - 2026-03-08

### Added
- Updated `README.md` with professional formatting, solution documentation,
  encryption-scheme analysis, and step-by-step decryption instructions

## [1.0.0] - 2026

### Added
- Initial release: `cryptpad.exe` binary challenge
- `CTF_2026.cpp` C++ decryption solution
- `flag.enc` encrypted flag file (64 bytes)
- `README.md` basic project description
