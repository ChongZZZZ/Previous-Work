# Team Onboarding — Phase A (4-person split)

Welcome. This guide gets you from zero → running your Phase A slice in
~30 min. Read [../PHASE_A_PLAN.md](../PHASE_A_PLAN.md) first for the
overall plan and the scientific context.

---

## Your assignment

| You are | Model | Benchmarks | Runs | Est. time | Est. cost | Script |
|---|---|---|---|---|---|---|
| **P1** | gpt-4.1-mini | HoVer + PUPA | 20 | ~62h | ~$190 | `run_P1_gpt41mini_hover_pupa.sh` |
| **P2** | gpt-4.1-mini | HotpotQA + IFBench | 20 | ~63h | ~$210 | `run_P2_gpt41mini_hotpotqa_ifbench.sh` |
| **P3** | Qwen3-8B (Together) | HoVer + IFBench | 20 | ~62h | ~$43 | `run_P3_qwen3_8b_hover_ifbench.sh` |
| **P4** | Qwen3-8B (Together) | HotpotQA + PUPA | 20 | ~52h | ~$51 | `run_P4_qwen3_8b_hotpotqa_pupa.sh` |

Wall-clock is overnight × 2 + daytime bridging. Plan to launch
**Saturday 4/25** and have results by **Monday 4/27 evening**.

---

## Step 0 — Clone + setup (one-time, ~5 min)

```bash
git clone <this-repo> gepa_merge
cd gepa_merge
bash experiments/setup.sh
```

That installs `uv`, creates `.venv`, sync's dependencies, clones
`gepa-ai/gepa-artifact` into `experiments/vendor/`, and scrubs macOS
duplicate files.

---

## Step 1 — Get your API key

### P1 / P2 (gpt-4.1-mini)
1. Go to https://platform.openai.com/api-keys
2. Generate a **new** key (do NOT share keys between teammates — avoids
   RPM throttling)
3. `export OPENAI_API_KEY='sk-proj-...'` in your shell
4. **Fund the account** — Phase A will cost ~$190-210 for your slice.
   Add $250 credit under Billing to cover slice + buffer for retries.

### P3 / P4 (Qwen3-8B via Together AI)
1. Sign up at https://www.together.ai/
2. Go to https://api.together.xyz/settings/api-keys, generate a key
3. `export TOGETHER_API_KEY='...'` in your shell
4. Add ~$60 credit (your slice costs ~$43-51 + buffer; P4 also runs
   Phase B.2 scaling on 4B+14B so +$13)

---

## Step 2 — Wiki corpus (P2, P3, P4 only — skip if your benches don't need it)

HotpotQA and HoVer use BM25 over the Wikipedia 2017 abstracts (608 MB
download + ~15 min BM25 index build).

```bash
PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py
```

Idempotent — skips if cached. **P1 can skip this** (PUPA and HoVer —
wait actually P1 has HoVer, so yes P1 also needs this). Only the
IFBench+PUPA-only person could skip, but that's nobody in our split.

**In short: everyone runs `warmup_wiki_corpus.py` once.**

---

## Step 3 — Verify your env (~30 sec)

```bash
bash experiments/team/_verify_env.sh
```

Output tells you what's missing. Common fixes:
- `dspy import failed` → `uv pip install --prerelease=allow dspy`
- `gepa local import failed` → `uv pip install -e .` (re-install editable)
- `datasets corrupted` → `uv pip install --force-reinstall --no-deps 'datasets<4' --python .venv/bin/python`
- API key rejected → check it's the new one you just generated, no whitespace

---

## Step 4 — Cheap local smoke (~$0.05, ~5-10 min)

```bash
bash experiments/team/_smoke_ifbench_nano.sh
```

This runs IFBench on **gpt-5-nano** (regardless of which model you'll
actually use in Phase A). Purpose: confirm the whole pipeline — optimizer,
retrieval, metrics, sidecar writing — works end-to-end on your machine
before you commit to a 60-hour Phase A slice.

Expected: `✅ Smoke passed. Sidecars in runs/_local_smoke_TIMESTAMP/`.

---

## Step 5 — Launch your slice

From `gepa_merge/` root:

```bash
# P1
bash experiments/team/run_P1_gpt41mini_hover_pupa.sh

# P2
bash experiments/team/run_P2_gpt41mini_hotpotqa_ifbench.sh

# P3
bash experiments/team/run_P3_qwen3_8b_hover_ifbench.sh

# P4
bash experiments/team/run_P4_qwen3_8b_hotpotqa_pupa.sh
```

These scripts are just thin wrappers around `experiments/run_phase_a.sh`
with your benchmarks + model pre-filled. Each one of 20 runs streams its
own log to stdout + writes to `runs/phase_a_main/<task>/<cell>.log`.

The script is **idempotent** — if a run already has
`best_candidate.json`, it's skipped. Safe to ctrl-C and restart.

### Recommended: run overnight with keep-alive + retry

Mac: prevent sleep while running.
```bash
caffeinate -dimsu -w $$ &   # keeps Mac awake while this shell lives
bash experiments/team/run_P1_gpt41mini_hover_pupa.sh
```

Or wrap in auto-retry loop (survives transient API errors):
```bash
until bash experiments/team/run_P1_gpt41mini_hover_pupa.sh; do
    echo "Crashed. Retrying in 60s..."; sleep 60
done
```

---

## Step 6 — Monitor progress

During a run, check a separate terminal:

```bash
# Live count: how many runs completed vs remaining
find runs/phase_a_main/ -name "best_candidate.json" | wc -l

# Per-run log tail
tail -f runs/phase_a_main/hover/original_immediate_s0.log

# Latest merge events across all runs
tail -q runs/phase_a_main/*/merge_quality.jsonl
```

---

## Step 7 — Sync results back

When your 20 runs are done, the tree looks like:

```
runs/phase_a_main/
├── hover/
│   ├── original_immediate_s0/
│   │   ├── best_candidate.json
│   │   ├── candidates.jsonl
│   │   ├── merge_quality.jsonl
│   │   └── ...
│   └── ... (9 more merge cells + 1 NoMerge)
└── <your-other-bench>/
    └── ...
```

Coordination with team: decide a shared location (S3 / Google Drive /
shared machine / squash commit to a `results/` branch). Simplest:

```bash
# Tar your slice
tar czf phase_a_P1_hover_pupa.tar.gz runs/phase_a_main/

# Each teammate uploads their tar. Team lead unpacks all into one tree.
```

---

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `AuthenticationError: Incorrect API key` | stale key in env | re-export key; `echo $OPENAI_API_KEY` to confirm |
| `RateLimitError: 429` | hit tier-1 RPM (500/min for gpt-4.1-mini) | wait a few min; if persistent, upgrade to tier-2 with $50 prepay |
| Run hangs for 30+ min at "Iteration N" | transient API timeout | ctrl-C, re-launch (idempotent) |
| HoVer "Dataset scripts are no longer supported" | `datasets>=4` installed | `uv pip install --force-reinstall --no-deps 'datasets<4' --python .venv/bin/python` |
| HoVer `cannot import name 'tqdm'` | corrupted datasets install | same as above |
| `Exception: Incorrect API key provided: sk-d0716...` | previous key cached by LiteLLM | `unset OPENAI_API_KEY; export OPENAI_API_KEY=sk-...` again |

---

## Scientific context (TL;DR)

We're ablating **3 merge algorithms × 3 start policies** on **4 benchmarks
× 2 models × 1 seed = 80 runs**. Goal: identify a `(merge_algo, start_policy)`
that beats the paper's default `GEPA+Merge`, especially on Qwen3-8B
(where paper Observation 5 reports merge HURTS). We also verify the
winner transfers across Qwen3 sizes (4B, 14B) in Phase B.2.

Deliverables: poster v1 due **5/7**, paper due **5/12**.

Your data alone doesn't answer the question — we need all 4 slices to
cross-compare. Please **aim to finish by end-of-day Monday 4/27** so
analysis can begin Tuesday.

---

## Who to ping if stuck

- Environment / code bugs: team lead
- API billing / key issues: you (own your own key)
- Paper content / methodology questions: read `PHASE_A_PLAN.md` + paper
  Section 4 and D.1; if still unclear, slack team channel
