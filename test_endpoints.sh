#!/bin/bash
# Quick test script for Trust Decision Engine endpoints

BASE_URL="http://localhost:8000"

echo "Testing Trust Decision Engine..."
echo "================================"
echo ""

echo "1. Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

echo "2. Get Public Key:"
curl -s "$BASE_URL/pubkey" | python3 -m json.tool
echo -e "\n"

echo "3. Submit good report for agent-test:"
curl -s -X POST "$BASE_URL/trust/report" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-test",
    "outcome": "good",
    "receipt_hash": "sha256:test123",
    "reporter_id": "agent-alice"
  }' | python3 -m json.tool
echo -e "\n"

echo "4. Get trust score for agent-test:"
curl -s "$BASE_URL/trust/agent-test" | python3 -m json.tool
echo -e "\n"

echo "5. Validate receipt:"
curl -s -X POST "$BASE_URL/validate-receipt" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkhaXgBZDvotDk",
      "subject_id": "agent-test",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=",
      "corroborations": []
    }
  }' | python3 -m json.tool
echo -e "\n"

echo "6. Make decision:"
curl -s -X POST "$BASE_URL/decide" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "issuer_did": "did:key:z6MkhaXgBZDvotDk",
      "subject_id": "agent-test",
      "claim": "delivered_goods",
      "timestamp": 1752200000,
      "signature": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=",
      "corroborations": []
    },
    "action": "pay_supplier"
  }' | python3 -m json.tool
echo -e "\n"

echo "7. Compare agents:"
curl -s "$BASE_URL/trust/compare?agent_a=agent-test&agent_b=agent-42" | python3 -m json.tool
echo -e "\n"

echo "All tests completed!"
