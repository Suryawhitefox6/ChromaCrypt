# Hybrid Cryptographic Framework for Image Security

## Overview

This project enhances image security by developing a hybrid cryptographic framework that combines **XChaCha20**, **Salsa20**, and **BLAKE2b-256** algorithms. The framework ensures the **confidentiality**, **integrity**, and **authenticity** of digital images.

## Key Features

- **Robust Encryption with XChaCha20:**
  - High-strength encryption.
  - Extended nonce for improved resistance against nonce reuse attacks.

- **High-Speed Stream Encryption with Salsa20:**
  - Lightweight and fast.
  - Suitable for encrypting large image files efficiently.

- **Integrity Verification with BLAKE2b-256:**
  - Fast cryptographic hashing.
  - Ensures data authenticity and detects unauthorized modifications.

## How It Works

1. **Encryption:**
   - The image is first encrypted using the **XChaCha20** algorithm for robust protection.
   - For efficiency on large files, **Salsa20** is utilized to enhance encryption speed.

2. **Integrity Check:**
   - After encryption, a **BLAKE2b-256** hash of the encrypted image is generated.
   - This hash is used to verify the authenticity and integrity of the image during decryption.

3. **Decryption:**
   - Upon receiving the encrypted image, the framework first verifies the hash.
   - If the hash matches, the image is decrypted using the same combination of XChaCha20 and Salsa20.

## Project Structure


├── encrypt.py        # Script for encryption
├── decrypt.py        # Script for decryption and integrity verification
├── utils.py          # Helper functions for encryption, decryption, and hashing
├── README.md         # Project documentation

## Requirements

- Python 3.8+

### Libraries

- cryptography
- pynacl
- hashlib

You can install the required packages with:

pip install cryptography pynacl
