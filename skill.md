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

## Receipt Format

A valid receipt must contain:

```json
{
  "issuer_did": "did:key:z6Mk...",      // Agent who issued this receipt
  "subject_id": "agent-42",              // Agent being evaluated  
  "claim": "delivered_goods",            // What was done
  "timestamp": 1752200000,               // Unix timestamp
  "signature": "base64-ed25519",         // Cryptographic signature
  "corroborations": []                   // Optional: witnesses
}
```

**Corroborations** (optional): Add witnesses to increase trust
```json
{"cosigner_did": "did:key:z6Mk...", "signature": "base64..."}
```

---

## Primary Endpoint

**Most agents should call `POST /decide`**. It performs receipt validation, computes trust, assesses risk, and returns an actionable recommendation (ACCEPT, ESCALATE, or REJECT). 

Use the other endpoints only for specialized tasks such as querying trust scores or reporting outcomes.

---

## Typical Workflow

```
Receipt from other agent
        │
        ▼
POST /decide
        │
        ▼
Recommendation
  ├── ACCEPT → Continue process
  ├── ESCALATE → Human review
  └── REJECT → Stop process
```

**Simple Example**:
```python
# 1. Get receipt from another agent
receipt = other_agent.get_receipt()

# 2. Ask for decision
decision = requests.post(
    "https://trust-decision-engine.onrender.com/decide",
    json={"receipt": receipt, "action": "release_payment"}
).json()

# 3. Act on recommendation
if decision['recommendation'] == 'ACCEPT':
    release_payment()
elif decision['recommendation'] == 'ESCALATE':
    notify_human(decision['reason'])
else:  # REJECT
    cancel_transaction(decision['reason'])
```

---

## Endpoints

### 1. POST `/decide` - Main Decision Endpoint

**Purpose**: Get actionable trust decision with reasoning

**When to use**: This is the primary endpoint - use it for most trust decisions.

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
  "action": "release_payment"  // Your intended action - provides context
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
  "reason": "High trust score (0.91). Agent has 42 verified reports.",
  "verification_receipt": {
    "verifier": "did:key:z6Mk...",
    "verdict": {...},
    "signature": "base64-ed25519-sig"
  }
}
```

**Note**: Store the `verification_receipt` to prove this decision to other services. Verify offline using the signature and public key from `/pubkey`.

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

**Purpose**: Validate receipt structure without trust scoring

**When to use**: When you only need format validation, not a trust decision.

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

**Purpose**: Report transaction outcome to build reputation network

**Request**:
```json
{
  "agent_id": "agent-42",
  "outcome": "good",
  "receipt_hash": "sha256:abc123...",
  "reporter_id": "your-agent-id"
}
```

**Recommended**: Report outcomes after completed transactions to improve future trust scores.

**Effect**: Your report immediately updates the agent's trust score and affects future decisions.

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

### 6. GET `/pubkey` - Get Public Key

**Purpose**: Retrieve TDE's public key for offline signature verification

**When to use**: When you need to verify `verification_receipt` signatures without network calls.

**curl**: `curl https://trust-decision-engine.onrender.com/pubkey`

**Response**:
```json
{
  "public_key": "MCowBQYDK2VwAyEA...",
  "did": "did:key:z6Mk...",
  "key_type": "Ed25519"
}
```

---

### 7. GET `/health` - Health Check

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
# Get decision from TDE
decision = requests.post(
    "https://trust-decision-engine.onrender.com/decide",
    json={
        "receipt": seller_receipt,
        "action": "release_payment"
    }
).json()

# Act on recommendation
if decision['recommendation'] == 'ACCEPT':
    transfer_funds(seller_id)
    report_outcome("good", seller_receipt)
elif decision['recommendation'] == 'ESCALATE':
    notify_human_reviewer(decision['reason'])
else:  # REJECT
    refund_buyer()
    report_outcome("bad", seller_receipt)
```

---

## Support

- **Interactive Docs**: `https://trust-decision-engine.onrender.com/docs` (auto-generated Swagger)
- **Health Check**: `GET /health`
- **Response Time**: Typically < 200ms
- **GitHub**: https://github.com/YOUR_USERNAME/trust-decision-engine
