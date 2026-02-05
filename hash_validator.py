"""
Hash Validation Module
Provides comprehensive hash validation against database and blockchain
"""

import sqlite3
from typing import Dict, Optional, Tuple

class HashValidator:
    """
    Validates document hashes against the database and blockchain
    """
    
    def __init__(self, db_path='document_verification.db'):
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def validate_hash(self, document_hash: str) -> Tuple[bool, Dict]:
        """
        Validate a document hash against the database
        
        Args:
            document_hash: The SHA-256 hash to validate
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        try:
            # Normalize hash: Remove '0x' if present and lowercase
            document_hash = document_hash.strip().lower()
            if document_hash.startswith('0x'):
                document_hash = document_hash[2:]

            conn = self.get_db_connection()
            
            # Search for exact hash match
            record = conn.execute(
                'SELECT * FROM documents WHERE document_hash = ?',
                (document_hash,)
            ).fetchone()
            
            conn.close()
            
            if record:
                return True, {
                    'id': record['id'],
                    'participant_name': record['participant_name'],
                    'hackathon_name': record['hackathon_name'],
                    'document_hash': record['document_hash'],
                    'txn_hash': record['txn_hash'],
                    'token_id': record['token_id'],
                    'contract_address': record['contract_address'],
                    'issuer_address': record['issuer_address'],
                    'timestamp': record['timestamp'],
                    'status': 'AUTHENTIC',
                    'message': 'This document hash exists in our database and is authentic.'
                }
            else:
                return False, {
                    'status': 'NOT_FOUND',
                    'message': 'This hash was never issued by our system. Document may be fraudulent.',
                    'document_hash': document_hash
                }
        
        except Exception as e:
            return False, {
                'status': 'ERROR',
                'message': f'Validation error: {str(e)}',
                'document_hash': document_hash
            }
    
    def get_all_hashes(self) -> list:
        """
        Get all document hashes from the database
        
        Returns:
            List of all document hashes
        """
        try:
            conn = self.get_db_connection()
            records = conn.execute(
                'SELECT document_hash, participant_name, hackathon_name, timestamp FROM documents ORDER BY timestamp DESC'
            ).fetchall()
            conn.close()
            
            return [dict(r) for r in records]
        
        except Exception as e:
            print(f"Error fetching hashes: {e}")
            return []
    
    def get_transaction_details(self, txn_hash: str) -> Optional[Dict]:
        """
        Get document details by transaction hash
        
        Args:
            txn_hash: The blockchain transaction hash
        
        Returns:
            Document details or None
        """
        try:
            conn = self.get_db_connection()
            record = conn.execute(
                'SELECT * FROM documents WHERE txn_hash = ?',
                (txn_hash,)
            ).fetchone()
            conn.close()
            
            if record:
                return dict(record)
            return None
        
        except Exception as e:
            print(f"Error fetching transaction: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            conn = self.get_db_connection()
            
            total_docs = conn.execute('SELECT COUNT(*) as count FROM documents').fetchone()['count']
            
            unique_participants = conn.execute(
                'SELECT COUNT(DISTINCT participant_name) as count FROM documents'
            ).fetchone()['count']
            
            unique_events = conn.execute(
                'SELECT COUNT(DISTINCT hackathon_name) as count FROM documents'
            ).fetchone()['count']
            
            recent_docs = conn.execute(
                'SELECT * FROM documents ORDER BY timestamp DESC LIMIT 5'
            ).fetchall()
            
            conn.close()
            
            return {
                'total_documents': total_docs,
                'unique_participants': unique_participants,
                'unique_events': unique_events,
                'recent_documents': [dict(r) for r in recent_docs]
            }
        
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_documents': 0,
                'unique_participants': 0,
                'unique_events': 0,
                'recent_documents': []
            }
    
    def search_by_name(self, name: str) -> list:
        """
        Search documents by participant name
        
        Args:
            name: Participant name to search
        
        Returns:
            List of matching documents
        """
        try:
            conn = self.get_db_connection()
            records = conn.execute(
                'SELECT * FROM documents WHERE participant_name LIKE ? ORDER BY timestamp DESC',
                (f'%{name}%',)
            ).fetchall()
            conn.close()
            
            return [dict(r) for r in records]
        
        except Exception as e:
            print(f"Error searching by name: {e}")
            return []
    
    def search_by_event(self, event: str) -> list:
        """
        Search documents by event/hackathon name
        
        Args:
            event: Event name to search
        
        Returns:
            List of matching documents
        """
        try:
            conn = self.get_db_connection()
            records = conn.execute(
                'SELECT * FROM documents WHERE hackathon_name LIKE ? ORDER BY timestamp DESC',
                (f'%{event}%',)
            ).fetchall()
            conn.close()
            
            return [dict(r) for r in records]
        
        except Exception as e:
            print(f"Error searching by event: {e}")
            return []


# Convenience function
def quick_validate(document_hash: str) -> Tuple[bool, Dict]:
    """
    Quick validation function
    
    Args:
        document_hash: Hash to validate
    
    Returns:
        Tuple of (is_valid, details)
    """
    validator = HashValidator()
    return validator.validate_hash(document_hash)


if __name__ == "__main__":
    # Test the validator
    import sys
    
    validator = HashValidator()
    
    if len(sys.argv) > 1:
        test_hash = sys.argv[1]
        print(f"Validating hash: {test_hash}")
        is_valid, details = validator.validate_hash(test_hash)
        
        print(f"\nValid: {is_valid}")
        print(f"Details: {details}")
    else:
        # Show statistics
        stats = validator.get_statistics()
        print("Database Statistics:")
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Unique Participants: {stats['unique_participants']}")
        print(f"Unique Events: {stats['unique_events']}")
        
        if stats['recent_documents']:
            print("\nRecent Documents:")
            for doc in stats['recent_documents']:
                print(f"  - {doc['participant_name']} @ {doc['hackathon_name']} ({doc['timestamp']})")
