"""
Deterministic decision engine
Maps trust scores and receipt validity to actionable decisions
"""
from typing import Dict, Any


def make_decision(
    trust_score: float,
    confidence: float,
    receipt_valid: bool,
    corroboration_count: int,
    total_reports: int
) -> Dict[str, Any]:
    """
    Deterministic decision table
    
    Priority order:
    1. Invalid receipt -> REJECT
    2. High trust (>=0.7) -> ACCEPT
    3. Unknown agent (no history) -> ESCALATE
    4. Low trust (<0.4) -> REJECT
    5. Medium trust (0.4-0.7) -> ESCALATE
    """
    
    # Invalid receipt = immediate reject
    if not receipt_valid:
        return {
            "risk": "CRITICAL",
            "recommendation": "REJECT",
            "reason": "Cryptographic verification failed. Receipt signature is invalid."
        }
    
    # Unknown agent (no history)
    if total_reports == 0:
        return {
            "risk": "MEDIUM",
            "recommendation": "ESCALATE",
            "reason": f"New agent with no track record. Receipt is valid with {corroboration_count} corroborations. Human review advised."
        }
    
    # High trust
    if trust_score >= 0.7:
        return {
            "risk": "LOW",
            "recommendation": "ACCEPT",
            "reason": f"High trust score ({trust_score:.2f}). Agent has {total_reports} verified reports. Receipt valid with {corroboration_count} corroborations."
        }
    
    # Low trust
    if trust_score < 0.4:
        return {
            "risk": "HIGH",
            "recommendation": "REJECT",
            "reason": f"Low trust score ({trust_score:.2f}). Agent has negative reputation based on {total_reports} reports. Do not proceed."
        }
    
    # Medium trust (0.4 <= score < 0.7)
    return {
        "risk": "MEDIUM",
        "recommendation": "ESCALATE",
        "reason": f"Medium trust score ({trust_score:.2f}). Agent has mixed reputation based on {total_reports} reports. Human review advised."
    }
