#!/usr/bin/env bash
# Launch the 2WikiMultiHopQA Phase A — gpt-4.1-mini batch 1.
#
# Scope: 8 of 10 gpt-4.1-mini cells. Deferred to a later round:
#   - summarize_before × score_plateau
#   - summarize_before × budget_proportional
#
# 4 shards × 2 cells each, ~9.2h critical path, ~$112 spend.
# Per-shard RAM ~1.5 GB (loader holds full 167K train.json). 4 shards ≈ 6 GB
# sustained — tight on 8 GB but safe with 30s startup staggering so shards
# don't all hit json.load simultaneously.
#
# Shard layout:
#   S1 — original × {immediate, score_plateau}                    (2 cells)
#   S2 — original × budget_proportional + NoMerge                 (2 cells)
#   S3 — combine_all × {immediate, score_plateau}                 (2 cells)
#   S4 — combine_all × budget_proportional + summarize_before × immediate
#                                                                 (2 cells)
#
# Idempotent — completed cells are skipped on rerun. Logs in logs/2wiki_phase_a/.
#
# Usage:
#   bash experiments/launch_2wiki_phase_a.sh
#   tail -f logs/2wiki_phase_a/*.log
#
# Stop everything:
#   for f in logs/2wiki_phase_a/*.pid; do kill $(cat "$f") 2>/dev/null; done
#   pkill -f "experiments.benchmarks.run_dspy.*2wiki"
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Source Prime credentials from .env.local
if [ -f .env.local ]; then
    set -a; . .env.local; set +a
fi
: "${PRIME_API_KEY:=$PRIME_API_KEY_XIXIXI}"
: "${PRIME_API_KEY:?Set PRIME_API_KEY (or PRIME_API_KEY_XIXIXI in .env.local)}"
: "${PRIME_TEAM_ID:?Set PRIME_TEAM_ID in .env.local}"

# OpenAI key isn't actually used (Prime intercepts), but the runner asserts it.
: "${OPENAI_API_KEY:=dummy}"
export PRIME_API_KEY PRIME_TEAM_ID OPENAI_API_KEY

LOG_DIR="logs/2wiki_phase_a"
mkdir -p "$LOG_DIR"

RUNS_ROOT="runs/phase_a_main"
SEED="0"
TASK="2wiki"
MODEL="openai/gpt-4.1-mini"

# Build a multi-line bash payload that runs one or more pass(es) of run_phase_a.sh.
# `delay` lets us stagger startup so shards don't all hit json.load at once
# (each shard briefly peaks at ~1 GB during dataset parse).
launch_shard() {
    local label="$1"
    local delay="$2"
    local script="$3"
    local log="$LOG_DIR/${label}.log"
    echo "[launch] $label (start delay ${delay}s) -> $log"
    nohup bash -c "sleep $delay; $script" > "$log" 2>&1 &
    echo $! > "$LOG_DIR/${label}.pid"
}

# ── S1: original × {immediate, score_plateau}
S1='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=original START_ONLY="immediate score_plateau" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S2: original × budget_proportional + NoMerge
S2='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=original START_ONLY="budget_proportional" INCLUDE_NOMERGE=yes \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S3: combine_all × {immediate, score_plateau}
S3='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=combine_all START_ONLY="immediate score_plateau" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S4: combine_all × budget_proportional + summarize_before × immediate (sequential)
S4='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=combine_all START_ONLY="budget_proportional" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=summarize_before START_ONLY="immediate" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# Stagger by 30s each — keeps the simultaneous json.load peak from
# spiking RAM all at once. Total stagger window is 90s.
launch_shard s1_orig_im_pl       0  "$S1"
launch_shard s2_orig_bp_nomerge  30 "$S2"
launch_shard s3_cmb_im_pl        60 "$S3"
launch_shard s4_cmb_bp_sum_im    90 "$S4"

echo
echo "All 4 shards launched. Watch with:"
echo "  tail -f $LOG_DIR/*.log"
echo
echo "Deferred to next round (run separately when ready):"
echo "  summarize_before × score_plateau"
echo "  summarize_before × budget_proportional"
echo
echo "PIDs:"
for f in "$LOG_DIR"/*.pid; do
    printf "  %-30s %s\n" "$(basename "$f" .pid)" "$(cat "$f")"
done
