import hashlib
from typing import List, Dict

def verify_chain(ledger: List[Dict[str, str]]) -> bool:
    """
    Validates the cryptographic integrity of the ledger chain.
    Returns True if all hashes match and the chain is unbroken.
    """
    for i in range(len(ledger) - 1):
        current_block = ledger[i]
        next_block = ledger[i + 1]
        
        # Verify link
        if current_block["prev_hash"] != next_block["hash"]:
            return False
            
        # Verify current block integrity
        payload = (
            f"{current_block['timestamp']}|{current_block['source']}|"
            f"{current_block['topic']}|{current_block['fact']}|"
            f"{current_block['image_url']}|{current_block['source_url']}|"
            f"{current_block['prev_hash']}"
        )
        if hashlib.sha256(payload.encode("utf-8")).hexdigest() != current_block["hash"]:
            return False
            
    return True