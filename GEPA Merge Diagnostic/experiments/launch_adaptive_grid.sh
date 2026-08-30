#!/usr/bin/env bash
# Adaptive Merge live re-run — fan-out launcher for the 7 cells beyond the smoke.
#
# Wraps `run_adaptive_live.sh` to launch each cell in its own nohup subshell so
# they run concurrently. Each cell writes to its own log file. Cells with a
# completed `test_eval.json` are skipped automatically (so re-running this
# script is safe and idempotent).
#
# ─── Modes ──────────────────────────────────────────────────────────────
#   $1 = "all"       (default) — all 7 remaining cells
#   $1 = "qwen-only"           — 3 qwen cells (~$15, ~5h critical path)
#   $1 = "gpt-only"            — 4 gpt-4.1-mini cells (~$49, ~5h critical path)
#
# ─── Required env (sourced from .env.local automatically) ───────────────
#   PRIME_API_KEY (or PRIME_API_KEY_XIXIXI / PRIME_API_KEY_HAHAHA)
#   PRIME_TEAM_ID
#
# ─── Cells launched ─────────────────────────────────────────────────────
#   qwen × {hotpotqa, hover, musique}                           [3 cells]
#   gpt-4.1-mini × {hotpotqa, ifbench, hover, musique}          [4 cells]
#   Total: 7 cells. (The qwen × ifbench smoke is already running and is
#                    auto-skipped if its test_eval.json exists.)
#
# ─── Cost / wall-clock estimate ─────────────────────────────────────────
#   qwen-only : ~$15  /  ~5h critical path  /  ~12h CPU-time
#   gpt-only  : ~$49  /  ~5h critical path  /  ~12h CPU-time
#   all       : ~$64  /  ~5h critical path  /  ~24h CPU-time
#
# ─── Stagger ────────────────────────────────────────────────────────────
# 30 s between cell launches to avoid thundering-herd on Prime auth + dspy
# import. Cells then run their full optimization in parallel.
#
# ─── Stopping ───────────────────────────────────────────────────────────
# Per-cell PIDs are written to adaptive_merge/logs/pids/<cell>.pid so any
# single cell can be killed cleanly:
#   kill $(cat adaptive_merge/logs/pids/qwen_hotpotqa_adaptive_s0.pid)
#
# ─── Usage ──────────────────────────────────────────────────────────────
#   # Cheap-first: just the qwen cells (~$15)
#   bash experiments/launch_adaptive_grid.sh qwen-only
#
#   # Then the gpt cells (~$49)
#   bash experiments/launch_adaptive_grid.sh gpt-only
#
#   # Or fire all 7 at once (~$64)
#   bash experiments/launch_adaptive_grid.sh all
#
# After launching, monitor via:
#   tail -F adaptive_merge/logs/*.log
#   ls adaptive_merge/runs/*/test_eval.json    # cells that have finished
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env.local ]; then
    set -a; . .env.local; set +a
fi
: "${PRIME_API_KEY:=${PRIME_API_KEY_XIXIXI:-${PRIME_API_KEY_HAHAHA:-}}}"
: "${OPENAI_API_KEY:=dummy}"
: "${PRIME_API_KEY:?Set PRIME_API_KEY (or PRIME_API_KEY_XIXIXI / PRIME_API_KEY_HAHAHA in .env.local)}"
: "${PRIME_TEAM_ID:?Set PRIME_TEAM_ID in .env.local}"
export PRIME_API_KEY PRIME_TEAM_ID OPENAI_API_KEY

MODE="${1:-all}"
LOG_DIR="adaptive_merge/logs"
PID_DIR="$LOG_DIR/pids"
RUNS_ROOT="adaptive_merge/runs"
mkdir -p "$LOG_DIR" "$PID_DIR" "$RUNS_ROOT"

launch_cell() {
    local model_label="$1"   # "gpt" or "qwen"
    local task="$2"
    local delay="$3"
    local cell="${model_label}_${task}_adaptive_s0"
    local log="$LOG_DIR/${cell}.log"
    local pid_file="$PID_DIR/${cell}.pid"

    if [ -f "$RUNS_ROOT/$cell/test_eval.json" ]; then
        echo "[skip] $cell already complete -> $RUNS_ROOT/$cell/test_eval.json"
        return 0
    fi
    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "[skip] $cell already running (pid $(cat "$pid_file"))"
        return 0
    fi

    echo "[launch] $cell  delay=${delay}s  -> $log"
    nohup bash -c "sleep $delay; MODEL_LIST=$model_label TASK_LIST=$task SEEDS=0 \
        bash experiments/run_adaptive_live.sh" > "$log" 2>&1 &
    echo $! > "$pid_file"
}

delay=0
case "$MODE" in
    qwen-only|all)
        # CHANGED 2026-05-01: added ifbench. Old comment said qwen×ifbench
        # was the smoke and auto-skipped; v2 run starts fresh with all 4.
        launch_cell qwen hotpotqa "$delay"; delay=$((delay+30))
        launch_cell qwen ifbench  "$delay"; delay=$((delay+30))
        launch_cell qwen hover    "$delay"; delay=$((delay+30))
        launch_cell qwen musique  "$delay"; delay=$((delay+30))
        ;;
esac
case "$MODE" in
    gpt-only|all)
        launch_cell gpt hotpotqa "$delay"; delay=$((delay+30))
        launch_cell gpt ifbench  "$delay"; delay=$((delay+30))
        launch_cell gpt hover    "$delay"; delay=$((delay+30))
        launch_cell gpt musique  "$delay"; delay=$((delay+30))
        ;;
    qwen-only)
        ;;
    *)
        if [ "$MODE" != "all" ] && [ "$MODE" != "qwen-only" ] && [ "$MODE" != "gpt-only" ]; then
            echo "[error] unknown mode: $MODE  (use: all | qwen-only | gpt-only)" >&2
            exit 1
        fi
        ;;
esac

echo
echo "Launched. Monitor with:"
echo "  tail -F adaptive_merge/logs/*adaptive_s0.log"
echo
echo "Watch completion (cells with test_eval.json have finished):"
echo "  watch -n 30 'ls adaptive_merge/runs/*/test_eval.json 2>/dev/null'"
echo
echo "When all complete, generate comparison report:"
echo "  PYTHONPATH=src .venv/bin/python -m experiments.analysis.compare_adaptive_to_phase_a \\"
echo "      --adaptive_root adaptive_merge/runs \\"
echo "      --baseline_roots P2_result/phase_a_main P3_result/phase_a_main P4_result/phase_a_main runs/phase_a_main_qwen \\"
echo "      --out adaptive_merge/compare/adaptive_live_v1_compare.md"
