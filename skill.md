# Trust Decision Engine

**Service URL**: `https://trust-decision-engine.onrender.com` *(update after deployment)*

---

## What This Service Does

Autonomous agents frequently need to decide whether to trust claims made by other agents before releasing payments, delegating tasks, or accepting results. 

This service:
- Validates NandaTown structured receipts
- Scores agent reputation based on historical reports
- Returns actionable decisions: **ACCEPT**, **REJECT**, or **ESCALATE**
- Provides Ed25519-signed verification receipts for composability

---

## When to Call This Service

Use this service when you need to:
- **Verify trust** before releasing payment to another agent
- **Make delegation decisions** between multiple agents
- **Validate receipts** from untrusted sources
- **Build reputation** by reporting transaction outcomes

---

## Agent Workflow

```
┌─────────────────────────────────────────────────┐
│  Your Agent                                     │
└──────────────┬──────────────────────────────────┘
               │
               │ 1. Collect receipt from other agent
               ▼
    ┌──────────────────────────┐
    │  POST /decide            │
    │  (receipt + action)      │
    └──────────┬───────────────┘
               │
               │ 2. Get decision + reasoning
               ▼
         ┌─────────────┐
         │ ACCEPT?     │
         └─────┬───────┘
               │
       ┌───────┼───────┐
       │       │       │
      YES     MAYBE    NO
       │       │       │
       ▼       ▼       ▼
   Continue  Escalate  Stop
   Process   to Human  Process
```

**Simple Example**:
```python
# 1. Get receipt from another agent
receipt = other_agent.get_receipt()

# 2. Ask for decision
response = requests.post(
    "https://trust-decision-engine.onrender.com/decide",
    json={"receipt": receipt, "action": "release_payment"}
).json()

# 3. Act on recommendation
if response['recommendation'] == 'ACCEPT':
    release_payment()
elif response['recommendation'] == 'ESCALATE':
    notify_human(response['reason'])
else:  # REJECT
    cancel_transaction(response['reason'])
```

---

## Endpoints

### 1. POST `/decide` - Main Decision Endpoint

**Purpose**: Get actionable trust decision with reasoning

**Request**:
```json
{
  "receipt": {
    "issuer_did": "did:key:z6MkhaXg...",
    "subject_id": "agent-42",
    "claim": "delivered_goods",
    "timestamp": 1752200000,
    "signature": "base64-signature",
    "corroborations": []
  },
  "action": "release_payment"
}
```

**Response**:
```json
{
  "risk": "LOW",
  "recommendation": "ACCEPT",
  "confidence": 0.94,
  "receipt_valid": true,
  "issuer_reputation": 0.91,
  "reason": "High trust score (0.91). Agent has 42 verified reports. Receipt valid with 2 corroborations.",
  "verification_receipt": {
    "verifier": "did:key:z6Mk...",
    "input_hash": "sha256:abc123...",
    "verdict": {...},
    "issued_at": 1752200005,
    "signature": "base64-ed25519-sig"
  }
}
```

**curl Example**:
```bash
curl -X POST https://trust-decision-engine.onrender.com/decide \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkhaXgBZDvotDk",
      "subject_id": "agent-42",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=",
      "corroborations": []
    },
    "action": "release_payment"
  }'
```

---

### 2. POST `/validate-receipt` - Receipt Validation Only

**Purpose**: Validate receipt structure without scoring

**Request**: Same receipt structure as `/decide`

**Response**:
```json
{
  "valid": true,
  "signature_valid": true,
  "corroborated": true,
  "corroboration_count": 2,
  "warnings": []
}
```

---

### 3. GET `/trust/{agent_id}` - Query Trust Score

**Purpose**: Check reputation of any agent

**curl**: `curl https://trust-decision-engine.onrender.com/trust/agent-42`

**Response**:
```json
{
  "agent_id": "agent-42",
  "trust_score": 0.87,
  "confidence": 0.90,
  "based_on_receipts": 42,
  "good_reports": 40,
  "bad_reports": 2
}
```

---

### 4. POST `/trust/report` - Submit Outcome Report

**Purpose**: Report transaction outcome (builds reputation)

**Request**:
```json
{
  "agent_id": "agent-42",
  "outcome": "good",
  "receipt_hash": "sha256:abc123...",
  "reporter_id": "your-agent-id"
}
```

**Important**: Always report outcomes to build the reputation network.

---

### 5. GET `/trust/compare` - Compare Two Agents

**Purpose**: Choose between multiple agents

**curl**: `curl "https://trust-decision-engine.onrender.com/trust/compare?agent_a=alice&agent_b=bob"`

**Response**:
```json
{
  "recommendation": "alice",
  "agent_a_score": 0.92,
  "agent_b_score": 0.71,
  "reasoning": "alice has higher trust (0.92 vs 0.71)"
}
```

---

### 6. GET `/health` - Health Check

**curl**: `curl https://trust-decision-engine.onrender.com/health`

---

## Decision Logic Table

| Condition | Risk | Recommendation | When This Happens |
|-----------|------|----------------|-------------------|
| Invalid signature | CRITICAL | REJECT | Receipt format is invalid |
| reputation ≥ 0.7 | LOW | ACCEPT | Agent has strong positive history |
| 0.4 ≤ reputation < 0.7 | MEDIUM | ESCALATE | Agent has mixed history |
| reputation < 0.4 | HIGH | REJECT | Agent has negative history |
| Unknown issuer | MEDIUM | ESCALATE | No history available for agent |

**Trust Score Formula**:
- Good reports: +1 point
- Bad reports: -2 points
- Normalized to 0.0-1.0 range
- More data = higher confidence

---

## Error Handling

### Common Errors

**400 Bad Request**:
```json
{
  "detail": "Invalid receipt format: missing required field 'signature'"
}
```
**Action**: Check your receipt structure matches the schema

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "outcome"],
      "msg": "value is not a valid enumeration member; permitted: 'good', 'bad'"
    }
  ]
}
```
**Action**: Fix the field indicated in `loc`

**500 Internal Server Error**:
```json
{
  "detail": "Service error"
}
```
**Action**: Retry after a few seconds or check `/health` endpoint

---

## Integration Example

**Escrow Service Using TDE**:

```python
class EscrowService:
    def release_payment(self, seller_receipt):
        # 1. Ask TDE for decision
        decision = requests.post(
            "https://trust-decision-engine.onrender.com/decide",
            json={
                "receipt": seller_receipt,
                "action": "release_payment"
            }
        ).json()
        
        # 2. Act on recommendation
        if decision['recommendation'] == 'ACCEPT':
            self.transfer_funds(seller_receipt['subject_id'])
            self.report_outcome("good", seller_receipt)
            return "Payment released"
            
        elif decision['recommendation'] == 'ESCALATE':
            self.notify_human_reviewer(decision['reason'])
            return "Pending human review"
            
        else:  # REJECT
            self.refund_buyer()
            self.report_outcome("bad", seller_receipt)
            return "Payment rejected"
    
    def report_outcome(self, outcome, receipt):
        # 3. Always report outcomes (builds network)
        requests.post(
            "https://trust-decision-engine.onrender.com/trust/report",
            json={
                "agent_id": receipt['issuer_did'],
                "outcome": outcome,
                "receipt_hash": hash_receipt(receipt),
                "reporter_id": self.agent_id
            }
        )
```

---

## Support

- **Service Status**: `GET /health`
- **Interactive Docs**: `https://trust-decision-engine.onrender.com/docs`
- **GitHub**: https://github.com/YOUR_USERNAME/trust-decision-engine
