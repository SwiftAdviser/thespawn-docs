#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://thespawn.io}"
SOCIAL_MCP_URL="${SOCIAL_MCP_URL:-https://socialintel.dev/mcp/}"

echo "Checking public search API"
search_json="$(curl -sS "${BASE_URL}/api/v1/search?q=instagram%20influencer%20finder&limit=2")"
printf '%s' "$search_json" | grep -Fq '"agent_id":29382'

echo "Checking agent detail API"
detail_json="$(curl -sS "${BASE_URL}/api/v1/agents/base/29382")"
printf '%s' "$detail_json" | grep -Fq '"endpoint":"https:\/\/socialintel.dev\/mcp\/"'

echo "Checking Social Intel MCP tools/list"
tools_json="$(curl -sS "$SOCIAL_MCP_URL" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":"tools-list","method":"tools/list","params":{}}')"
printf '%s' "$tools_json" | grep -Fq '"search_leads"'

echo "Checking Social Intel direct demo request"
demo_body="/tmp/thespawn-social-demo-smoke.json"
demo_status="$(curl -sS -o "$demo_body" -w '%{http_code}' "https://socialintel.dev/v1/search?limit=3&query=fitness&country=US&demo=true")"
if [ "$demo_status" = "200" ]; then
  grep -Fq 'demo_result_count' "$demo_body"
  grep -Fq '"count":3' "$demo_body"
elif [ "$demo_status" = "429" ]; then
  grep -Fq 'Demo rate limit exceeded' "$demo_body"
else
  echo "Unexpected demo status: $demo_status" >&2
  cat "$demo_body" >&2
  exit 1
fi

echo "Checking hosted spawnr MCP runtime"
spawnr_init_json="$(curl -sS "${BASE_URL}/mcp" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":"init","method":"initialize","params":{}}')"
printf '%s' "$spawnr_init_json" | grep -Fq '"name":"spawnr MCP"'

spawnr_tools_json="$(curl -sS "${BASE_URL}/mcp" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":"tools-list","method":"tools/list","params":{}}')"
printf '%s' "$spawnr_tools_json" | grep -Fq '"spawnr_search"'
printf '%s' "$spawnr_tools_json" | grep -Fq '"spawnr_execute"'

echo "Checking x402 challenge"
x402_status="$(curl -sS -o /tmp/thespawn-x402-smoke.json -w '%{http_code}' https://socialintel.dev/v1/search \
  -H "Content-Type: application/json" \
  --data '{"query":"yoga","country":"US","limit":1}')"
test "$x402_status" = "402"

echo "Smoke checks passed"
