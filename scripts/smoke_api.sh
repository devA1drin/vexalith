#!/usr/bin/env bash
# Smoke-test the running API (expects backend on :8000).
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8000}"
curl -s "$BASE/api/health" | python3 -m json.tool
NAME="smoke-$(date +%s)"
USER_JSON=$(curl -s -X POST "$BASE/api/users" -H 'Content-Type: application/json' -d "{\"display_name\":\"$NAME\"}")
echo "$USER_JSON" | python3 -m json.tool
USER_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "$USER_JSON")
Q_JSON=$(curl -s "$BASE/api/questions/next?user_id=$USER_ID")
echo "$Q_JSON" | python3 -m json.tool
QID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "$Q_JSON")
curl -s -X POST "$BASE/api/responses" -H 'Content-Type: application/json' \
  -d "{\"user_id\":$USER_ID,\"question_id\":$QID,\"answer_text\":\"The claim lacks evidence because the sample is tiny; an assumption is that the poll is representative. An alternative is selection bias.\"}" \
  | python3 -m json.tool
curl -s "$BASE/api/progress/$USER_ID" | python3 -m json.tool
