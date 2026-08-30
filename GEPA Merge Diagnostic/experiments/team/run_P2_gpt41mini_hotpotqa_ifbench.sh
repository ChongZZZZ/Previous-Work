#!/usr/bin/env bash
# Person 2 — gpt-4.1-mini · HotpotQA + IFBench
# 20 runs total (9 merge + 1 NoMerge per benchmark × 2 benchmarks)
# Est. ~63h, ~$155
#
# Before running:
#   1. Generate your own OpenAI API key at https://platform.openai.com/api-keys
#   2. export OPENAI_API_KEY='sk-proj-your-key'
#   3. Ensure wiki corpus downloaded (needed for HotpotQA BM25):
#        PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py
#   4. Verify local env:
#        bash experiments/team/_verify_env.sh
#   5. Launch:
#        bash experiments/team/run_P2_gpt41mini_hotpotqa_ifbench.sh

set -e

: "${OPENAI_API_KEY:?OPENAI_API_KEY must be set. Get your own at https://platform.openai.com/api-keys}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Person 2 slice: gpt-4.1-mini · HotpotQA + IFBench · 20 runs"
echo "Output dir: runs/phase_a_main/{hotpotqa,ifbench}/"
echo ""

MODEL=openai/gpt-4.1-mini \
TASK_LIST="hotpotqa ifbench" \
SEED_ONLY=0 \
INCLUDE_NOMERGE=yes \
RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh
