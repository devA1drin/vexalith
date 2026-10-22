#!/usr/bin/env bash
# Smoke-test a running Vexalith API with a locally minted backend JWT.
#   BACKEND_JWT_SECRET must match the API's secret (read from env; never echoed).
#   BASE defaults to http://127.0.0.1:8000
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8000}"
: "${BACKEND_JWT_SECRET:?export BACKEND_JWT_SECRET first}"
TOKEN=$(python3 - <<'PY'
import os, time, jwt
now = int(time.time())
print(jwt.encode({"iss": "vexalith-web", "aud": "vexalith-api", "sub": "github:smoke",
                  "provider": "github", "provider_account_id": "smoke", "name": "Smoke Test",
                  "iat": now, "exp": now + 300}, os.environ["BACKEND_JWT_SECRET"], algorithm="HS256"))
PY
)
AUTH=(-H "Authorization: Bearer $TOKEN")
curl -s "$BASE/api/health"; echo
curl -s -o /dev/null -w "no token -> %{http_code}\n" "$BASE/api/me"
Q=$(curl -s "${AUTH[@]}" "$BASE/api/questions/next?language=python")
QID=$(python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" <<<"$Q")
echo "question $QID"
curl -s "${AUTH[@]}" -X POST "$BASE/api/questions/$QID/skip?language=python" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('skip ->', d['next_question']['id'])"
curl -s "${AUTH[@]}" -X POST "$BASE/api/responses" -H 'Content-Type: application/json' \
  -d "{\"question_id\":$QID,\"answer_text\":\"It returns early because the loop never runs for an empty input.\"}" \
  | python3 -c "import json,sys; f=json.load(sys.stdin)['feedback']; print('verdict', f['verdict'], f['overall_score'])"
curl -s "${AUTH[@]}" "$BASE/api/progress" | python3 -c "import json,sys; d=json.load(sys.stdin); print('responses', d['total_responses'], 'skips', d['total_skips'])"
