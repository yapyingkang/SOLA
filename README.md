# SOLA
# SG Online Library Application (SOLA)

## Overview
The SG Online Library Application (SOLA) is a modern library management system designed to replace paper-based processes in school libraries. By digitizing library operations, SOLA simplifies book borrowing, returning, user management, and fine tracking with enterprise-grade security.

## Features
- User registration and authentication with secure password hashing
- Book catalogue management including search and status tracking
- Borrowing and returning books with borrowing limits enforced
- Fine calculation and payment management
- Comprehensive borrower and item management for administrators
- Uses symmetric encryption (Fernet) to protect sensitive data in transit and at rest

## Security
SOLA implements strong data security principles:
- Sensitive files (e.g., user data CSVs) are encrypted locally using the cryptography library’s Fernet symmetric encryption
- Encryption keys are generated once, stored securely in a key file, and must be kept private
- Data in transit is protected by encrypting payloads before sending over the network

## Installation
- Requires Python 3.x and the `cryptography` library
- Install dependencies: `pip install cryptography`
- Ensure `secret.key` is generated on first run or provide your own securely

## Usage
- Use the provided `FileEncryption` class in `encryption_helper.py` to encrypt/decrypt sensitive files
- Run the main program (`Main.py`) to interact with the system via command line interface (CLI)
- Follow prompts for borrowing, returning, user management, and admin tasks

## Important Notes
- Never commit your `secret.key` or any unencrypted sensitive data files to public repositories
- Add `secret.key` and sensitive files to `.gitignore` to prevent accidental exposure
- Keep backups of your encryption key securely outside of the repository

 Note About Databases

For security, demo releases, SOLA do NOT include real database files  (CatalogueItems.csv, etc.). 
Please create your own data files or follow instructions in the README to initialize sample data.

## Contribution
Contributions are welcome via pull requests. Please adhere to security best practices when handling sensitive data.


