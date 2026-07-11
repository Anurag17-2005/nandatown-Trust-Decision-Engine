"""
Trust Decision Engine - Main FastAPI Application
Validates NandaTown receipts and returns actionable trust decisions
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
from datetime import datetime
from typing import Optional

import crypto
import trust_store
import receipts
import decision
from models import (
    DecisionRequest, DecisionResponse, ValidationRequest, ValidationResponse,
    TrustScoreResponse, ReportRequest, ReportResponse, CompareResponse,
    PublicKeyResponse, HealthResponse, VerificationReceipt
)

# Initialize FastAPI app
app = FastAPI(
    title="Trust Decision Engine",
    description="Validates NandaTown receipts and provides actionable trust decisions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service start time for uptime tracking
SERVICE_START_TIME = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize database and keypair on startup"""
    # Initialize database
    trust_store.init_db()
    
    # Generate or load TDE keypair
    private_key = trust_store.get_metadata("private_key")
    public_key = trust_store.get_metadata("public_key")
    
    if not private_key or not public_key:
        print("Generating new TDE Ed25519 keypair...")
        private_key, public_key = crypto.generate_keypair()
        trust_store.set_metadata("private_key", private_key)
        trust_store.set_metadata("public_key", public_key)
        trust_store.set_metadata("created_at", datetime.utcnow().isoformat())
        print(f"✓ Keypair generated. DID: {crypto.pubkey_to_did(public_key)}")
    else:
        print(f"✓ Loaded existing keypair. DID: {crypto.pubkey_to_did(public_key)}")


def create_verification_receipt(input_data: dict, verdict: dict) -> VerificationReceipt:
    """Create a signed verification receipt for composability"""
    public_key = trust_store.get_metadata("public_key")
    private_key = trust_store.get_metadata("private_key")
    
    input_hash = crypto.hash_data(input_data)
    issued_at = int(time.time())
    
    # Message to sign
    message = {
        "input_hash": input_hash,
        "verdict": verdict,
        "issued_at": issued_at
    }
    
    # Sign with TDE's private key
    signature = crypto.sign_message(message, private_key)
    
    return VerificationReceipt(
        verifier=crypto.pubkey_to_did(public_key),
        input_hash=input_hash,
        verdict=verdict,
        issued_at=issued_at,
        signature=signature
    )


@app.post("/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    """
    Main endpoint: Full validation + trust scoring + actionable decision
    Returns ACCEPT/REJECT/ESCALATE recommendation with signed verification receipt
    """
    # 1. Validate receipt
    validation = receipts.validate_receipt(request.receipt)
    
    # 2. Get trust score for issuer
    issuer_id = request.receipt.issuer_did
    trust_score, confidence, total_reports, good_reports, bad_reports = trust_store.compute_trust_score(issuer_id)
    
    # 3. Make decision
    decision_result = decision.make_decision(
        trust_score=trust_score,
        confidence=confidence,
        receipt_valid=validation.valid and validation.signature_valid,
        corroboration_count=validation.corroboration_count,
        total_reports=total_reports
    )
    
    # 4. Create response verdict
    verdict = {
        "risk": decision_result["risk"],
        "recommendation": decision_result["recommendation"],
        "confidence": confidence,
        "receipt_valid": validation.valid,
        "issuer_reputation": trust_score
    }
    
    # 5. Generate signed verification receipt
    input_data = request.model_dump()
    verification_receipt = create_verification_receipt(input_data, verdict)
    
    return DecisionResponse(
        risk=decision_result["risk"],
        recommendation=decision_result["recommendation"],
        confidence=confidence,
        receipt_valid=validation.valid and validation.signature_valid,
        issuer_reputation=trust_score,
        reason=decision_result["reason"],
        verification_receipt=verification_receipt
    )


@app.post("/validate-receipt", response_model=ValidationResponse)
async def validate_receipt_endpoint(request: ValidationRequest):
    """
    Pure cryptographic validation without scoring
    Returns detailed validation results with signed receipt
    """
    validation = receipts.validate_receipt(request.receipt)
    
    # Create verdict for verification receipt
    verdict = {
        "valid": validation.valid,
        "signature_valid": validation.signature_valid,
        "corroboration_count": validation.corroboration_count
    }
    
    input_data = request.model_dump()
    verification_receipt = create_verification_receipt(input_data, verdict)
    
    return ValidationResponse(
        valid=validation.valid,
        signature_valid=validation.signature_valid,
        issuer_resolvable=validation.issuer_resolvable,
        corroborated=validation.corroborated,
        corroboration_count=validation.corroboration_count,
        receipt_hash=validation.receipt_hash,
        warnings=validation.warnings,
        verification_receipt=verification_receipt
    )


@app.post("/trust/report", response_model=ReportResponse)
async def submit_report(request: ReportRequest):
    """
    Submit outcome report (feedback loop)
    Updates agent's trust score based on good/bad outcomes
    """
    # Get previous score
    previous_score, _, _, _, _ = trust_store.compute_trust_score(request.agent_id)
    
    # Add report
    report_id = trust_store.add_report(
        agent_id=request.agent_id,
        outcome=request.outcome,
        receipt_hash=request.receipt_hash,
        reporter_id=request.reporter_id
    )
    
    # Get new score
    new_score, _, _, _, _ = trust_store.compute_trust_score(request.agent_id)
    
    return ReportResponse(
        recorded=True,
        new_trust_score=new_score,
        report_id=report_id,
        previous_score=previous_score
    )


@app.get("/trust/compare", response_model=CompareResponse)
async def compare_agents(agent_a: str, agent_b: str):
    """
    Compare two agents for delegation decisions
    Returns recommendation and reasoning
    """
    score_a, conf_a, total_a, _, _ = trust_store.compute_trust_score(agent_a)
    score_b, conf_b, total_b, _, _ = trust_store.compute_trust_score(agent_b)
    
    # Determine recommendation
    if score_a > score_b:
        recommendation = agent_a
        reasoning = f"{agent_a} has higher trust ({score_a:.2f} vs {score_b:.2f}) with {total_a} reports vs {total_b} reports"
    elif score_b > score_a:
        recommendation = agent_b
        reasoning = f"{agent_b} has higher trust ({score_b:.2f} vs {score_a:.2f}) with {total_b} reports vs {total_a} reports"
    else:
        # Tie - prefer agent with more data
        if total_a >= total_b:
            recommendation = agent_a
            reasoning = f"Equal trust scores ({score_a:.2f}), but {agent_a} has more data ({total_a} vs {total_b} reports)"
        else:
            recommendation = agent_b
            reasoning = f"Equal trust scores ({score_b:.2f}), but {agent_b} has more data ({total_b} vs {total_a} reports)"
    
    # Both acceptable if above threshold
    both_acceptable = score_a >= 0.7 and score_b >= 0.7
    
    return CompareResponse(
        recommendation=recommendation,
        agent_a_score=score_a,
        agent_b_score=score_b,
        confidence_delta=abs(score_a - score_b),
        reasoning=reasoning,
        both_acceptable=both_acceptable
    )


@app.get("/trust/{agent_id}", response_model=TrustScoreResponse)
async def get_trust_score(agent_id: str):
    """
    Query trust score for any agent
    Returns score, confidence, and report counts
    """
    trust_score, confidence, total_reports, good_reports, bad_reports = trust_store.compute_trust_score(agent_id)
    
    return TrustScoreResponse(
        agent_id=agent_id,
        trust_score=trust_score,
        confidence=confidence,
        based_on_receipts=total_reports,
        good_reports=good_reports,
        bad_reports=bad_reports,
        last_updated=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/pubkey", response_model=PublicKeyResponse)
async def get_public_key():
    """
    Get TDE's public key for offline verification
    Other services use this to verify TDE's signed decisions
    """
    public_key = trust_store.get_metadata("public_key")
    created_at = trust_store.get_metadata("created_at")
    
    if not public_key:
        raise HTTPException(status_code=500, detail="Service keypair not initialized")
    
    return PublicKeyResponse(
        public_key=public_key,
        did=crypto.pubkey_to_did(public_key),
        key_type="Ed25519",
        created_at=created_at or datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check"""
    uptime = int(time.time() - SERVICE_START_TIME)
    
    # Check database
    try:
        trust_store.get_metadata("public_key")
        db_status = "connected"
    except Exception:
        db_status = "error"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=uptime,
        database=db_status
    )


@app.get("/skill.md")
async def get_skill_doc():
    """Serve SKILL.md for agent-readable documentation"""
    return FileResponse("skill.md", media_type="text/markdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
