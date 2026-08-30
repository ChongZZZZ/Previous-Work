#!/usr/bin/env bash
# Person 1 — gpt-4.1-mini · HoVer + PUPA
# 20 runs total (9 merge configs + 1 NoMerge per benchmark × 2 benchmarks)
# Est. ~62h, ~$150
#
# Before running:
#   1. Generate your own OpenAI API key at https://platform.openai.com/api-keys
#   2. export OPENAI_API_KEY='sk-proj-your-key'
#   3. Verify local env:
#        bash experiments/team/_verify_env.sh
#   4. (Optional) small smoke:
#        bash experiments/team/_smoke_ifbench_nano.sh
#   5. Launch this script:
#        bash experiments/team/run_P1_gpt41mini_hover_pupa.sh

set -e

: "${OPENAI_API_KEY:?OPENAI_API_KEY must be set. Get your own at https://platform.openai.com/api-keys}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Person 1 slice: gpt-4.1-mini · HoVer + PUPA · 20 runs"
echo "Output dir: runs/phase_a_main/{hover,pupa}/"
echo ""

MODEL=openai/gpt-4.1-mini \
TASK_LIST="hover pupa" \
SEED_ONLY=0 \
INCLUDE_NOMERGE=yes \
RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh
