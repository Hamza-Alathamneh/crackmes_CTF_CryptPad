# Makefile for CryptPad CTF challenge
#
# Targets:
#   make all      – build both solver and encrypt tool
#   make solver   – compile the decryption solver (CTF_2026.cpp)
#   make encrypt  – compile the encryption tool (encrypt_flag.cpp)
#   make clean    – remove compiled binaries

CXX      := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra

.PHONY: all solver encrypt clean

all: solver encrypt

solver: CTF_2026.cpp
	$(CXX) $(CXXFLAGS) -o solver CTF_2026.cpp

encrypt: encrypt_flag.cpp
	$(CXX) $(CXXFLAGS) -o encrypt encrypt_flag.cpp

clean:
	rm -f solver encrypt
