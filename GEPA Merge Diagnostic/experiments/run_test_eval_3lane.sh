#!/usr/bin/env bash
# 3-lane parallel test-eval launcher (one OR key per lane).
#
# Routes everything through OpenRouter so a single OR balance pays for all.
# Each lane runs sequentially within itself; lanes run in parallel.
#
# Lanes:
#   HOTPOT       → P1 hover × gpt-4.1-mini  (10 cells, ~$10)
#   PUPA         → musique × gpt-4.1-mini   (10 cells, ~$10)
#   PUPA_THINK   → musique × qwen3-8b       (10 cells, ~$1)
#
# Output: each cell drops a `test_eval.json` next to its `best_candidate.json`,
# and each lane writes a per-lane CSV under experiments/analysis/output/.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Load .env.local for OPENROUTER_API_KEY_{HOTPOT,PUPA,PUPA_THINK}.
if [ -f .env.local ]; then
    set -a
    . ./.env.local
    set +a
fi

: "${OPENROUTER_API_KEY_HOTPOT:?missing OR HOTPOT key}"
: "${OPENROUTER_API_KEY_PUPA:?missing OR PUPA key}"
: "${OPENROUTER_API_KEY_PUPA_THINK:?missing OR PUPA_THINK key}"

OUT_DIR="experiments/analysis/output"
mkdir -p "$OUT_DIR" logs

PYBIN=".venv/bin/python"
EVAL_MOD="experiments.analysis.eval_best_on_test"
PYPATH="src:experiments/vendor/gepa-artifact"

run_lane() {
    local lane_name="$1"
    local key="$2"
    local runs_root="$3"
    local out_csv="$4"
    local log="logs/test_eval_${lane_name}.log"

    echo "[$lane_name] launching → $runs_root  (csv=$out_csv, log=$log)"
    OPENROUTER_API_KEY="$key" \
        PYTHONPATH="$PYPATH" \
        "$PYBIN" -m "$EVAL_MOD" \
            --runs_root "$runs_root" \
            --out_csv "$out_csv" \
            --force_openrouter \
            > "$log" 2>&1 &
    local pid=$!
    echo "[$lane_name] PID=$pid"
    echo "$pid" > "logs/test_eval_${lane_name}.pid"
}

run_lane HOTPOT     "$OPENROUTER_API_KEY_HOTPOT"     \
         P1_result/phase_a_main/hover                \
         "$OUT_DIR/test_eval_p1_hover.csv"

run_lane PUPA       "$OPENROUTER_API_KEY_PUPA"       \
         runs/musique/gpt41mini                      \
         "$OUT_DIR/test_eval_musique_gpt41mini.csv"

run_lane PUPA_THINK "$OPENROUTER_API_KEY_PUPA_THINK" \
         runs/musique/qwen3_8b                       \
         "$OUT_DIR/test_eval_musique_qwen3_8b.csv"

echo ""
echo "All 3 lanes launched. Tail with:"
echo "  tail -f logs/test_eval_HOTPOT.log logs/test_eval_PUPA.log logs/test_eval_PUPA_THINK.log"
echo ""
echo "Wait for all lanes:"
echo "  wait \$(cat logs/test_eval_*.pid)"
