"""
Receipt validation logic - ported from PR #133
Validates NandaTown structured receipts
"""
from typing import Dict, Any, List, Tuple
from models import Receipt, Corroboration
import crypto
import time


class ValidationResult:
    def __init__(self):
        self.valid = True
        self.signature_valid = False
        self.issuer_resolvable = True
        self.corroborated = False
        self.corroboration_count = 0
        self.warnings: List[str] = []
        self.receipt_hash = ""


def validate_receipt(receipt: Receipt) -> ValidationResult:
    """
    Validate a NandaTown structured receipt
    Checks: signature, timestamp, corroborations
    """
    result = ValidationResult()
    
    # 1. Validate signature
    try:
        # Reconstruct message that was signed
        message = {
            "issuer_did": receipt.issuer_did,
            "subject_id": receipt.subject_id,
            "claim": receipt.claim,
            "timestamp": receipt.timestamp
        }
        
        # Extract public key from DID (simplified - in prod use DID resolver)
        # For demo, we'll assume signature is valid if format is correct
        if len(receipt.signature) > 20:  # Basic format check
            result.signature_valid = True
        else:
            result.valid = False
            result.warnings.append("Invalid signature format")
            
    except Exception as e:
        result.valid = False
        result.signature_valid = False
        result.warnings.append(f"Signature verification failed: {str(e)}")
    
    # 2. Check timestamp (not too old, not in future)
    current_time = int(time.time())
    if receipt.timestamp > current_time + 300:  # 5 min future tolerance
        result.warnings.append("Receipt timestamp is in the future")
        result.valid = False
    
    if receipt.timestamp < current_time - (86400 * 365):  # 1 year old
        result.warnings.append("Receipt is very old (>1 year)")
    
    # 3. Validate corroborations
    if receipt.corroborations:
        valid_corroborations = 0
        for corr in receipt.corroborations:
            try:
                # In production, verify each corroboration signature
                if len(corr.signature) > 20 and corr.cosigner_did.startswith("did:"):
                    valid_corroborations += 1
            except Exception:
                pass
        
        result.corroboration_count = valid_corroborations
        result.corroborated = valid_corroborations > 0
    
    # 4. Compute receipt hash
    receipt_dict = receipt.model_dump()
    result.receipt_hash = crypto.hash_data(receipt_dict)
    
    return result


def verify_receipt_signature(receipt: Receipt) -> bool:
    """
    Verify the Ed25519 signature on a receipt
    For demo purposes, simplified validation
    """
    # In production: use DID resolver to get issuer's public key
    # then verify signature with crypto.verify_signature()
    
    # Demo: basic format checks
    if not receipt.signature or len(receipt.signature) < 20:
        return False
    
    if not receipt.issuer_did.startswith("did:"):
        return False
    
    return True


def check_corroborations(receipt: Receipt) -> int:
    """Count valid corroborations"""
    if not receipt.corroborations:
        return 0
    
    count = 0
    for corr in receipt.corroborations:
        if corr.cosigner_did.startswith("did:") and len(corr.signature) > 20:
            count += 1
    
    return count
