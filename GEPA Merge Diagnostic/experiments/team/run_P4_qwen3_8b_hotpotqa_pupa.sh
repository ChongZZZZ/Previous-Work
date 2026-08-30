#!/usr/bin/env bash
# Person 4 — Qwen3-8B via Together AI · HotpotQA + PUPA
# 20 runs total (9 merge + 1 NoMerge per benchmark × 2 benchmarks)
# Est. ~52h, ~$78
#
# Before running:
#   1. Sign up at https://www.together.ai/ and generate API key
#   2. export TOGETHER_API_KEY='your-key'
#   3. Ensure wiki corpus downloaded (needed for HotpotQA BM25):
#        PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py
#   4. Verify local env:
#        bash experiments/team/_verify_env.sh
#   5. Launch:
#        bash experiments/team/run_P4_qwen3_8b_hotpotqa_pupa.sh

set -e

: "${TOGETHER_API_KEY:?TOGETHER_API_KEY must be set. Get one at https://api.together.xyz/settings/api-keys}"

: "${OPENAI_API_KEY:=dummy-not-used-for-together-runs}"
export OPENAI_API_KEY

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Person 4 slice: Qwen3-8B (Together) · HotpotQA + PUPA · 20 runs"
echo "Output dir: runs/phase_a_main/{hotpotqa,pupa}/"
echo ""

MODEL=together_ai/Qwen/Qwen3-8B \
TASK_LIST="hotpotqa pupa" \
SEED_ONLY=0 \
INCLUDE_NOMERGE=yes \
RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh
