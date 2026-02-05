import os
import time
import json
import hashlib
import sqlite3
import re
import requests
from web3 import Web3
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for, session

# Import local OCR module
from local_ocr import extract_document_details

# Import hash validator for enhanced validation
from hash_validator import HashValidator

load_dotenv()

# Configuration
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-for-mvp")
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("✓ Using LOCAL OCR (PaddleOCR) - No external API dependencies!")

# Old external API functions removed - now using local OCR


def fuzzy_match(s1, s2):
    """Simple fuzzy match: checks if strings are very similar after normalization."""
    n1 = normalize_text(s1)
    n2 = normalize_text(s2)
    if not n1 or not n2: return False
    # Check if one is a substring of another or they share 80% similar length/chars
    if n1 in n2 or n2 in n1:
        return True
    return False

# Blockchain Setup (Neo X Testnet)
neoxt_url = os.getenv("WEB3_PROVIDER", "https://neoxt4seed1.ngd.network")
web3 = Web3(Web3.HTTPProvider(neoxt_url))

# Testnet Credentials (provided in original code)
FROM_ADDRESS = "0x8883bFFa42A7f5B509D0929c6fFa041e46E18e2f"
PRIVATE_KEY = "9b63cd445ab8312da178e90693290d0d2c98a334f77634013f5d8cfce60f644f"
CHAIN_ID = int(os.getenv("CHAIN_ID", 80002))
EXPLORER_URL = os.getenv("EXPLORER_URL", "https://xt4scan.ngd.network")

# NFT Contract Config
NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
NFT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "bytes32", "name": "docHash", "type": "bytes32"}
        ],
        "name": "mintCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "documentHashes",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "nextTokenId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# DB Initialization
def get_db_connection():
    conn = sqlite3.connect('document_verification.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_name TEXT,
            hackathon_name TEXT,
            document_hash TEXT,
            txn_hash TEXT,
            token_id INTEGER,
            contract_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check for missing columns in existing table (Migration)
    cursor = conn.execute('PRAGMA table_info(documents)')
    columns = [row['name'] for row in cursor.fetchall()]
    
    if 'token_id' not in columns:
        print("Migrating: Adding token_id column...")
        conn.execute('ALTER TABLE documents ADD COLUMN token_id INTEGER')
    
    if 'contract_address' not in columns:
        print("Migrating: Adding contract_address column...")
        conn.execute('ALTER TABLE documents ADD COLUMN contract_address TEXT')

    if 'issuer_address' not in columns:
        print("Migrating: Adding issuer_address column...")
        conn.execute('ALTER TABLE documents ADD COLUMN issuer_address TEXT')

    if 'document_content' not in columns:
        print("Migrating: Adding document_content column...")
        conn.execute('ALTER TABLE documents ADD COLUMN document_content TEXT')
        
    conn.commit()
    conn.close()

init_db()


def normalize_text(text):
    """Normalize text for consistent hashing."""
    if not text:
        return ""
    # Convert to string, lowercase, strip whitespace, and replace multiple spaces with single space
    text = str(text).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    # Remove non-alphanumeric characters for even more robustness (optional, but good for OCR)
    text = re.sub(r'[^a-z0-9 ]', '', text)
    return text

def calculate_hash(data):
    """
    Calculate SHA-256 hash of the entire document content.
    This creates a unique Digital Fingerprint for any document.
    """
    content = data.get("document_content", "")
    if not content:
        # Fallback for old records if needed
        keys = ["name", "hackathon_name"]
        content = "|".join([normalize_text(data.get(k, "")) for k in keys])
    
    normalized_content = normalize_text(content)
    return hashlib.sha256(normalized_content.encode()).hexdigest()

def calculate_legacy_hash(data):
    """Calculate SHA-256 hash using the old JSON method (Legacy Logic)."""
    normalized_data = {k: normalize_text(v) for k, v in data.items()}
    data_string = json.dumps(normalized_data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()

def verify_on_chain(txn_hash, expected_hash):
    """
    Robust verification that the expected hash exists in the blockchain transaction.
    Handles both legacy data anchors and contract function calls.
    """
    try:
        # 1. Fetch transaction and receipt
        receipt = web3.eth.get_transaction_receipt(txn_hash)
        if not receipt:
            return False, "Transaction not found on-chain."
        if not receipt.status:
            return False, "Transaction failed on-chain."
            
        txn = web3.eth.get_transaction(txn_hash)
        input_data = txn.input
        if isinstance(input_data, bytes):
            input_data = input_data.hex()
        
        # Clean the input data for comparison
        clean_input = input_data.lower().replace('0x', '')
        clean_expected = str(expected_hash).lower().replace('0x', '')
        
        print(f"DEBUG: Checking On-Chain. Expected: {clean_expected[:10]}... Input Length: {len(clean_input)}")
        
        # Check if the expected hash exists anywhere in the input data
        # This covers:
        # - Legacy (data is just the hash)
        # - Contract (hash is an argument, usually padded with 0s)
        if clean_expected in clean_input:
            return True, "Identity Confirmed on Neo X (Verified)"
            
        return False, "Hash not found in this transaction data."
        
    except Exception as e:
        print(f"Blockchain Verification Error: {str(e)}")
        return False, f"Protocol Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_details')
def upload_page():
    return render_template('upload.html')

@app.route('/verify')
def verify_page():
    return render_template('verify.html')

@app.route('/upload_and_issue', methods=['POST'])
def upload_and_issue():
    """OCR and Issue to Blockchain."""
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Use LOCAL OCR (PaddleOCR) - No external API calls!
        print(f"🔍 Processing document with LOCAL OCR: {filepath}")
        
        # Extract details using local OCR
        details = extract_document_details(filepath)
        doc_content = details.get("document_content", "")
        doc_title = details.get("document_title", "Untitled Document")
        
        # Allow manual override if OCR fails
        if not doc_content:
            print("⚠ OCR extraction failed or empty, checking for manual input...")
            doc_content = request.form.get('manual_content', "No content extracted.")
            doc_title = request.form.get('manual_title', "Manual Entry")
        
        print(f"✓ Document Scanned. Content length: {len(doc_content)}")

        # Calculate Digital Fingerprint
        doc_hash = calculate_hash({"document_content": doc_content})

        # 3. Blockchain Minting
        token_id = 0 # Initialize token_id
        txn_hex = None
        legacy_needed = False
        
        if NFT_CONTRACT_ADDRESS != "0x0000000000000000000000000000000000000000":
            try:
                contract = web3.eth.contract(address=NFT_CONTRACT_ADDRESS, abi=NFT_ABI)
                nonce = web3.eth.get_transaction_count(FROM_ADDRESS)
                
                # Convert hex hash to bytes32 for Solidity
                bytes_hash = web3.to_bytes(hexstr=doc_hash)
                
                txn = contract.functions.mintCertificate(FROM_ADDRESS, bytes_hash).build_transaction({
                    'chainId': CHAIN_ID,
                    'gas': 500000,
                    'gasPrice': web3.to_wei('50', 'gwei'),
                    'nonce': nonce,
                })
                
                signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
                txn_send_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                txn_hex = web3.to_hex(txn_send_hash)
                
                print(f"Waiting for receipt for TX: {txn_hex}...")
                receipt = web3.eth.wait_for_transaction_receipt(txn_send_hash, timeout=120)
                print(f"Transaction mined in block: {receipt.blockNumber}")
            except Exception as e:
                print(f"Contract Minting Error: {str(e)}. Falling back to legacy anchor...")
                legacy_needed = True
        else:
            legacy_needed = True

        if legacy_needed:
            # Legacy Data Anchor (Transaction to Null Address)
            print("Performing legacy data anchor on Neo X...")
            nonce = web3.eth.get_transaction_count(FROM_ADDRESS)
            txn = {
                'to': "0x0000000000000000000000000000000000000000",
                'value': 0,
                'gas': 500000,
                'gasPrice': web3.to_wei('50', 'gwei'),
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'data': "0x" + doc_hash
            }
            signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            txn_send_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            txn_hex = web3.to_hex(txn_send_hash)
            
            print(f"Legacy TX Sent: {txn_hex}. Waiting for receipt...")
            web3.eth.wait_for_transaction_receipt(txn_send_hash, timeout=120)
            token_id = 0 

        # 4. Store in Local DB
        conn = get_db_connection()
        conn.execute('INSERT INTO documents (participant_name, hackathon_name, document_hash, txn_hash, token_id, contract_address, issuer_address, document_content) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (doc_title, "General Document", doc_hash, txn_hex, token_id, NFT_CONTRACT_ADDRESS, FROM_ADDRESS, doc_content))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "title": doc_title,
            "hash": doc_hash,
            "txn_hash": txn_hex,
            "token_id": token_id,
            "aadhaar_data": {
                "name": details.get("name"),
                "address": details.get("address"),
                "phone": details.get("phone")
            },
            "explorer_url": EXPLORER_URL
        })

    except Exception as e:
        import traceback
        print(f"Error in {request.endpoint}:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/verify_document', methods=['POST'])
def verify_document():
    """
    Unified Verification Engine:
    - Handles ID (Fingerprint/Transaction) with or without 0x
    - Handles OCR visual scan
    - Aligns noisy OCR with backend
    """
    manual_hash = request.form.get('manual_hash', '').strip().lower()
    
    # NORMALIZE: Always strip 0x prefix if user included it
    if manual_hash.startswith('0x'):
        manual_hash = manual_hash[2:]
        
    image_present = 'image' in request.files and request.files['image'].filename != ''
    
    try:
        conn = get_db_connection()
        records = conn.execute('SELECT * FROM documents').fetchall()
        conn.close()
        
        record = None
        details = {}

        # --- PHASE 1: IDENTIFICATION ---
        
        if manual_hash:
            print(f"🔍 System Search: ID [{manual_hash[:10]}...]")
            for r in records:
                # Check both Document Fingerprint AND Blockchain Transaction Hash
                db_hash = str(r['document_hash'] or "").lower()
                db_txn = str(r['txn_hash'] or "").lower().replace('0x', '')
                
                if db_hash == manual_hash or db_txn == manual_hash:
                    record = r
                    print(f"✓ Identity Found: {r['participant_name']} (Via {'Transaction' if db_txn == manual_hash else 'Fingerprint'})")
                    break
        
        elif image_present:
            file = request.files['image']
            filepath = os.path.join(UPLOAD_FOLDER, f"verify_{int(time.time())}_{file.filename}")
            file.save(filepath)
            
            print(f"🔍 Analyzing File: {filepath}")
            details = extract_document_details(filepath)
            doc_content = details.get("document_content", "")
            doc_title = details.get("document_title", "Untitled Document")
            
            scanned_hash = calculate_hash({"document_content": doc_content})
            print(f"✓ Scanned Fingerprint: {scanned_hash[:10]}...")
            
            # Direct Match
            for r in records:
                if r['document_hash'] == scanned_hash:
                    record = r
                    break
            
            # Intelligent Alignment
            if not record:
                for r in records:
                    if fuzzy_match(r['participant_name'], doc_title):
                        record = r
                        break
        else:
            return jsonify({"error": "Provide ID or Image"}), 400

        if not record:
            # --- PHASE 1.5: BLOCKCHAIN FALLBACK ---
            # If not in DB, check if the ID itself is a valid Transaction on Neo X
            if manual_hash and len(manual_hash) >= 60:
                print(f"⚓ Protocol Check: Searching Neo X for TX {manual_hash[:10]}...")
                try:
                    # Try fetching directly from the chain
                    txn = web3.eth.get_transaction('0x' + manual_hash)
                    if txn:
                        print(f"✓ Found external transaction on-chain: {manual_hash[:10]}")
                        input_data = txn.input
                        if isinstance(input_data, bytes):
                            input_data = input_data.hex()
                        
                        # Extract potential hash from input data
                        # We look for a 64-character hex string (32 bytes)
                        match = re.search(r'[0-9a-f]{64}', input_data.lower())
                        if match:
                            detected_hash = match.group(0)
                            print(f"✓ Found document fingerprint in TX: {detected_hash[:10]}...")
                            
                            # Perform verification logic
                            blockchain_verified, bc_msg = verify_on_chain('0x' + manual_hash, detected_hash)
                            
                            return jsonify({
                                "status": "verified" if blockchain_verified else "failed",
                                "message": f"Global Chain Match: {bc_msg}",
                                "data": {
                                    "title": "Verified Protocol Record",
                                    "txn_hash": '0x' + manual_hash,
                                    "hash": detected_hash,
                                    "issuer_address": txn['from'],
                                    "aadhaar_data": {
                                        "name": "On-Chain Verified",
                                        "address": "Refer to Transaction Log",
                                        "phone": "N/A"
                                    },
                                    "blockchain_status": bc_msg,
                                    "explorer_url": EXPLORER_URL
                                }
                            })
                except Exception as e:
                    print(f"Blockchain fallback failed: {e}")

            return jsonify({
                "status": "not_found",
                "message": "No matching record found in our database or on-chain.",
                "data": {"blockchain_status": "Search Exhausted"}
            })

        # --- PHASE 2: BLOCKCHAIN PROOF ---
        
        stored_hash = record['document_hash']
        txn_hash = record['txn_hash']
        
        print(f"⚓ Checking Neo X: TX {txn_hash[:10]}...")
        blockchain_verified, bc_msg = verify_on_chain(txn_hash, stored_hash)
        
        # --- PHASE 3: RESPONSE ---
        
        return jsonify({
            "status": "verified" if blockchain_verified else "failed",
            "message": f"Global Document Verification: {bc_msg}",
            "data": {
                "title": record['participant_name'],
                "txn_hash": txn_hash,
                "hash": stored_hash,
                "issuer_address": record['issuer_address'] if 'issuer_address' in record.keys() else None,
                "aadhaar_data": {
                    "name": details.get("name", record['participant_name']),
                    "address": details.get("address", "Refer to On-Chain Proof"),
                    "phone": details.get("phone", "N/A")
                },
                "blockchain_status": bc_msg,
                "explorer_url": EXPLORER_URL
            }
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def history():
    conn = get_db_connection()
    docs = conn.execute('SELECT * FROM documents ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('history.html', documents=docs, explorer_url=EXPLORER_URL)

# ============================================================
# NEW: Enhanced Hash Validation & Database Query Endpoints
# ============================================================

@app.route('/api/validate_hash', methods=['POST'])
def api_validate_hash():
    """API endpoint to validate a document hash"""
    try:
        data = request.get_json()
        document_hash = data.get('hash', '').strip()
        validator = HashValidator()
        is_valid, details = validator.validate_hash(document_hash)
        return jsonify({"valid": is_valid, "details": details})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/api/validate_hash/<hash_value>', methods=['GET'])
def api_validate_hash_get(hash_value):
    """GET endpoint to validate a hash via URL parameter"""
    try:
        validator = HashValidator()
        is_valid, details = validator.validate_hash(hash_value)
        return jsonify({"valid": is_valid, "details": details})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def api_statistics():
    """Get database statistics"""
    try:
        validator = HashValidator()
        return jsonify(validator.get_statistics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/all_hashes', methods=['GET'])
def api_all_hashes():
    """Get all document hashes in the database"""
    try:
        validator = HashValidator()
        hashes = validator.get_all_hashes()
        return jsonify({"count": len(hashes), "hashes": hashes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/name/<name>', methods=['GET'])
def api_search_by_name(name):
    """Search documents by participant name"""
    try:
        validator = HashValidator()
        results = validator.search_by_name(name)
        return jsonify({"count": len(results), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/event/<event>', methods=['GET'])
def api_search_by_event(event):
    """Search documents by event name"""
    try:
        validator = HashValidator()
        results = validator.search_by_event(event)
        return jsonify({"count": len(results), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transaction/<txn_hash>', methods=['GET'])
def api_get_transaction(txn_hash):
    """Get document details by transaction hash"""
    try:
        validator = HashValidator()
        details = validator.get_transaction_details(txn_hash)
        return jsonify({"found": bool(details), "details": details})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check_hash', methods=['GET'])
def api_check_hash_simple():
    """Simple hash check via query parameter"""
    try:
        document_hash = request.args.get('hash', '').strip()
        if not document_hash:
            return jsonify({"error": "No hash provided"}), 400
        validator = HashValidator()
        is_valid, details = validator.validate_hash(document_hash)
        if is_valid:
            return jsonify({
                "authentic": True,
                "message": "✓ Document AUTHENTIC",
                "participant": details.get('participant_name'),
                "event": details.get('hackathon_name'),
                "issued": details.get('timestamp')
            })
        return jsonify({"authentic": False, "message": "✗ Hash NOT FOUND"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)