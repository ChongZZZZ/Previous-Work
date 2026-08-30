#!/usr/bin/env bash
# 2WikiMultiHopQA Phase A — Qwen3-8B batch 1 (8 of 10 cells).
#
# Routes through Prime Intellect (paper-exact thinking-on sampling: temp=0.6,
# top_p=0.95, top_k=20) — see experiments/benchmarks/run_dspy.py::_make_lm.
#
# Cells in this batch (8):
#   - original × {immediate, score_plateau, budget_proportional}
#   - combine_all × {immediate, score_plateau, budget_proportional}
#   - summarize_before × immediate
#   - NoMerge
#
# Deferred to a later batch (2):
#   - summarize_before × score_plateau
#   - summarize_before × budget_proportional
#
# 4 shards × 2 cells each, ~9h critical path, ~$40 spend (10× cheaper than the
# gpt-4.1-mini batch).
#
# IMPORTANT: writes to runs/phase_a_main_qwen/ — separate from the gpt cells in
# runs/phase_a_main/ — so a stray python can't collide across models.
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

LOG_DIR="logs/2wiki_qwen_batch1"
mkdir -p "$LOG_DIR"

RUNS_ROOT="runs/phase_a_main_qwen"   # ← separate from gpt's runs/phase_a_main/
SEED="0"
TASK="2wiki"
MODEL="qwen/qwen3-8b"

launch_shard() {
    local label="$1" delay="$2" script="$3"
    local log="$LOG_DIR/${label}.log"
    echo "[launch] $label  (start delay ${delay}s)  -> $log"
    nohup bash -c "sleep $delay; $script" > "$log" 2>&1 &
    echo $! > "$LOG_DIR/${label}.pid"
}

# ── S1: original × {immediate, score_plateau} ──
S1='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=original START_ONLY="immediate score_plateau" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S2: original × budget_proportional + NoMerge ──
S2='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=original START_ONLY="budget_proportional" INCLUDE_NOMERGE=yes \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S3: combine_all × {immediate, score_plateau} ──
S3='
set -e
cd '"$ROOT"'
MODEL='"$MODEL"' TASK_LIST='"$TASK"' SEED_ONLY='"$SEED"' \
  MERGE_ALGO_ONLY=combine_all START_ONLY="immediate score_plateau" INCLUDE_NOMERGE=no \
  RUNS_ROOT='"$RUNS_ROOT"' bash experiments/run_phase_a.sh
'

# ── S4: combine_all × budget_proportional + summarize_before × immediate ──
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

# 30s stagger to spread the json.load peaks (~1 GB transient per shard).
launch_shard q1_orig_im_pl       0  "$S1"
launch_shard q2_orig_bp_nomerge 30  "$S2"
launch_shard q3_cmb_im_pl       60  "$S3"
launch_shard q4_cmb_bp_sum_im   90  "$S4"

echo
echo "All 4 Qwen batch-1 shards launched. Watch with:"
echo "  tail -f $LOG_DIR/*.log"
echo
echo "Deferred to batch 2 (run separately when ready):"
echo "  summarize_before × score_plateau"
echo "  summarize_before × budget_proportional"
echo
echo "PIDs:"
for f in "$LOG_DIR"/*.pid; do
    printf "  %-30s %s\n" "$(basename "$f" .pid)" "$(cat "$f")"
done
