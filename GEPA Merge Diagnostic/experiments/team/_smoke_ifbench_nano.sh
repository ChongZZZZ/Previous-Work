#!/usr/bin/env bash
# Cheap end-to-end smoke test — IFBench on gpt-5-nano, tiny budget.
# Costs ~$0.05, takes ~5-10 min. Confirms full pipeline is alive before
# committing to a multi-hour Phase A slice.
#
# Requires: OPENAI_API_KEY (even if you're on the Qwen3 slice — this smoke
# is just for local validation, not your actual Phase A run).

set -e

: "${OPENAI_API_KEY:?OPENAI_API_KEY must be set for the cheap nano smoke}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

RUN_DIR="runs/_local_smoke_$(date +%Y%m%d_%H%M%S)"
echo "Running IFBench nano smoke → $RUN_DIR"
echo ""

PYTHONPATH=src .venv/bin/python -m experiments.benchmarks.run_dspy \
    --task ifbench \
    --model openai/gpt-5-nano \
    --use_merge --merge_algorithm original --merge_start immediate \
    --merge_quality \
    --run_dir "$RUN_DIR" \
    --max_metric_calls 300 \
    --val_size 15 --train_size 20 --seed 0

echo ""
if [ -f "$RUN_DIR/best_candidate.json" ]; then
    echo "✅ Smoke passed. Sidecars in $RUN_DIR/:"
    ls "$RUN_DIR/"
    echo ""
    echo "You're ready to run your Phase A slice:"
    echo "  bash experiments/team/run_P<1|2|3|4>_*.sh"
else
    echo "❌ Smoke failed — best_candidate.json missing."
    exit 1
fi
