#!/usr/bin/env bash
# One-time setup: wire SpineRadiology publish notifications to a Telegram bot.
#
# What it does (no secret is stored in this file):
#   1. Prompts you to paste the bot token (hidden input).
#   2. Reads getUpdates to auto-detect YOUR chat id  -> you must have tapped
#      "Start" / sent a message to the bot first (e.g. t.me/SpineRadiologyBot).
#   3. Sets the repo secrets TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID via gh.
#   4. Sends a test message so you can confirm it works.
#
# Re-run any time you rotate the token. Requires: gh (authed to the repo), curl, python3.
set -euo pipefail

REPO="tech524tintillo/spineradiology"

read -rsp "Paste the bot token (input hidden): " TG_TOKEN; echo
if [ -z "${TG_TOKEN}" ]; then echo "No token entered. Aborting."; exit 1; fi

echo "Looking up your chat id from recent messages to the bot…"
CHAT_ID="$(curl -fsS "https://api.telegram.org/bot${TG_TOKEN}/getUpdates" \
  | python3 -c 'import sys,json
d=json.load(sys.stdin)
ids=[u["message"]["chat"]["id"] for u in d.get("result",[]) if "message" in u]
print(ids[-1] if ids else "")')"

if [ -z "${CHAT_ID}" ]; then
  echo "Could not find a chat id. Open the bot in Telegram (e.g. t.me/SpineRadiologyBot),"
  echo "tap Start / send any message, then re-run this script."
  exit 1
fi
echo "Detected chat id: ${CHAT_ID}"

printf '%s' "${TG_TOKEN}" | gh secret set TELEGRAM_BOT_TOKEN --repo "${REPO}"
printf '%s' "${CHAT_ID}"  | gh secret set TELEGRAM_CHAT_ID  --repo "${REPO}"
echo "Repo secrets set on ${REPO}."

echo "Sending a test message…"
curl -fsS -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHAT_ID}" \
  --data-urlencode "text=✅ SpineRadiology publish notifications are wired up. You'll get a ping here whenever an editor edit goes live." \
  >/dev/null && echo "Test message sent — check Telegram." || echo "Test send failed."

unset TG_TOKEN
echo "Done."
