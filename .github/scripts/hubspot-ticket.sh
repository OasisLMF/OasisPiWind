#!/usr/bin/env bash
set -euo pipefail

MODE="${1:?usage: hubspot-ticket.sh create|comment|close}"

HUBSPOT_PIPELINE_ID="0"
TICKET_MARKER_REGEX='HubSpot ticket ID: [0-9]+'

# Strip stray whitespace/newlines from the secret - a common copy-paste mistake
# that corrupts the Authorization header and causes a raw 415 from HubSpot's
# edge gateway instead of a normal JSON auth error.
HUBSPOT_API_KEY="$(printf '%s' "$HUBSPOT_API_KEY" | tr -d '[:space:]')"

hubspot_request() {
  local method="$1" url="$2" data="${3:-}"
  local args=(-s -w '\n%{http_code}' -X "$method" "$url" \
    -H "Authorization: Bearer $HUBSPOT_API_KEY" \
    -H "Content-Type: application/json")
  if [ -n "$data" ]; then
    args+=(-d "$data")
  fi
  curl "${args[@]}"
}

# Runs a hubspot_request and exits with ::error:: if the HTTP status is >= 400.
# Echoes the response body on success.
hubspot_request_or_fail() {
  local label="$1" method="$2" url="$3" data="${4:-}"
  local response http_code body
  response=$(hubspot_request "$method" "$url" "$data")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  echo "HubSpot $label response ($http_code): $body" >&2
  if [ "$http_code" -ge 400 ]; then
    echo "::error::HubSpot API returned error $http_code during $label"
    exit 1
  fi
  echo "$body"
}

get_portal_id() {
  local body
  if ! body=$(hubspot_request_or_fail "account-info lookup" GET "https://api.hubapi.com/account-info/v3/details" 2>/dev/null); then
    echo ""
    return
  fi
  echo "$body" | jq -r '.portalId // ""'
}

ticket_link_line() {
  local ticket_id="$1" portal_id
  portal_id=$(get_portal_id)
  if [ -n "$portal_id" ]; then
    echo "Link: https://app.hubspot.com/contacts/$portal_id/ticket/$ticket_id"
  else
    echo "Link: unavailable (grant the HubSpot private app the account-info.read scope to enable this)"
  fi
}

post_link_comment() {
  local ticket_id="$1"
  local body
  body=$(printf '🎫 HubSpot ticket ID: %s\n%s' "$ticket_id" "$(ticket_link_line "$ticket_id")")
  gh issue comment "$ISSUE_NUMBER" --repo "$REPO_NAME" --body "$body"
}

find_ticket_id() {
  gh api "repos/$REPO_NAME/issues/$ISSUE_NUMBER/comments" --paginate --jq '.[].body' \
    | grep -oE "$TICKET_MARKER_REGEX" \
    | tail -n1 \
    | grep -oE '[0-9]+$' || true
}

create_ticket() {
  local content="$1"
  local subject="[$REPO_NAME #$ISSUE_NUMBER] $ISSUE_TITLE"
  local payload body ticket_id
  payload=$(jq -n \
    --arg subject "$subject" \
    --arg content "$content" \
    --arg pipeline "$HUBSPOT_PIPELINE_ID" \
    '{
      properties: {
        subject: $subject,
        content: $content,
        hs_pipeline: $pipeline,
        hs_pipeline_stage: "1",
        hs_ticket_priority: "MEDIUM",
        source_type: "FORM"
      }
    }')
  body=$(hubspot_request_or_fail "ticket creation" POST "https://api.hubapi.com/crm/objects/2026-03/tickets" "$payload")
  ticket_id=$(echo "$body" | jq -r '.id')
  post_link_comment "$ticket_id"
}

append_comment_to_ticket() {
  local ticket_id="$1" comment_body="$2"
  local get_body existing_content new_content payload
  get_body=$(hubspot_request_or_fail "ticket fetch" GET "https://api.hubapi.com/crm/objects/2026-03/tickets/$ticket_id?properties=content")
  existing_content=$(echo "$get_body" | jq -r '.properties.content // ""')
  new_content=$(printf '%s\n\n---\nComment by %s on %s:\n%s' "$existing_content" "$COMMENT_AUTHOR" "$COMMENT_URL" "$comment_body")
  payload=$(jq -n --arg content "$new_content" '{properties: {content: $content}}')
  hubspot_request_or_fail "ticket update" PATCH "https://api.hubapi.com/crm/objects/2026-03/tickets/$ticket_id" "$payload" >/dev/null
}

get_closed_stage_id() {
  local body stage_id
  body=$(hubspot_request_or_fail "pipeline lookup" GET "https://api.hubapi.com/crm/v3/pipelines/tickets/$HUBSPOT_PIPELINE_ID")
  stage_id=$(echo "$body" | jq -r '[.stages[] | select(.metadata.ticketState=="CLOSED")][0].id // ""')
  if [ -z "$stage_id" ]; then
    echo "::error::Could not find a stage with ticketState=CLOSED in pipeline $HUBSPOT_PIPELINE_ID"
    exit 1
  fi
  echo "$stage_id"
}

close_ticket() {
  local ticket_id="$1" stage_id payload
  stage_id=$(get_closed_stage_id)
  payload=$(jq -n --arg stage "$stage_id" '{properties: {hs_pipeline_stage: $stage}}')
  hubspot_request_or_fail "ticket close" PATCH "https://api.hubapi.com/crm/objects/2026-03/tickets/$ticket_id" "$payload" >/dev/null
}

case "$MODE" in
  create)
    content=$(printf '%s\n\nSource: %s' "$ISSUE_BODY" "$ISSUE_URL")
    create_ticket "$content"
    ;;
  comment)
    ticket_id=$(find_ticket_id)
    if [ -z "$ticket_id" ]; then
      echo "No existing HubSpot ticket found for issue #$ISSUE_NUMBER, creating one from this comment"
      content=$(printf '%s\n\nSource: %s' "$COMMENT_BODY" "$ISSUE_URL")
      create_ticket "$content"
    else
      echo "Found existing HubSpot ticket $ticket_id, appending comment"
      append_comment_to_ticket "$ticket_id" "$COMMENT_BODY"
    fi
    ;;
  close)
    ticket_id=$(find_ticket_id)
    if [ -z "$ticket_id" ]; then
      echo "No existing HubSpot ticket found for issue #$ISSUE_NUMBER, nothing to close"
      exit 0
    fi
    echo "Found existing HubSpot ticket $ticket_id, closing it"
    close_ticket "$ticket_id"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    exit 1
    ;;
esac
