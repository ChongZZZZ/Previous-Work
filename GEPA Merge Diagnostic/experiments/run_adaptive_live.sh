#!/usr/bin/env bash
# Adaptive Merge — live re-run on Phase A's 4 benchmarks × 2 models.
#
# Validates the BehavioralAdaptiveMergePolicy + AdaptiveStartPolicy end-to-end
# on real LM calls. Compares against Phase A NoMerge baselines + best-fixed
# merge cells already in {P2,P3,P4}_result/ and runs/phase_a_main_qwen/.
#
# DOES NOT REPLACE Phase A's existing 80-cell archive. Writes to a separate
# RUNS_ROOT (default `runs/adaptive_live_v1/`) so nothing collides.
#
# ─── Required env ────────────────────────────────────────────────────────
#   PRIME_API_KEY (or PRIME_API_KEY_XIXIXI in .env.local) and PRIME_TEAM_ID:
#   route BOTH `openai/gpt-4.1-mini` and `qwen/qwen3-8b` through Prime
#   Intellect's OpenAI-compatible inference endpoint via run_dspy.py::_make_lm.
#   No direct OpenAI key required.
#
# ─── Knobs ──────────────────────────────────────────────────────────────
#   MODEL_LIST    — space-separated. Default "gpt qwen". Subset to e.g. "qwen" only.
#   TASK_LIST     — Default "hotpotqa ifbench hover musique".
#   SEEDS         — Default "0" (matches Phase A's _s0 cells exactly).
#   RUNS_ROOT     — Default "adaptive_merge/runs" (per-cell artifacts).
#   LOG_DIR       — Default "adaptive_merge/logs".
#   ADAPTIVE_FALLBACK_ALGO — Algorithm used by the wrapper only when the policy
#                            returns None (which it doesn't in current code).
#                            Default "original".
#   USE_MATURITY_GATE      — "yes" | "no". Default "yes" (G3 on).
#                            Set "no" for the G3-off variant.
#
# ─── Per-benchmark budget (paper-exact, matches Phase A) ────────────────
#   HotpotQA : 6871    MuSiQue : 6871  (mirrors HotpotMultiHop)
#   HoVer    : 7051    IFBench : 3593
#
# ─── Cost estimate (single seed, all 4 tasks, via Prime Intellect) ──────
# Calibrated from launch_2wiki_*.sh batches' measured spend:
#   gpt-4.1-mini : $0.00204 per metric call → ~$50 total across 4 tasks
#                    HotpotQA ~$14.0  IFBench ~$7.3  Hover ~$14.4  MuSiQue ~$14.0
#   qwen3-8b     : $0.00073 per metric call → ~$18 total across 4 tasks
#                    (Qwen3 with /no_think — _make_lm's default behavior;
#                     set DISABLE_NO_THINK=1 for paper-exact thinking-on at ~200x cost)
#   Total        : ~$68 / seed for the 8-cell grid (4 tasks × 2 models).
#   Wall-clock   : ~36h sequential OR ~5h fully parallel (Prime tolerated 30
#                  simultaneous calls in their probe).
#
# Phase A baselines used the same models (gpt-4.1-mini in P{2,3,4}_result/,
# qwen3-8b in runs/phase_a_main_qwen/) at seed 0, so this gives apples-to-apples
# comparison via experiments/analysis/compare_adaptive_to_phase_a.py.
#
# ─── Usage ──────────────────────────────────────────────────────────────
#   # Full 8-cell grid:
#   OPENAI_API_KEY=... PRIME_API_KEY=... PRIME_TEAM_ID=... \
#       bash experiments/run_adaptive_live.sh
#
#   # Just qwen (cheap test):
#   PRIME_API_KEY=... PRIME_TEAM_ID=... MODEL_LIST=qwen \
#       bash experiments/run_adaptive_live.sh
#
#   # Single task to validate plumbing:
#   OPENAI_API_KEY=... MODEL_LIST=gpt TASK_LIST=ifbench \
#       bash experiments/run_adaptive_live.sh
#
#   # G3-off variant for ablation:
#   ... USE_MATURITY_GATE=no RUNS_ROOT=runs/adaptive_live_v1_no_g3 \
#       bash experiments/run_adaptive_live.sh
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Pick up local API keys if present
if [ -f .env.local ]; then
    set -a; . .env.local; set +a
fi
# `:=` assigns but doesn't export. Use explicit export so the Python
# subprocess sees PRIME_API_KEY (otherwise _make_lm falls through to default
# litellm dispatch and qwen/qwen3-8b routes to OpenRouter → 401).
: "${PRIME_API_KEY:=${PRIME_API_KEY_XIXIXI:-${PRIME_API_KEY_HAHAHA:-}}}"
: "${OPENAI_API_KEY:=dummy}"
: "${PRIME_API_KEY:?Set PRIME_API_KEY (or PRIME_API_KEY_XIXIXI / PRIME_API_KEY_HAHAHA in .env.local)}"
: "${PRIME_TEAM_ID:?Set PRIME_TEAM_ID in .env.local}"
export PRIME_API_KEY PRIME_TEAM_ID OPENAI_API_KEY

: "${MODEL_LIST:=gpt qwen}"
: "${TASK_LIST:=hotpotqa ifbench hover musique}"
: "${SEEDS:=0}"
: "${RUNS_ROOT:=adaptive_merge/runs}"
: "${LOG_DIR:=adaptive_merge/logs}"
: "${ADAPTIVE_FALLBACK_ALGO:=original}"
: "${USE_MATURITY_GATE:=yes}"
# CHANGED 2026-05-01: enable plateau gate by default for v2 qwen run.
# CONFIRMED 2026-05-02: v2 vs v2.6 ablation on qwen3-8b × 4 tasks proved
# plateau ON wins decisively. v2.6 (plateau OFF) lost on 3/4 cells: ifbench
# −2.89pp, musique −2.67pp, hover −41.33pp (catastrophic prompt collapse from
# 7 stacked merges). hotpotqa unchanged. Plateau ON is now the code default
# in AdaptiveMergeConfig (use_plateau_gate=True), so this env override is
# redundant but kept for explicit documentation. Override with USE_PLATEAU_GATE=no
# to reproduce the v2.6 ablation.
: "${USE_PLATEAU_GATE:=yes}"
: "${PLATEAU_WINDOW:=3}"
: "${PLATEAU_EPS:=0.0}"

: "${BUDGET_HOTPOTQA:=6871}"
: "${BUDGET_IFBENCH:=3593}"
: "${BUDGET_HOVER:=7051}"
: "${BUDGET_MUSIQUE:=6871}"  # mirrors HotpotMultiHop structure (4 predictors)

mkdir -p "$LOG_DIR" "$RUNS_ROOT"

budget_for_task() {
    case "$1" in
        hotpotqa) echo "$BUDGET_HOTPOTQA" ;;
        ifbench)  echo "$BUDGET_IFBENCH"  ;;
        hover)    echo "$BUDGET_HOVER"    ;;
        musique)  echo "$BUDGET_MUSIQUE"  ;;
        *) echo "5000" ;;
    esac
}

run_cell() {
    local model_label="$1"   # "gpt" or "qwen"
    local task="$2"
    local seed="$3"
    local budget; budget="$(budget_for_task "$task")"
    local model_arg
    # Both models route through Prime Intellect via run_dspy.py::_make_lm
    # (auth env exported once at the top of the script).
    if [ "$model_label" = "gpt" ]; then
        model_arg="openai/gpt-4.1-mini"
    elif [ "$model_label" = "qwen" ]; then
        model_arg="qwen/qwen3-8b"
    else
        echo "[skip] unknown model: $model_label" >&2
        return 0
    fi

    local cell="${model_label}_${task}_adaptive_s${seed}"
    local run_dir="$RUNS_ROOT/$cell"
    local log="$LOG_DIR/${cell}.log"

    if [ -d "$run_dir" ] && [ -f "$run_dir/test_eval.json" ]; then
        echo "[skip] $cell already complete -> $run_dir"
        return 0
    fi

    local maturity_flag=""
    if [ "$USE_MATURITY_GATE" = "no" ]; then
        maturity_flag="--adaptive_no_maturity_gate"
    fi
    # ADDED 2026-05-01: plateau-gate flag (default on; see USE_PLATEAU_GATE
    # default in env block above).
    local plateau_flags=""
    if [ "$USE_PLATEAU_GATE" = "yes" ]; then
        plateau_flags="--adaptive_use_plateau_gate --adaptive_plateau_window $PLATEAU_WINDOW --adaptive_plateau_eps $PLATEAU_EPS"
    fi

    echo "[launch] $cell  budget=$budget  model=$model_arg  -> $log"
    PYTHONPATH=src \
    .venv/bin/python -m experiments.benchmarks.run_dspy \
        --task "$task" \
        --model "$model_arg" \
        --max_metric_calls "$budget" \
        --use_merge \
        --max_merge_invocations 15 \
        --adaptive_merge_enabled \
        $maturity_flag \
        $plateau_flags \
        --merge_algorithm "$ADAPTIVE_FALLBACK_ALGO" \
        --merge_quality \
        --run_dir "$run_dir" \
        --seed "$seed" \
        2>&1 | tee "$log"
    echo "[done] $cell"
}

for model in $MODEL_LIST; do
    for task in $TASK_LIST; do
        for seed in $SEEDS; do
            run_cell "$model" "$task" "$seed"
        done
    done
done

echo
echo "All cells complete. Test-eval scores in:"
echo "  ${RUNS_ROOT}/*/test_eval.json"
echo
echo "Compare against Phase A baselines with:"
echo "  PYTHONPATH=src .venv/bin/python -m experiments.analysis.compare_adaptive_to_phase_a \\"
echo "      --adaptive_root $RUNS_ROOT \\"
echo "      --baseline_roots P2_result/phase_a_main P3_result/phase_a_main P4_result/phase_a_main runs/phase_a_main_qwen \\"
echo "      --out adaptive_merge/compare/adaptive_live_v1_compare.md"
