#!/usr/bin/env bash
# Person 3 — Qwen3-8B via Together AI · HoVer + IFBench
# 20 runs total (9 merge + 1 NoMerge per benchmark × 2 benchmarks)
# Est. ~62h, ~$98
#
# Before running:
#   1. Sign up at https://www.together.ai/ and generate API key
#   2. export TOGETHER_API_KEY='your-key'
#   3. Ensure wiki corpus downloaded (needed for HoVer BM25):
#        PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py
#   4. Verify local env:
#        bash experiments/team/_verify_env.sh
#   5. Launch:
#        bash experiments/team/run_P3_qwen3_8b_hover_ifbench.sh
#
# Note: LiteLLM uses TOGETHER_API_KEY env var automatically when model has
# the together_ai/ prefix. No OpenAI key needed for this slice.

set -e

: "${TOGETHER_API_KEY:?TOGETHER_API_KEY must be set. Get one at https://api.together.xyz/settings/api-keys}"

# Pass a dummy value for OPENAI_API_KEY since run_phase_a.sh requires it.
# LiteLLM will route gpt-5-nano/gpt-4.1-mini via this, but we're using Qwen so it's never called.
: "${OPENAI_API_KEY:=dummy-not-used-for-together-runs}"
export OPENAI_API_KEY

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Person 3 slice: Qwen3-8B (Together) · HoVer + IFBench · 20 runs"
echo "Output dir: runs/phase_a_main/{hover,ifbench}/"
echo ""

MODEL=together_ai/Qwen/Qwen3-8B \
TASK_LIST="hover ifbench" \
SEED_ONLY=0 \
INCLUDE_NOMERGE=yes \
RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh
