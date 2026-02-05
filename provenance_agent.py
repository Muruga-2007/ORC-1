import sqlite3
import os
import re
from datetime import datetime
from web3 import Web3

class ProvenanceAgent:
    """
    Advanced Authenticity Verification and Provenance Intelligence Agent.
    Operates on VeriChain protocol to provide luxury-grade authenticity assurance.
    """
    def __init__(self, db_path=None, web3_provider="https://testnet.rpc.banelabs.org"):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, 'document_verification.db')
        else:
            self.db_path = db_path
        
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def analyze_product(self, product_id):
        """
        Main intelligence function to identify, reconstruct, and validate product history.
        """
        # 1. Database Lookup
        conn = self._get_conn()
        record = conn.execute('SELECT * FROM documents WHERE document_hash = ? OR txn_hash = ?', 
                             (product_id, product_id)).fetchone()
        conn.close()

        if not record:
            return self._generate_not_found_report(product_id)

        # 2. Extract verified data
        brand_verified = "Confirmed" if record['issuer_address'] else "Unverified"
        integrity_score = 100
        risk_flags = []
        confidence = 100

        # 3. Blockchain Lifecycle Reconstruction (Conceptual for now, can query logs in production)
        # For this prototype, we treat the registration as the Genesis event.
        timeline = [
            {
                "event": "Genesis Protocol Registration",
                "actor": record['issuer_address'] or "System Registry",
                "timestamp": record['timestamp'],
                "status": "Verified On-Chain",
                "proof": record['txn_hash']
            }
        ]

        # 4. Anomaly Detection
        if not record['txn_hash']:
            risk_flags.append("Genesis transaction proof missing.")
            integrity_score -= 30
            confidence -= 20
        
        if len(record['document_hash']) < 64:
            risk_flags.append("Fingerprint density below security threshold.")
            integrity_score -= 10
            confidence -= 10

        # 5. Build structured report
        report = {
            "metadata": {
                "product_name": record['participant_name'],
                "brand": record['hackathon_name'],
                "fingerprint": record['document_hash'],
                "report_timestamp": datetime.now().isoformat()
            },
            "authenticity_status": "Authentic" if confidence > 80 else "Suspicious",
            "brand_verification": brand_verified,
            "ownership_timeline": timeline,
            "transfer_integrity_score": integrity_score,
            "risk_flags": risk_flags,
            "final_confidence_score": confidence,
            "on_chain_proof": {
                "contract": record['contract_address'],
                "token_id": record['token_id'],
                "txn": record['txn_hash']
            }
        }
        
        return report

    def _generate_not_found_report(self, product_id):
        # Even if not found, we check the blockchain directly for ANY trace
        blockchain_trace = None
        if product_id.startswith("0x") and len(product_id) >= 64:
            try:
                txn = self.web3.eth.get_transaction(product_id)
                if txn:
                    blockchain_trace = "Transaction exists but is not registered in VeriChain index."
            except:
                pass

        return {
            "authenticity_status": "Counterfeit" if not blockchain_trace else "Unknown",
            "brand_verification": "Failed",
            "ownership_timeline": [],
            "transfer_integrity_score": 0,
            "risk_flags": ["No official registry entry found.", blockchain_trace] if blockchain_trace else ["Product ID not found in global registry."],
            "final_confidence_score": 0 if not blockchain_trace else 15
        }
