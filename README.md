# 🛡️ VeriChain: Anti-Counterfeit Blockchain Protocol

**VeriChain** is a state-of-the-art brand protection and product authenticity platform. It leverages **AI-driven Vision (PaddleOCR)** and the **Neo X Blockchain** to create an immutable, decentralized registry for luxury goods, electronics, and high-value shipments.

![VeriChain Banner](https://img.shields.io/badge/Status-Live_on_Neo_X_Testnet-magenta?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Built_With-Python_|_Flask_|_Web3.py_|_PaddleOCR-blue?style=for-the-badge)

---

## 🚀 The Problem
Global trade loses over **$500 Billion annually** to counterfeit products. Existing serial numbers and QR codes are easily duplicated, and centralized databases are vulnerable to hacking or internal tampering.

## 💡 The Solution
VeriChain provides a **Double-Bind Verification** system:
1.  **AI Visual Fingerprinting**: Instead of relying on a simple serial number, we scan the entire product label/invoice. Our AI extracts invisible patterns and technical specs to generate a unique **SHA-256 Fingerprint**.
2.  **On-Chain Anchoring**: This fingerprint is anchored to the **Neo X Blockchain**. Once registered, it is impossible for a counterfeiter to "insert" a fake record into the history.

---

## ✨ Key Features

### 🔍 AI Laser Scanner UI
A premium, cyber-security-focused interface featuring a dynamic laser scanning animation for real-time authenticity analysis.

### 🧠 Intelligent OCR Registry
Powered by **PaddleOCR** with specialized logic to detect:
*   Manufacturer & Brand Owners
*   Unique Product IDs (S/N)
*   Manufacturing (MFG) & Batch Data
*   Tamper-evident label markers

### ⛓️ Global Authenticity Check (Protocol 2.0)
The system doesn't just check a local database; it performs a **Global Protocol Scan**. If a product was registered by an official brand owner anywhere in the world, our protocol pulls the proof directly from the Neo X distributed ledger.

### 🏛️ Immutable Ledger
A transparent, searchable record of every genuine product issued, ensuring supply chain visibility from the factory to the consumer.

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.12 + Flask
*   **Blockchain**: Neo X Testnet (EVM-compatible)
*   **OCR Engine**: PaddleOCR (with Angle Classification)
*   **Smart Contracts**: Solidity (Standard NFT/Anchor Architecture)
*   **Database**: SQLite (Local Indexer)
*   **Frontend**: Vanilla JS + CSS (Glassmorphism & Cyberpunk Design System)

---

## � Getting Started

### Prerequisites
*   Python 3.12+
*   Neo X Testnet Wallet (MetaMask)
*   PaddleOCR Dependencies

### Installation
1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/Muruga-2007/ORC-1.git
    cd ORC-1/verichain
    ```

2.  **Environment Setup**:
    Create a `.env` file:
    ```env
    FLASK_SECRET_KEY=your_secret_key
    WEB3_PROVIDER=https://testnet.rpc.banelabs.org
    PRIVATE_KEY=your_neo_x_private_key
    NFT_CONTRACT_ADDRESS=your_deployed_contract
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Protocol**:
    ```bash
    python app.py
    ```

---

## 🗺️ Roadmap
- [ ] Mobile App with NFC/AR label scanning
- [ ] Integration with major ERP systems (SAP/Oracle)
- [ ] Zero-Knowledge Proofs for private supply chains
- [ ] Batch-verification for logistics hubs

---

## � License
Internal Development - VeriChain Protocol 2026.

---
*Built for the future of authentic commerce.*
