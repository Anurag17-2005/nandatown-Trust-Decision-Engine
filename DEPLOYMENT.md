# Deployment Guide - Trust Decision Engine

## Option 1: Deploy to Render (Recommended)

### Prerequisites
- GitHub account
- Render account (free tier works)

### Steps

1. **Push to GitHub**
   ```bash
   # Create a new repo on GitHub first, then:
   git remote add origin https://github.com/Anurag17-2005/trust-decision-engine.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select the `trust-decision-engine` repository

3. **Configure Service**
   - **Name**: `trust-decision-engine`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or upgrade for better performance)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-3 minutes)
   - Your service will be live at: `https://trust-decision-engine.onrender.com`

5. **Update SKILL.md**
   - Once deployed, update the service URL in `skill.md`
   - Replace `https://trust-decision-engine.onrender.com` with your actual URL
   - Commit and push

### Auto-Deploy
- Render automatically redeploys on every git push to main
- Check deployment logs in Render dashboard

---

## Option 2: Deploy to Other Platforms

### Railway
```bash
railway login
railway init
railway up
```

### Fly.io
```bash
flyctl launch
flyctl deploy
```

### Heroku
```bash
heroku create trust-decision-engine
git push heroku main
```

---

## Option 3: Local Development

### Setup
```bash
cd trust-decision-engine
pip install -r requirements.txt
```

### Run
```bash
python3 main.py
# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Test
```bash
# Run test script
./test_endpoints.sh

# Or use curl
curl http://localhost:8000/health
```

---

## Post-Deployment Checklist

- [ ] Service is accessible via HTTPS
- [ ] `/health` endpoint returns `{"status":"healthy"}`
- [ ] `/skill.md` is accessible
- [ ] All 7 endpoints tested
- [ ] Update service URL in README.md
- [ ] Update service URL in SKILL.md
- [ ] Register in NandaTown service registry
- [ ] Record demo video

---

## Service Registry Entry

Once deployed, add to NandaTown service registry:

```json
{
  "name": "Trust Decision Engine",
  "category": "trust",
  "description": "Validates NandaTown receipts and returns actionable trust decisions with signed verification receipts",
  "url": "https://trust-decision-engine.onrender.com",
  "endpoints": [
    "/decide",
    "/validate-receipt",
    "/trust/{agent_id}",
    "/trust/report",
    "/trust/compare",
    "/pubkey",
    "/health"
  ],
  "maintainer": "github.com/Anurag17-2005",
  "phase": 2,
  "novel_features": [
    "First NandaTown receipt validator",
    "Cryptographic Ed25519 verification",
    "Signed verification receipts",
    "Deterministic decision engine"
  ]
}
```

---

## Monitoring

### Check Service Health
```bash
curl https://trust-decision-engine.onrender.com/health
```

### View Logs (Render)
- Dashboard → your-service → Logs tab
- Real-time log streaming

### Common Issues

**Issue**: Service won't start
- **Fix**: Check logs for Python errors, verify requirements.txt

**Issue**: Database errors
- **Fix**: Render's ephemeral storage resets on deploy. For production, use persistent storage.

**Issue**: Slow first request
- **Fix**: Render free tier sleeps after inactivity. Upgrade or accept 10-20s cold starts.

---

## Environment Variables (Optional)

For production, consider adding:

```bash
# In Render dashboard → Environment
DATABASE_URL=<persistent-db-url>
SECRET_KEY=<random-secret>
LOG_LEVEL=info
```

---

## Scaling

### Render
- Upgrade instance type in dashboard
- Enable auto-scaling

### Database
- For production: Use PostgreSQL instead of SQLite
- Update `trust_store.py` to use SQLAlchemy with PostgreSQL

---

## Security Notes

- Service uses Ed25519 keypair generated on first startup
- Keypair stored in SQLite (ephemeral on free tier)
- For production: Store keypair in environment variables or secret manager
- No authentication required (designed for agent-to-agent communication)

---

## Testing Deployed Service

```bash
# Set your deployed URL
export TDE_URL="https://trust-decision-engine.onrender.com"

# Health check
curl $TDE_URL/health

# Get public key
curl $TDE_URL/pubkey

# Make decision
curl -X POST $TDE_URL/decide \
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

## Support

- **GitHub Issues**: https://github.com/Anurag17-2005/trust-decision-engine/issues
- **NandaTown Fork**: https://github.com/Anurag17-2005/nandatown
- **Demo Video**: [Link after recording]
