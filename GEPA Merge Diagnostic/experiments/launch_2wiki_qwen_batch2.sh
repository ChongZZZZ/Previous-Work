#!/usr/bin/env bash
# 2WikiMultiHopQA Phase A — Qwen3-8B batch 2 (the 2 deferred cells).
#
# Cells:
#   - summarize_before × score_plateau
#   - summarize_before × budget_proportional
#
# 2 shards × 1 cell each, ~3-4h critical path, ~$10 spend.
# Writes to runs/phase_a_main_qwen/2wiki/ (separate from gpt cells).
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env.local ]; then
    set -a; . .env.local; set +a
fi
: "${PRIME_API_KEY:=$PRIME_API_KEY_XIXIXI}"
: "${PRIME_API_KEY:?Set PRIME_API_KEY (or PRIME_API_KEY_XIXIXI in .env.local)}"
: "${PRIME_TEAM_ID:?Set PRIME_TEAM_ID in .env.local}"
: "${OPENAI_API_KEY:=dummy}"
export PRIME_API_KEY PRIME_TEAM_ID OPENAI_API_KEY

LOG_DIR="logs/2wiki_qwen_batch2"
mkdir -p "$LOG_DIR"

RUNS_ROOT="runs/phase_a_main_qwen"
SEED="0"
TASK="2wiki"
MODEL="qwen/qwen3-8b"

launch_shard() {
    local label="$1" delay="$2" start="$3"
    local log="$LOG_DIR/${label}.log"
    local script="
        set -e
        cd $ROOT
        MODEL=$MODEL TASK_LIST=$TASK SEED_ONLY=$SEED \\
          MERGE_ALGO_ONLY=summarize_before START_ONLY=$start INCLUDE_NOMERGE=no \\
          RUNS_ROOT=$RUNS_ROOT bash experiments/run_phase_a.sh
    "
    echo "[launch] $label  (start=$start delay=${delay}s)  -> $log"
    nohup bash -c "sleep $delay; $script" > "$log" 2>&1 &
    echo $! > "$LOG_DIR/${label}.pid"
}

launch_shard qb2_sum_plat   0  score_plateau
launch_shard qb2_sum_bp    30  budget_proportional

echo
echo "PIDs:"
for f in "$LOG_DIR"/*.pid; do
    printf "  %-30s %s\n" "$(basename "$f" .pid)" "$(cat "$f")"
done
