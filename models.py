"""
Pydantic models for Trust Decision Engine API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Corroboration(BaseModel):
    cosigner_did: str
    signature: str


class Receipt(BaseModel):
    issuer_did: str
    subject_id: str
    claim: str
    timestamp: int
    signature: str
    corroborations: Optional[List[Corroboration]] = []


class DecisionRequest(BaseModel):
    receipt: Receipt
    action: str


class VerificationReceipt(BaseModel):
    verifier: str
    input_hash: str
    verdict: Dict[str, Any]
    issued_at: int
    signature: str


class DecisionResponse(BaseModel):
    risk: str
    recommendation: str
    confidence: float
    receipt_valid: bool
    issuer_reputation: float
    reason: str
    verification_receipt: VerificationReceipt


class ValidationRequest(BaseModel):
    receipt: Receipt


class ValidationResponse(BaseModel):
    valid: bool
    signature_valid: bool
    issuer_resolvable: bool
    corroborated: bool
    corroboration_count: int
    receipt_hash: str
    warnings: List[str]
    verification_receipt: VerificationReceipt


class TrustScoreResponse(BaseModel):
    agent_id: str
    trust_score: float
    confidence: float
    based_on_receipts: int
    good_reports: int
    bad_reports: int
    last_updated: str


class ReportRequest(BaseModel):
    agent_id: str
    outcome: str = Field(..., pattern="^(good|bad)$")
    receipt_hash: str
    reporter_id: str


class ReportResponse(BaseModel):
    recorded: bool
    new_trust_score: float
    report_id: str
    previous_score: float


class CompareResponse(BaseModel):
    recommendation: str
    agent_a_score: float
    agent_b_score: float
    confidence_delta: float
    reasoning: str
    both_acceptable: bool


class PublicKeyResponse(BaseModel):
    public_key: str
    did: str
    key_type: str
    created_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: int
    database: str
