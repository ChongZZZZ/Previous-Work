#!/usr/bin/env bash
# 2WikiMultiHopQA Phase A — gpt-4.1-mini batch 2 (the 3 deferred cells).
#
# Cells:
#   - original × score_plateau          (re-run; batch 1's run was contaminated
#                                        by an orphan Qwen3 process; safe now)
#   - summarize_before × score_plateau  (deferred from batch 1)
#   - summarize_before × budget_proportional  (deferred from batch 1)
#
# 3 shards × 1 cell each, ~4h critical path, ~$42 spend. Per-shard RAM ~1.5 GB.
#
# Idempotent — completed cells are skipped on rerun. Logs in
# logs/2wiki_phase_a_batch2/.
#
# Usage:
#   bash experiments/launch_2wiki_phase_a_batch2.sh
#
# Stop everything:
#   for f in logs/2wiki_phase_a_batch2/*.pid; do kill $(cat "$f") 2>/dev/null; done
#   pkill -f "experiments.benchmarks.run_dspy.*2wiki"
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

LOG_DIR="logs/2wiki_phase_a_batch2"
mkdir -p "$LOG_DIR"

RUNS_ROOT="runs/phase_a_main"
SEED="0"
TASK="2wiki"
MODEL="openai/gpt-4.1-mini"

# Wipe the contaminated cell so run_phase_a.sh doesn't skip it.
CONTAMINATED="$RUNS_ROOT/2wiki/original_score_plateau_s0"
if [ -d "$CONTAMINATED" ]; then
    echo "[clean] removing contaminated cell: $CONTAMINATED"
    rm -rf "$CONTAMINATED"
fi

launch_shard() {
    local label="$1"
    local delay="$2"
    local algo="$3"
    local start="$4"
    local log="$LOG_DIR/${label}.log"
    local script="
        set -e
        cd $ROOT
        MODEL=$MODEL TASK_LIST=$TASK SEED_ONLY=$SEED \\
          MERGE_ALGO_ONLY=$algo START_ONLY=$start INCLUDE_NOMERGE=no \\
          RUNS_ROOT=$RUNS_ROOT bash experiments/run_phase_a.sh
    "
    echo "[launch] $label  (algo=$algo start=$start delay=${delay}s)  -> $log"
    nohup bash -c "sleep $delay; $script" > "$log" 2>&1 &
    echo $! > "$LOG_DIR/${label}.pid"
}

# Stagger by 30s each so json.load peaks don't pile up.
launch_shard b2_orig_plat       0  original         score_plateau
launch_shard b2_sum_plat       30  summarize_before score_plateau
launch_shard b2_sum_bp         60  summarize_before budget_proportional

echo
echo "All 3 batch-2 shards launched. Watch with:"
echo "  tail -f $LOG_DIR/*.log"
echo
echo "Critical path ~4h — reminder: caffeinate -i & in another terminal if you'll close the lid."
echo
echo "PIDs:"
for f in "$LOG_DIR"/*.pid; do
    printf "  %-30s %s\n" "$(basename "$f" .pid)" "$(cat "$f")"
done
