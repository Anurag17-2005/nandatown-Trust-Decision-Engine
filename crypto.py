"""
Cryptographic operations for Trust Decision Engine
Ed25519 signing and verification
"""
import nacl.signing
import nacl.encoding
import hashlib
import json
from typing import Tuple


def generate_keypair() -> Tuple[str, str]:
    """Generate Ed25519 keypair for TDE service"""
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    
    private_key = signing_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
    public_key = verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
    
    return private_key, public_key


def sign_message(message: dict, private_key_b64: str) -> str:
    """Sign a message with Ed25519 private key"""
    # Canonical JSON representation
    message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
    
    # Decode private key
    signing_key = nacl.signing.SigningKey(
        private_key_b64.encode('utf-8'),
        encoder=nacl.encoding.Base64Encoder
    )
    
    # Sign
    signed = signing_key.sign(message_bytes)
    signature = signed.signature
    
    return nacl.encoding.Base64Encoder.encode(signature).decode('utf-8')


def verify_signature(message: dict, signature_b64: str, public_key_b64: str) -> bool:
    """Verify Ed25519 signature"""
    try:
        # Canonical JSON representation
        message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
        
        # Decode public key and signature
        verify_key = nacl.signing.VerifyKey(
            public_key_b64.encode('utf-8'),
            encoder=nacl.encoding.Base64Encoder
        )
        signature = nacl.encoding.Base64Encoder.decode(signature_b64.encode('utf-8'))
        
        # Verify
        verify_key.verify(message_bytes, signature)
        return True
    except Exception:
        return False


def hash_data(data: dict) -> str:
    """SHA256 hash of canonical JSON"""
    data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    return "sha256:" + hashlib.sha256(data_bytes).hexdigest()


def pubkey_to_did(public_key_b64: str) -> str:
    """Convert Ed25519 public key to did:key format"""
    # Simplified DID key format for demo
    return f"did:key:z6Mk{public_key_b64[:20]}"


def extract_pubkey_from_did(did: str) -> str:
    """Extract public key from did:key (simplified)"""
    # In production, properly decode multibase/multicodec
    # For demo, we'll use a mapping or registry
    return did.replace("did:key:z6Mk", "")
