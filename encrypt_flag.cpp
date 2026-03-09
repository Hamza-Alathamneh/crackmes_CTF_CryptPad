/*
 * encrypt_flag.cpp
 *
 * Encryption tool for the CryptPad CTF challenge format.
 *
 * Usage:
 *   ./encrypt <plaintext> <key> <output.enc>
 *   ./encrypt <plaintext> <key>            (writes to flag.enc)
 *   ./encrypt                              (interactive mode)
 *
 * Encryption scheme:
 *   plaintext  →  XOR(key)  →  RC4(key)  →  XOR(key)  →  ciphertext
 *   Output file: ciphertext + footer (13 bytes)
 *
 * Footer layout:
 *   [0..3]  uint32_t original plaintext length (little-endian)
 *   [4..11] 8-byte key
 *   [12]    separator byte (0x00)
 */

#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// RC4 stream cipher
// ---------------------------------------------------------------------------

class RC4 {
    vector<uint8_t> S;
    int i, j;

public:
    RC4(const vector<uint8_t>& key) : S(256), i(0), j(0) {
        for (int k = 0; k < 256; ++k) S[k] = static_cast<uint8_t>(k);
        int jk = 0;
        for (int k = 0; k < 256; ++k) {
            jk = (jk + S[k] + key[k % static_cast<int>(key.size())]) % 256;
            swap(S[k], S[jk]);
        }
    }

    vector<uint8_t> process(const vector<uint8_t>& data) {
        vector<uint8_t> out(data.size());
        for (size_t k = 0; k < data.size(); ++k) {
            i = (i + 1) % 256;
            j = (j + S[i]) % 256;
            swap(S[i], S[j]);
            uint8_t ks = S[(S[i] + S[j]) % 256];
            out[k] = data[k] ^ ks;
        }
        return out;
    }
};

// ---------------------------------------------------------------------------
// XOR helper
// ---------------------------------------------------------------------------

static void xor_inplace(vector<uint8_t>& buf, const vector<uint8_t>& key) {
    for (size_t k = 0; k < buf.size(); ++k)
        buf[k] ^= key[k % key.size()];
}

// ---------------------------------------------------------------------------
// Encryption
// ---------------------------------------------------------------------------

static vector<uint8_t> encrypt(const string& plaintext,
                                const vector<uint8_t>& key) {
    vector<uint8_t> data(plaintext.begin(), plaintext.end());

    // Layer 1: XOR
    xor_inplace(data, key);

    // Layer 2: RC4
    RC4 rc4(key);
    data = rc4.process(data);

    // Layer 3: XOR
    xor_inplace(data, key);

    return data;
}

// ---------------------------------------------------------------------------
// Build output file (ciphertext + footer)
// ---------------------------------------------------------------------------

static vector<uint8_t> build_enc_file(const vector<uint8_t>& ciphertext,
                                       const vector<uint8_t>& key,
                                       uint32_t orig_len) {
    vector<uint8_t> out(ciphertext);

    // Footer: 4-byte length (little-endian)
    out.push_back(static_cast<uint8_t>(orig_len & 0xFF));
    out.push_back(static_cast<uint8_t>((orig_len >> 8) & 0xFF));
    out.push_back(static_cast<uint8_t>((orig_len >> 16) & 0xFF));
    out.push_back(static_cast<uint8_t>((orig_len >> 24) & 0xFF));

    // Footer: 8-byte key
    for (int k = 0; k < 8; ++k)
        out.push_back(key[k % key.size()]);

    // Footer: separator byte
    out.push_back(0x00);

    return out;
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

int main(int argc, char* argv[]) {
    string plaintext;
    string key_str;
    string out_path = "flag.enc";

    if (argc >= 3) {
        plaintext = argv[1];
        key_str   = argv[2];
        if (argc >= 4) out_path = argv[3];
    } else {
        cout << "CryptPad Encryption Tool\n";
        cout << "========================\n\n";
        cout << "Enter plaintext: ";
        getline(cin, plaintext);
        cout << "Enter 8-byte key (exactly 8 characters): ";
        getline(cin, key_str);
        cout << "Output file [flag.enc]: ";
        string tmp;
        getline(cin, tmp);
        if (!tmp.empty()) out_path = tmp;
    }

    if (plaintext.empty()) {
        cerr << "[!] Plaintext must not be empty.\n";
        return 1;
    }

    // Pad or truncate key to 8 bytes
    vector<uint8_t> key(8, 0x00);
    for (size_t k = 0; k < 8 && k < key_str.size(); ++k)
        key[k] = static_cast<uint8_t>(key_str[k]);

    uint32_t orig_len = static_cast<uint32_t>(plaintext.size());

    vector<uint8_t> ciphertext = encrypt(plaintext, key);
    vector<uint8_t> file_data  = build_enc_file(ciphertext, key, orig_len);

    ofstream out(out_path, ios::binary);
    if (!out) {
        cerr << "[!] Cannot open output file: " << out_path << "\n";
        return 1;
    }
    out.write(reinterpret_cast<const char*>(file_data.data()),
              static_cast<streamsize>(file_data.size()));
    out.close();

    cout << "\n[+] Encrypted " << orig_len << " bytes → " << out_path
         << " (" << file_data.size() << " bytes total)\n";
    cout << "[+] Key (hex): ";
    for (uint8_t b : key) cout << hex << setw(2) << setfill('0') << (int)b;
    cout << dec << "\n";

    return 0;
}
