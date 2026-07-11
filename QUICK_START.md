# Trust Decision Engine - Quick Start Guide

## 🚀 What You Have

A complete, working Trust Decision Engine service for NandaHack Phase 2!

- ✅ 7 RESTful endpoints
- ✅ Cryptographic receipt validation (Ed25519)
- ✅ Trust scoring using PR #129 formula
- ✅ Deterministic decision engine
- ✅ Signed verification receipts
- ✅ Complete documentation
- ✅ Test scripts and demos
- ✅ Ready for deployment

---

## ⚡ Quick Test (Local)

```bash
# Start the server
cd trust-decision-engine
python3 main.py

# In another terminal, test all endpoints
./test_endpoints.sh
```

Server runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

---

## 🌐 Deploy to Render (5 minutes)

1. **Create GitHub repo** (if not done):
   ```bash
   # On GitHub, create new repo: trust-decision-engine
   git remote add origin https://github.com/YOUR_USERNAME/trust-decision-engine.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect settings from `render.yaml`
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment

3. **Update URLs**:
   - Once deployed, get your service URL (e.g., `https://trust-decision-engine.onrender.com`)
   - Update URLs in `skill.md` and `README.md`
   - Commit and push

---

## 🎬 Record Demo Video (3 minutes)

Use this script:

**[0:00-0:30] Introduction**
```
"Hi! This is Trust Decision Engine for NandaHack Phase 2.
It's the first service to validate NandaTown receipts cryptographically
and return actionable trust decisions."
```

**[0:30-1:00] Show SKILL.md**
```bash
# Open in browser:
curl https://YOUR-SERVICE-URL.onrender.com/skill.md

"Here's the complete documentation. We have 7 endpoints.
The main one is /decide - it validates receipts and returns
ACCEPT, REJECT, or ESCALATE decisions."
```

**[1:00-1:45] Demo: Good Agent**
```bash
# Show this command:
curl -X POST https://YOUR-SERVICE-URL.onrender.com/decide \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkGoodAgent",
      "subject_id": "agent-good",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "validSignatureHere==",
      "corroborations": []
    },
    "action": "pay_supplier"
  }'

"For an agent with good history, we get ACCEPT recommendation
with high trust score. The reason explains why."
```

**[1:45-2:30] Demo: Bad Agent**
```bash
# First, add bad reports:
curl -X POST https://YOUR-SERVICE-URL.onrender.com/trust/report \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "did:key:z6MkBadAgent",
    "outcome": "bad",
    "receipt_hash": "sha256:xyz",
    "reporter_id": "agent-alice"
  }'

# Then decide:
curl -X POST https://YOUR-SERVICE-URL.onrender.com/decide \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkBadAgent",
      "subject_id": "agent-bad",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "validSignatureHere==",
      "corroborations": []
    },
    "action": "pay_supplier"
  }'

"For an agent with bad history, we get REJECT with low trust score."
```

**[2:30-3:00] Composability**
```bash
"Notice every response includes a verification_receipt with a signature.
Other services can verify this decision offline using our /pubkey endpoint.
No need to call us repeatedly - the signature proves we issued this decision."

# Show pubkey:
curl https://YOUR-SERVICE-URL.onrender.com/pubkey
```

---

## 📋 Pre-Submission Checklist

### Must Do
- [ ] Deploy to Render (or similar)
- [ ] Test all endpoints on live service
- [ ] Update service URLs in docs
- [ ] Record 3-minute demo video
- [ ] Submit video + GitHub link + live URL

### Optional But Recommended
- [ ] Register in NandaTown service registry
- [ ] Add badge to README showing service is live
- [ ] Test offline verification demo
- [ ] Share on Discord/social media

---

## 🎯 Key Selling Points (For Judges)

### 1. Perfect Phase 1 → Phase 2 Continuity
- PR #133 added receipt field → We validate those receipts
- PR #129 fixed scoring formula → We use that exact formula
- Direct technical link, not just narrative

### 2. Fills Real Gap
- 222 services exist, 30+ do trust
- NONE validate NandaTown receipts cryptographically
- First NandaTown-native receipt validator

### 3. Composability Innovation
- Signed verification receipts
- Offline verification possible
- Other services can trust our decisions without repeated calls

### 4. Deterministic = Reliable
- No LLM (fast, free, predictable)
- Same input → same output
- Explainable reasoning

### 5. Production-Ready
- Error handling
- Input validation
- Auto-generated API docs
- Health checks
- Test scripts

---

## 📞 Quick Commands Reference

```bash
# Local Development
python3 main.py                    # Start server
./test_endpoints.sh                # Test all endpoints
python3 verify_offline.py          # Demo offline verification

# Git
git status                         # Check status
git add -A && git commit -m "msg"  # Commit changes
git push                           # Deploy to Render (auto)

# Testing Live Service
export URL="https://your-service.onrender.com"
curl $URL/health                   # Health check
curl $URL/pubkey                   # Get public key
curl $URL/skill.md                 # View documentation
curl $URL/docs                     # Interactive API docs
```

---

## 🐛 Troubleshooting

### Server won't start locally
```bash
pip install -r requirements.txt    # Reinstall dependencies
python3 --version                  # Check Python >= 3.9
```

### Render deployment fails
- Check logs in Render dashboard
- Verify `render.yaml` is correct
- Ensure `requirements.txt` has all deps

### Database errors
- SQLite creates `trust_history.db` automatically
- On Render free tier, DB resets on deploy (expected)
- For production, use persistent storage

---

## 📚 Documentation Files

- **README.md**: Overview for humans
- **SKILL.md**: Agent-readable API documentation
- **DEPLOYMENT.md**: Detailed deployment guide
- **SUBMISSION.md**: Complete Phase 2 submission doc
- **QUICK_START.md**: This file (quick reference)

---

## 🎉 You're Ready!

1. Deploy to Render (5 min)
2. Update URLs in docs (2 min)
3. Record demo video (3 min)
4. Submit!

**Total time to submission: ~10 minutes from here**

---

**Questions?** Check SUBMISSION.md for comprehensive details.

**Good luck!** 🚀
