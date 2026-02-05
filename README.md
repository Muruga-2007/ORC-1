# VeriChain: Anti-Counterfeit Blockchain Protocol 🛡️

VeriChain is a next-generation brand protection platform that eliminates counterfeit products through AI-driven OCR and immutable blockchain indexing on the Neo X network.

## 🚀 Overview

VeriChain provides a dual-layer security protocol for manufacturers and consumers:
1.  **Brand Protection**: Manufacturers register unique product fingerprints (labels, serial numbers, technical specs) by anchoring them to the Neo X blockchain.
2.  **Consumer Verification**: Customers can scan product labels using their smartphones to instantly verify authenticity against the global immutable ledger.

## ✨ Key Features

-   **AI-Powered Vision Engine**: Leverages PaddleOCR for high-precision extraction of Brand names, Serial numbers (S/N), and Manufacturing dates.
-   **Immutable Digital Fingerprints**: Every product identity is hashed (SHA-256) and anchored to the Neo X Testnet.
-   **Global Protocol Scan**: Direct blockchain fallback check that allows verification even if the local database record is missing.
-   **Cyber-Security UI**: A premium, responsive interface featuring dynamic laser-scan animations and a real-time supply chain ledger.
-   **Zero-Gas Optimization**: Built using legacy data-anchoring techniques to minimize transaction costs while maintaining security.

## 🛠️ Tech Stack

-   **Backend**: Python 3.12, Flask
-   **Blockchain**: Web3.py, Neo X Testnet (Chain ID: 80002)
-   **AI/OCR**: PaddleOCR, OpenCV
-   **Database**: SQLite3 (Local Asset Registry)
-   **Frontend**: Vanilla HTML5, Modern CSS Modern, JavaScript (ES6+)

## 📦 Installation

### 1. Prerequisites
- Python 3.12+
- Node.js (Optional, for frontend assets)
- Tesseract (Fallback OCR)

### 2. Clone the Repository
```bash
git clone https://github.com/Muruga-2007/ORC-1.git
cd ORC-1
```

### 3. Setup Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Create a `.env` file in the root directory:
```env
FLASK_SECRET_KEY=your_secret_key
WEB3_PROVIDER=https://neoxt4seed1.ngd.network  # Neo X Testnet
NFT_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...
EXPLORER_URL=https://xt4scan.ngd.network
```

## 🚦 Usage Guide

### Registering a Brand Product
1.  Navigate to **Register Product**.
2.  Upload a clear image of the product label or technical invoice.
3.  The AI will extract the Serial Number and Brand information.
4.  Click **Register on Blockchain** to mint the immutable fingerprint.

### Scanning for Authenticity
1.  Navigate to **Scan for Authenticity**.
2.  Paste the **Digital Fingerprint ID** or upload a photo of the product you just purchased.
3.  The laser scanner will analyze the markers.
4.  If the fingerprint matches the blockchain record, it will display **✅ GENUINE PRODUCT**. Otherwise, it will flag it as **⚠️ COUNTERFEIT**.

## 🛡️ Security Protocol
VeriChain uses a triple-check validation system:
1.  **Local Match**: Check against the manufacturer's local database.
2.  **Chain Match**: Verify the `document_hash` exists on Neo X.
3.  **Owner Proof**: Confirm the transaction was initiated by the official brand wallet address.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**VeriChain - Securing the Global Supply Chain.**
