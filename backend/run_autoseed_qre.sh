#!/bin/bash
# QRE-focused generator — runs until QRE gaps are filled, then switches to full
LOG="/home/bhanu/Desktop/pariksha365/backend/autoseed.log"
cd /home/bhanu/Desktop/pariksha365/backend

LAST_POOL=$(python3 -c "import json; d=json.load(open('scripts/auto_seed/state.json')); print(d['total_questions'])" 2>/dev/null || echo 0)
echo "[$(date)] QRE-focused wrapper started. Pool=$LAST_POOL" >> "$LOG"

while true; do
    python3 -m scripts.auto_seed.state > /dev/null 2>&1
    CURRENT=$(python3 -c "import json; d=json.load(open('scripts/auto_seed/state.json')); print(d['total_questions'])" 2>/dev/null || echo 0)

    if [ "$CURRENT" -ge 50000 ]; then
        echo "[$(date)] Target 50k reached! Pool=$CURRENT. Stopping." >> "$LOG"
        break
    fi

    echo "[$(date)] Starting QRE generator. Pool=$CURRENT" >> "$LOG"
    # 20 topics/wave, 2 workers — QRE topics will dominate priority queue
    python3 -u -m scripts.auto_seed.auto_run --topics 20 --workers 2 --target 50000 >> "$LOG" 2>&1

    EXIT_CODE=$?
    python3 -m scripts.auto_seed.state > /dev/null 2>&1
    NEW=$(python3 -c "import json; d=json.load(open('scripts/auto_seed/state.json')); print(d['total_questions'])" 2>/dev/null || echo 0)
    DELTA=$((NEW - LAST_POOL))

    echo "[$(date)] Generator exited (code=$EXIT_CODE). Pool=$NEW delta=+$DELTA" >> "$LOG"

    if [ "$DELTA" -ge 500 ]; then
        echo "[$(date)] Committing +$DELTA questions..." >> "$LOG"
        git add seeds/ scripts/auto_seed/state.json scripts/auto_seed/gates.py >> "$LOG" 2>&1
        git commit -m "$(printf 'Auto-seed QRE focus: +%d questions (pool=%d)\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>' "$DELTA" "$NEW")" >> "$LOG" 2>&1
        LAST_POOL=$NEW
        echo "[$(date)] Committed." >> "$LOG"
    fi

    [ "$NEW" -ge 50000 ] && break
    sleep 5
done
