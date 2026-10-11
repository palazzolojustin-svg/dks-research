#!/bin/bash
# Snapshot live (in-progress) scrape output into data/pages, re-run aggregation, commit and push.
cd "$(dirname "$0")/.."
cp live/pages/*.jsonl data/pages/ 2>/dev/null
python3 scripts/aggregate.py > logs/aggregate.log 2>&1
cd ../.. && git add ALT_DATA/footlocker_discounts && git commit -qm "Foot Locker scrape: progress snapshot $(date -u +%F' '%H:%M)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HFkAdzRDGd38z4GhS4jFep" && git push -q -u origin claude/pensive-volta-08c4uz
