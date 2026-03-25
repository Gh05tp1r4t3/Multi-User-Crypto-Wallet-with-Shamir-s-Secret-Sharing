# 🔐 Multi-User Crypto Wallet

A secure, multi-user cryptocurrency wallet application built with Python and Tkinter, implementing **Shamir's Secret Sharing** scheme for distributed key management. Developed as an Information Security project.

## 📋 Overview

This application allows multiple users to collaboratively control a crypto wallet using threshold-based secret sharing. No single user owns the full private key — instead, the secret is split into shares, and only a defined minimum number of shares (`k`) are required to recover the wallet.

## ✨ Features

- **Shamir's Secret Sharing** — Cryptographically split a wallet's secret key among `n` users, requiring `k` shares to recover
- **Multi-User Wallet Creation** — Define any number of users (`n`) and a recovery threshold (`k ≤ n`)
- **Wallet Recovery** — Reconstruct the wallet using at least `k` valid user shares
- **Transaction System** — Send funds between wallets with balance validation
- **Transaction History** — View a timestamped log of all wallet transactions
- **Local Persistence** — Wallet data stored securely as JSON files
- **Modern GUI** — Clean Tkinter interface with styled buttons and card layouts

## 🛠️ Requirements

- Python 3.8 or higher
- No external libraries required (uses Python standard library only)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/multi-user-crypto-wallet.git
cd multi-user-crypto-wallet
```

### 2. Run the Application

```bash
python Multi-User Crypto Wallet with Shamir's Secret Sharing.py
```

> **Note:** No additional packages need to be installed. The app uses only Python built-in modules (`tkinter`, `secrets`, `json`, `os`, `time`, `random`, `functools`).

## 📖 How to Use

### Creating a New Wallet
1. Launch the app and click **"Generate New Wallet"**
2. Enter a unique **Wallet ID**
3. Set the total number of users (`n`) and the minimum recovery threshold (`k`)
4. Enter comma-separated **usernames** (must match count `n`)
5. Click **"Generate Wallet"** — the app will display each user's secret share
6. **Save each share securely** — they are needed for wallet recovery

### Recovering a Wallet
1. Click **"Recover Existing Wallet"** from the main menu
2. Enter the **Wallet ID**
3. Provide at least `k` valid username + share pairs
4. Click **"Recover Wallet"** to access the wallet

### Sending a Transaction
1. After recovering a wallet, click **"Send Transaction"**
2. Enter the **Receiver Wallet ID** and the **Amount**
3. Confirm the transaction — balances update immediately

## 🔐 Security Concepts

| Concept | Description |
|---|---|
| Shamir's Secret Sharing | A cryptographic scheme where a secret is divided into parts (shares). Only `k` of `n` shares can reconstruct the original secret. |
| Threshold Cryptography | Requires a minimum number of participants to perform operations, preventing single points of failure. |
| Lagrange Interpolation | The mathematical basis used to reconstruct the secret polynomial at point `0`. |

## 📁 Project Structure

```
multi-user-crypto-wallet/
├── Multi-User Crypto Wallet with Shamir's Secret Sharing.py   # Main application source code
├── README.md                                                  # Project documentation
├── requirements.txt                                           # Dependencies (standard library only)
├── .gitignore                                                 # Git ignore rules
└── LICENSE                                                    # MIT License
```

> **Runtime files** (`wallet_*.json`, `users.json`) are generated when wallets are created and are excluded from version control via `.gitignore`.


## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
