#!/usr/bin/env python3
"""
Offline Verification Demo
Demonstrates how other services can verify TDE decisions without network calls
"""
import json
import nacl.signing
import nacl.encoding
import requests
import sys


def verify_tde_decision_offline(response_json, tde_pubkey):
    """
    Verify TDE's signed decision without making network calls
    
    Args:
        response_json: The complete response from /decide or /validate-receipt
        tde_pubkey: TDE's public key (Base64 encoded)
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        vr = response_json['verification_receipt']
        
        # Reconstruct the message that was signed
        message = {
            'input_hash': vr['input_hash'],
            'verdict': vr['verdict'],
            'issued_at': vr['issued_at']
        }
        message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
        
        # Decode TDE's public key
        verify_key = nacl.signing.VerifyKey(
            tde_pubkey.encode('utf-8'),
            encoder=nacl.encoding.Base64Encoder
        )
        
        # Decode signature
        signature = nacl.encoding.Base64Encoder.decode(vr['signature'].encode('utf-8'))
        
        # Verify signature
        verify_key.verify(message_bytes, signature)
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return False


def demo_workflow():
    """
    Complete demo: Call TDE, get decision, verify offline
    """
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Trust Decision Engine - Offline Verification Demo")
    print("=" * 60)
    print()
    
    # Step 1: Get TDE's public key
    print("Step 1: Getting TDE's public key...")
    pubkey_response = requests.get(f"{base_url}/pubkey")
    pubkey_data = pubkey_response.json()
    tde_pubkey = pubkey_data['public_key']
    tde_did = pubkey_data['did']
    
    print(f"✓ TDE Public Key: {tde_pubkey[:20]}...")
    print(f"✓ TDE DID: {tde_did}")
    print()
    
    # Step 2: Make a decision request
    print("Step 2: Requesting trust decision...")
    decision_request = {
        "receipt": {
            "issuer_did": "did:key:z6MkhaXgBZDvotDk",
            "subject_id": "agent-demo",
            "claim": "delivered_goods",
            "timestamp": 1752200000,
            "signature": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=",
            "corroborations": [
                {
                    "cosigner_did": "did:key:z6MkCosigner1",
                    "signature": "Y29zaWduZXIxc2lnbmF0dXJl"
                }
            ]
        },
        "action": "pay_supplier"
    }
    
    decision_response = requests.post(
        f"{base_url}/decide",
        json=decision_request
    )
    decision_data = decision_response.json()
    
    print(f"✓ Risk: {decision_data['risk']}")
    print(f"✓ Recommendation: {decision_data['recommendation']}")
    print(f"✓ Issuer Reputation: {decision_data['issuer_reputation']:.2f}")
    print(f"✓ Reason: {decision_data['reason']}")
    print()
    
    # Step 3: Verify the decision offline
    print("Step 3: Verifying decision signature (OFFLINE)...")
    print("   (No network call - verifying cryptographically)")
    
    is_valid = verify_tde_decision_offline(decision_data, tde_pubkey)
    
    if is_valid:
        print("✓ Signature VALID - TDE definitely issued this decision")
        print("✓ Decision can be trusted without calling TDE again")
    else:
        print("✗ Signature INVALID - Decision may be tampered!")
        return False
    
    print()
    
    # Step 4: Show how this prevents tampering
    print("Step 4: Demonstrating tampering detection...")
    import copy
    tampered_data = copy.deepcopy(decision_data)
    # Tamper with the signed verdict (the part that's actually verified)
    tampered_data['verification_receipt']['verdict']['recommendation'] = 'ACCEPT'
    
    print("   Attempting to verify tampered decision...")
    is_valid_tampered = verify_tde_decision_offline(tampered_data, tde_pubkey)
    
    if not is_valid_tampered:
        print("✓ Tampering detected! Modified decision rejected.")
    else:
        print("✗ Warning: Tampered decision was accepted (should not happen)")
    
    print()
    print("=" * 60)
    print("Demo completed successfully!")
    print()
    print("Key Takeaways:")
    print("- TDE signs every decision with Ed25519 private key")
    print("- Other services can verify decisions offline")
    print("- Signatures prevent tampering and impersonation")
    print("- No need to call TDE repeatedly for the same decision")
    print("=" * 60)
    
    return True


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python3 verify_offline.py")
        print()
        print("This script demonstrates offline verification of TDE decisions.")
        print("Requirements:")
        print("  - TDE service running on http://localhost:8000")
        print("  - pip install requests pynacl")
        return
    
    try:
        demo_workflow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to TDE service at http://localhost:8000")
        print("Make sure the service is running: python3 main.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
