# Trust Decision Engine - Demo Video Script (3 minutes)

## 🎬 Setup
- **Open**: `demo.html` in your browser (just double-click the file)
- **Have ready**: This script
- **Duration**: 3 minutes max

---

## 📝 Script

### [0:00 - 0:20] Introduction (20 seconds)

**SAY**:
> "Hi! I'm demonstrating Trust Decision Engine for NandaHack Phase 2.
> 
> In NandaTown, autonomous agents need to decide whether to trust other agents before releasing payments or delegating tasks.
> 
> My service validates receipts, scores reputation, and returns clear decisions: ACCEPT, REJECT, or ESCALATE."

**SHOW**: 
- The demo page title and header

---

### [0:20 - 1:00] Scenario 1: Trusted Agent (40 seconds)

**SAY**:
> "Let's start with a trusted agent - someone with good history."

**DO**:
1. Click "🌟 Trusted Agent" button
2. Scroll to show the receipt JSON
3. Point out the `issuer_did` and `claim` fields

**SAY**:
> "Here we have Alice, who claims she delivered goods. Let me ask the Trust Decision Engine."

**DO**:
4. Click "🚀 Get Trust Decision"
5. Wait for response (2 seconds)

**SAY**:
> "Perfect! The system returns ACCEPT with LOW risk because Alice has a high reputation score of 91%. 
> The reason explains she has 42 verified reports with strong history."

**SHOW**:
- Green ACCEPT badge
- The trust score (0.91)
- The reason text

---

### [1:00 - 1:40] Scenario 2: Untrusted Agent (40 seconds)

**SAY**:
> "Now let's try an untrusted agent with bad history."

**DO**:
1. Click "⚠️ Untrusted Agent" button
2. Click "🚀 Get Trust Decision"
3. Wait for response

**SAY**:
> "See the difference? The system returns REJECT with HIGH risk.
> The trust score is low because this agent has negative reputation.
> This protects you from bad actors automatically."

**SHOW**:
- Red REJECT badge
- Low trust score
- The warning reason

---

### [1:40 - 2:20] Scenario 3: New Agent (40 seconds)

**SAY**:
> "What about a brand new agent with no history?"

**DO**:
1. Click "❓ New Agent" button
2. Click "🚀 Get Trust Decision"
3. Wait for response

**SAY**:
> "Interesting! It returns ESCALATE with MEDIUM risk.
> This means: 'I don't have enough data - you should review this manually.'
> The system is being cautious and transparent about uncertainty."

**SHOW**:
- Orange ESCALATE badge
- 0.5 trust score (neutral)
- The explanation about no history

---

### [2:20 - 2:50] Scenario 4: Corroborated Receipt (30 seconds)

**SAY**:
> "Finally, here's something unique: a corroborated receipt with witnesses."

**DO**:
1. Click "✅ Corroborated Receipt" button
2. Scroll to show the `corroborations` array
3. Click "🚀 Get Trust Decision"

**SAY**:
> "Notice the receipt has two corroborations - other agents who witnessed the transaction.
> This increases trust significantly. Multiple parties verified this action.
> The system accounts for this and returns ACCEPT with even higher confidence."

**SHOW**:
- The corroborations in the JSON
- High confidence score
- The reason mentioning corroborations

---

### [2:50 - 3:00] Closing (10 seconds)

**SAY**:
> "That's Trust Decision Engine: validating receipts, scoring trust, returning clear decisions.
> 
> Every response includes a signed verification receipt that other services can verify offline.
> 
> Thank you!"

**SHOW**:
- Scroll to show the `verification_receipt` in one of the responses
- The GitHub link at bottom: https://github.com/Anurag17-2005/nandatown-Trust-Decision-Engine

---

## 🎯 Key Points to Hit

1. ✅ **Problem**: Agents need to trust each other
2. ✅ **Solution**: Automated trust decisions
3. ✅ **Novel**: Validates NandaTown receipts specifically
4. ✅ **Deterministic**: Same input = same output
5. ✅ **Composability**: Signed verification receipts
6. ✅ **Smart**: Handles trusted, untrusted, and unknown agents differently

---

## 💡 Tips for Recording

1. **Go Slow**: Pause 2 seconds after each click
2. **Read Clearly**: Speak at 80% your normal speed
3. **Show Results**: Hover over important parts (badges, scores)
4. **Stay Calm**: If you mess up, just restart that section
5. **Test First**: Do a practice run before recording

---

## 🎥 Recording Checklist

- [ ] Close unnecessary browser tabs
- [ ] Full screen browser (F11)
- [ ] Check microphone audio
- [ ] Test demo page first (click through all scenarios)
- [ ] Clear throat, sip water
- [ ] Record in quiet room
- [ ] Follow script timing
- [ ] Show GitHub link at end

---

## 🔧 If Something Goes Wrong

**Demo page not loading?**
- Just open `demo.html` file directly in Chrome/Firefox

**API not responding?**
- Check https://nandatown-trust-decision-engine.onrender.com/health
- If service is asleep (free tier), wait 30 seconds for wake-up

**Forgot what to say?**
- Just explain what you see on screen
- Focus on the recommendation (ACCEPT/REJECT/ESCALATE)

---

**Good luck! You've got this! 🚀**
