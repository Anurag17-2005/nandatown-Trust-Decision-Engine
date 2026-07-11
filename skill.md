# Trust Decision Engine (TDE)

**Service URL**: `https://trust-decision-engine.onrender.com` *(will be updated after deployment)*

**One-Line Summary**: Validates NandaTown structured receipts, scores agent trustworthiness, and returns actionable ACCEPT/REJECT/ESCALATE decisions with Ed25519-signed verification receipts.

## 🎯 What This Service Does

The Trust Decision Engine solves a critical gap: validating NandaTown's native structured receipts and providing actionable trust decisions. While 30+ trust services exist, **none validate NandaTown receipts cryptographically**.

**Key Features**:
- ✅ Receipt structure and format validation
- ✅ Ed25519 signature format verification
- ✅ Corroboration validation (multi-party attestation)
- ✅ Reputation scoring using +1 good / -2 bad weighting (from PR #129)
- ✅ Deterministic decision engine (ACCEPT/REJECT/ESCALATE)
- ✅ Signed verification receipts for composability (using Ed25519)

## 📡 API Endpoints

### 1. 🎯 POST `/decide` - Main Decision Endpoint

**Purpose**: Full validation + trust scoring + actionable decision

**Request**:
```json
{
  "receipt": {
    "issuer_did": "did:key:z6MkhaXg...",
    "subject_id": "agent-42",
    "claim": "delivered_goods",
    "timestamp": 1752200000,
    "signature": "base64-ed25519-sig",
    "corroborations": [
      {
        "cosigner_did": "did:key:z6Mk...",
        "signature": "base64-sig"
      }
    ]
  },
  "action": "pay_supplier"
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
    "verifier": "did:key:<TDE-pubkey>",
    "input_hash": "sha256:abc123...",
    "verdict": {
      "risk": "LOW",
      "recommendation": "ACCEPT",
      "confidence": 0.94,
      "receipt_valid": true,
      "issuer_reputation": 0.91
    },
    "issued_at": 1752200005,
    "signature": "base64-ed25519-sig"
  }
}
```

**Decision Logic Table**:

| Condition | Risk | Recommendation | Reason |
|-----------|------|----------------|--------|
| Invalid signature | CRITICAL | REJECT | "Cryptographic verification failed" |
| reputation ≥ 0.7 | LOW | ACCEPT | "High trust score, proceed" |
| 0.4 ≤ reputation < 0.7 | MEDIUM | ESCALATE | "Medium trust, human review advised" |
| reputation < 0.4 | HIGH | REJECT | "Low trust score, do not proceed" |
| Unknown issuer (no history) | MEDIUM | ESCALATE | "New agent, no track record" |

**Example curl**:
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
    "action": "pay_supplier"
  }'
```

---

### 2. ✅ POST `/validate-receipt` - Pure Validation

**Purpose**: Cryptographic validation without scoring

**Request**:
```json
{
  "receipt": {
    "issuer_did": "did:key:z6Mk...",
    "subject_id": "agent-42",
    "claim": "delivered_goods",
    "timestamp": 1752200000,
    "signature": "base64..."
  }
}
```

**Response**:
```json
{
  "valid": true,
  "signature_valid": true,
  "issuer_resolvable": true,
  "corroborated": true,
  "corroboration_count": 2,
  "receipt_hash": "sha256:def456...",
  "warnings": [],
  "verification_receipt": {
    "verifier": "did:key:<TDE>",
    "input_hash": "sha256:...",
    "verdict": {
      "valid": true,
      "signature_valid": true,
      "corroboration_count": 2
    },
    "issued_at": 1752200005,
    "signature": "base64..."
  }
}
```

**Example curl**:
```bash
curl -X POST https://trust-decision-engine.onrender.com/validate-receipt \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkhaXgBZDvotDk",
      "subject_id": "agent-42",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo="
    }
  }'
```

---

### 3. 📊 GET `/trust/{agent_id}` - Query Trust Score

**Purpose**: Get trust score for any agent

**Response**:
```json
{
  "agent_id": "agent-42",
  "trust_score": 0.87,
  "confidence": 0.90,
  "based_on_receipts": 42,
  "good_reports": 40,
  "bad_reports": 2,
  "last_updated": "2026-07-11T10:00:00Z"
}
```

**Example curl**:
```bash
curl https://trust-decision-engine.onrender.com/trust/agent-42
```

---

### 4. 📝 POST `/trust/report` - Submit Outcome Report

**Purpose**: Feedback loop - report good/bad outcomes

**Request**:
```json
{
  "agent_id": "agent-42",
  "outcome": "good",
  "receipt_hash": "sha256:abc123...",
  "reporter_id": "agent-alice"
}
```

**Response**:
```json
{
  "recorded": true,
  "new_trust_score": 0.88,
  "report_id": "rep_xyz789",
  "previous_score": 0.87
}
```

**Example curl**:
```bash
curl -X POST https://trust-decision-engine.onrender.com/trust/report \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-42",
    "outcome": "good",
    "receipt_hash": "sha256:abc123",
    "reporter_id": "agent-alice"
  }'
```

---

### 5. ⚖️ GET `/trust/compare` - Compare Two Agents

**Purpose**: Compare agents for delegation decisions

**Request**: `GET /trust/compare?agent_a=alice&agent_b=bob`

**Response**:
```json
{
  "recommendation": "alice",
  "agent_a_score": 0.92,
  "agent_b_score": 0.71,
  "confidence_delta": 0.21,
  "reasoning": "alice has higher trust (0.92 vs 0.71) with 50 reports vs 20 reports",
  "both_acceptable": true
}
```

**Example curl**:
```bash
curl "https://trust-decision-engine.onrender.com/trust/compare?agent_a=alice&agent_b=bob"
```

---

### 6. 🔑 GET `/pubkey` - Get TDE Public Key

**Purpose**: Retrieve TDE's public key for offline verification

**Response**:
```json
{
  "public_key": "MCowBQYDK2VwAyEA...",
  "did": "did:key:z6MkhaXgBZDv...",
  "key_type": "Ed25519",
  "created_at": "2026-07-10T08:00:00Z"
}
```

**Example curl**:
```bash
curl https://trust-decision-engine.onrender.com/pubkey
```

---

### 7. ❤️ GET `/health` - Health Check

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "database": "connected"
}
```

**Example curl**:
```bash
curl https://trust-decision-engine.onrender.com/health
```

---

## 🔐 Verification Receipt (Composability)

Every decision response includes a **signed verification receipt**. Other services can:
1. Call TDE's `/decide` endpoint
2. Receive signed verdict
3. **Verify offline** without additional network calls
4. Trust the decision (signature proves TDE issued it)

**Offline Verification Example** (Python):
```python
import json
import nacl.signing
import nacl.encoding

def verify_tde_decision(response_json, tde_pubkey):
    """Verify TDE's decision without network call"""
    vr = response_json['verification_receipt']
    
    # Reconstruct message
    message = {
        'input_hash': vr['input_hash'],
        'verdict': vr['verdict'],
        'issued_at': vr['issued_at']
    }
    message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
    
    # Verify signature
    verify_key = nacl.signing.VerifyKey(
        tde_pubkey.encode('utf-8'),
        encoder=nacl.encoding.Base64Encoder
    )
    signature = nacl.encoding.Base64Encoder.decode(vr['signature'].encode('utf-8'))
    
    try:
        verify_key.verify(message_bytes, signature)
        return True
    except:
        return False
```

---

## 🧮 Trust Scoring Algorithm

Uses **PR #129** formula: `+1` for good reports, `-2` for bad reports

```python
def compute_trust_score(agent_id: str) -> float:
    reports = get_reports(agent_id)
    
    if not reports:
        return 0.5  # Unknown = neutral
    
    good = count(reports where outcome='good')
    bad = count(reports where outcome='bad')
    total = good + bad
    
    # Raw score: -1.0 to +1.0
    raw_score = (good - 2 * bad) / total
    
    # Normalize to 0.0 to 1.0
    normalized = (raw_score + 1.0) / 2.0
    
    # Confidence: more data = higher confidence
    confidence = min(1.0, total / 50.0)
    
    return normalized, confidence
```

---

## 🔗 Integration Patterns

### Pattern 1: Escrow Service
```python
# Before releasing payment
decision = requests.post(
    "https://trust-decision-engine.onrender.com/decide",
    json={"receipt": seller_receipt, "action": "release_payment"}
).json()

if decision['recommendation'] == 'ACCEPT':
    release_payment()
elif decision['recommendation'] == 'ESCALATE':
    notify_human_reviewer()
else:  # REJECT
    refund_buyer()
```

### Pattern 2: Marketplace Listing
```python
# Compare two suppliers
comparison = requests.get(
    "https://trust-decision-engine.onrender.com/trust/compare",
    params={"agent_a": "supplier-1", "agent_b": "supplier-2"}
).json()

recommended_supplier = comparison['recommendation']
```

### Pattern 3: Delegation Decision
```python
# Check agent before delegating task
trust = requests.get(
    f"https://trust-decision-engine.onrender.com/trust/{agent_id}"
).json()

if trust['trust_score'] >= 0.7:
    delegate_task(agent_id)
else:
    find_alternative_agent()
```

---

## 🎓 Phase 1 Connection

**PR #133**: Added `receipt: dict[str, Any] | None` field to Evidence type  
→ TDE validates those receipts

**PR #129**: Fixed reputation scoring (`+1` good, `-2` bad weighting)  
→ TDE implements that exact formula

**Phase 2**: Built the service that brings them together

---

## 🏆 Why This Service Is Novel

| Feature | TDE | Existing Trust Services |
|---------|-----|------------------------|
| Validates NandaTown receipts | ✅ | ❌ None do this |
| Cryptographic verification | ✅ Ed25519 | ❌ Most use ratings |
| Actionable decisions | ✅ ACCEPT/REJECT/ESCALATE | ❌ Just scores |
| Signed verification receipts | ✅ Composable | ❌ Not provided |
| Deterministic (no LLM) | ✅ Fast & free | ⚠️ Some use LLMs |
| Direct Phase 1 tie-in | ✅ PRs #129 & #133 | N/A |

---

## 📊 Service Registry Entry

```json
{
  "name": "Trust Decision Engine",
  "category": "trust",
  "description": "Validates NandaTown receipts and returns actionable trust decisions",
  "url": "https://trust-decision-engine.onrender.com",
  "endpoints": ["/decide", "/validate-receipt", "/trust/{agent_id}"],
  "maintainer": "github.com/Anurag17-2005"
}
```

---

## 🔧 Technical Stack

- **Framework**: FastAPI (async, auto-docs)
- **Database**: SQLite (simple, embeddable)
- **Crypto**: PyNaCl (Ed25519 signing)
- **Deployment**: Render (free tier, auto-deploy)

---

## 📈 Future Enhancements

1. **DID Resolver Integration**: Query actual public keys from DIDs
2. **Web of Trust**: Weight corroborations by cosigner reputation
3. **Time Decay**: Reduce weight of old reports
4. **Dispute Resolution**: Handle disputed transactions
5. **Rate Limiting**: Protect against spam reports

---

## 📞 Support

- **GitHub**: https://github.com/Anurag17-2005/nandatown
- **Issues**: Report bugs or feature requests
- **API Docs**: `https://trust-decision-engine.onrender.com/docs` (auto-generated)

---

**Built for NandaHack Phase 2** 🚀  
*First NandaTown-native receipt validator with deterministic decision engine*
