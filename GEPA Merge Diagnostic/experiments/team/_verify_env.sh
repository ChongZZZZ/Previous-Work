#!/usr/bin/env bash
# Verify local environment before Phase A launch.
# Checks: venv, imports, API key reachability, gepa-artifact vendor, wiki corpus.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

FAIL=0
pass() { echo "  ✅ $1"; }
fail() { echo "  ❌ $1"; FAIL=1; }
warn() { echo "  ⚠️  $1"; }

echo "=== Python / venv ==="
if [ -f .venv/bin/python ]; then
    VER=$(.venv/bin/python --version 2>&1)
    pass "venv present: $VER"
else
    fail "venv missing — run: bash experiments/setup.sh"
fi

echo ""
echo "=== Package imports (via PYTHONPATH=src, matching production runs) ==="
PYTHONPATH=src .venv/bin/python -c "import dspy; print(f'  ✅ dspy {dspy.__version__}')" 2>&1 | grep -E "^  |Error" || fail "dspy import failed"
PYTHONPATH=src .venv/bin/python -c "import datasets; print(f'  ✅ datasets {datasets.__version__}')" 2>&1 | grep -E "^  |Error" || fail "datasets import failed"
PYTHONPATH=src .venv/bin/python -c "import bm25s; print(f'  ✅ bm25s imported')" 2>&1 | grep -E "^  |Error" || fail "bm25s import failed"
PYTHONPATH=src .venv/bin/python -c "import gepa; from gepa.strategies.merge_algorithm import MERGE_ALGORITHMS; from gepa.strategies.merge_start_policy import START_POLICIES; print(f'  ✅ gepa local (algos: {list(MERGE_ALGORITHMS)}, policies: {list(START_POLICIES)})')" 2>&1 | grep -E "^  |Error" || fail "gepa local import failed"

echo ""
echo "=== Vendored gepa-artifact (paper benchmarks) ==="
if [ -d experiments/vendor/gepa-artifact/gepa_artifact ]; then
    pass "experiments/vendor/gepa-artifact/ present"
    for bench in IFBench papillon hotpotQA hover; do
        MOD_PATH=$(ls experiments/vendor/gepa-artifact/gepa_artifact/benchmarks/$bench/__init__.py 2>/dev/null | head -1)
        if [ -n "$MOD_PATH" ]; then
            pass "benchmark $bench"
        else
            warn "benchmark $bench not found at vendor/gepa-artifact"
        fi
    done
else
    fail "vendor/gepa-artifact/ missing — run: bash experiments/setup_benchmarks.sh"
fi

echo ""
echo "=== Wiki corpus (HotpotQA + HoVer) ==="
if [ -d experiments/vendor/gepa-artifact/gepa_artifact/benchmarks/hover/bm25s_retriever ]; then
    SIZE=$(du -sh experiments/vendor/gepa-artifact/gepa_artifact/benchmarks/hover/bm25s_retriever/ 2>/dev/null | awk '{print $1}')
    pass "BM25 index present ($SIZE) — HotpotQA + HoVer ready"
else
    warn "BM25 index missing (HotpotQA/HoVer will fail). Run: PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py"
fi

echo ""
echo "=== API keys ==="
if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "dummy-not-used-for-together-runs" ]; then
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY")
    if [ "$HTTP" = "200" ]; then
        pass "OPENAI_API_KEY is valid (HTTP 200)"
    else
        fail "OPENAI_API_KEY rejected (HTTP $HTTP)"
    fi
else
    warn "OPENAI_API_KEY not set (needed for P1/P2 gpt-4.1-mini slices)"
fi

if [ -n "$TOGETHER_API_KEY" ]; then
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" https://api.together.xyz/v1/models -H "Authorization: Bearer $TOGETHER_API_KEY")
    if [ "$HTTP" = "200" ]; then
        pass "TOGETHER_API_KEY is valid (HTTP 200)"
    else
        fail "TOGETHER_API_KEY rejected (HTTP $HTTP)"
    fi
else
    warn "TOGETHER_API_KEY not set (needed for P3/P4 Qwen3-8B slices)"
fi

echo ""
if [ $FAIL -eq 0 ]; then
    echo "✅ Env verified. Next: run bash experiments/team/_smoke_ifbench_nano.sh for a cheap end-to-end check."
else
    echo "❌ Fix the above before launching your Phase A slice."
    exit 1
fi
