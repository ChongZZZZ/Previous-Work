# When Does GEPA Merge Help? A Mechanism-Level Diagnostic

An MIT NLP course project (team of 4) studying the **system-aware merge operator** of
[GEPA](https://github.com/gepa-ai/gepa) — the genetic-Pareto prompt optimizer — and answering a
question the GEPA paper leaves open: its *Observation 5* reports that merge helps GPT-4.1-mini
(+1.14 pp) but **hurts Qwen3-8B (−2.45 pp)**, with no mechanism offered. Is that regression
algorithmic, or a hyperparameter artifact?

We ran a 98-cell configuration sweep (3 merge algorithms × 3 start policies + NoMerge baselines,
2 models, 5 benchmarks, held-out 300-example test eval), built a mechanism-level diagnostic of
*why* merges are accepted and when they pay off, and used those findings to design an adaptive,
behaviorally-gated merge policy — then validated it across models.

**Headline results:**

- **Observation 5 is reversed by a hyperparameter.** With a different merge *start policy*
  (`score_plateau` or `budget_proportional` instead of the paper's `immediate`), Qwen3-8B *gains*
  on 4/4 benchmarks (+1.33 to +4.25 pp). No new algorithm needed.
- **Merge can be catastrophic, for three distinct reasons.** The sweep surfaces cells at
  −22 to −36 pp with three separate mechanisms (prompt-bloat × small-model JSON failure,
  and two flavors of predictor-maturity imbalance).
- **GEPA's accept/reject decisions are behavioral, not textual.** 17 prompt-level features
  can't predict acceptance (AUC ≤ 0.58); the behavioral subsample profile reaches AUC 0.987.
- **The adaptive policy wins 5/5 benchmarks on gpt-4.1-mini** (avg +1.94 pp vs NoMerge,
  beating the best fixed config by +4.66 pp on HotpotQA) and correctly fires *zero* merges on the
  benchmark whose catastrophe class it was built to avoid. On Qwen3-8B it plateaus at 2/4 — and
  the diagnostic explains why: reflection-driven improvement is 6.85× more cost-efficient than
  merge, and val/test correlation (HoVer Pearson r ≈ −0.06) upper-bounds what *any* val-greedy
  policy can achieve there.
- **A counterfactual that falsified our own hypothesis.** Capping the reflection LM at 2,000
  output tokens (to "control prompt inflation") drops aggregate test score by −3.46 pp:
  reflective inflation is load-bearing, not pathological.

Full write-ups: [Report/REPORT.md](Report/REPORT.md) (the complete research log — sweep,
forensics, diagnostic stages 1–5, counterfactual, cross-model validation) and
[Report/AdaptiveMergePolicy.md](Report/AdaptiveMergePolicy.md) (design doc for the four-layer
adaptive policy). Pre-registered hypotheses are in [docs/hypotheses.md](docs/hypotheses.md).

## What was built

Everything runs through a fork of the GEPA library plus a single CLI entry point:

| Where | What |
|------|------|
| `src/gepa/strategies/merge_start_policy.py` | Merge start policies: `immediate` / `score_plateau` / `budget_proportional` |
| `src/gepa/strategies/merge_algorithm.py` | Merge operators: `original` / `combine_all` / `summarize_before` |
| `src/gepa/strategies/adaptive_merge.py` | The four-layer behaviorally-gated adaptive policy (all thresholds as constants) |
| `src/gepa/proposer/merge.py` | GEPA's structural merge proposer (paper Algorithm 4), instrumented |
| `src/gepa/proposer/adaptive_pair_selection.py` | Merge-pair ranking by behavioral diversity |
| `experiments/benchmarks/run_dspy.py` | Single CLI entry point for every run (task × model × merge config × seed) |
| `experiments/run_phase_a.sh` | Configuration-sweep launcher |
| `experiments/run_adaptive_probe.sh` | Adaptive-policy probe launcher |
| `experiments/run_test_eval.sh` | Held-out test evaluation over a tree of finished runs |
| `experiments/analysis/` | Forensics: merge quality, accept/reject classifiers, timing, judge ensembles |
| `analysis/evolution/` | Diagnostic stages 1–5: trajectories, reflect-vs-merge Δval, ancestry, gate audit |
| `results/analysis_output/` | The computed numbers behind the paper's tables and figures |

Benchmarks: IFBench, HotpotQA, HoVer, MuSiQue, 2WikiMultiHopQA via DSPy programs from the
upstream [gepa-artifact](https://github.com/gepa-ai/gepa-artifact) (vendored at setup time).
Models: `openai/gpt-4.1-mini` and `qwen/qwen3-8b`.

## Running it

```bash
bash experiments/setup.sh                # uv venv + deps + vendored DSPy benchmark programs
PYTHONPATH=src .venv/bin/python experiments/warmup_wiki_corpus.py   # Wiki BM25 corpus (~608 MB)

# one sweep cell (~10 min, ~$1)
OPENAI_API_KEY=<key> MODEL=openai/gpt-4.1-mini \
    TASK_LIST=hotpotqa MERGE_ALGO_ONLY=original START_ONLY=immediate \
    SEED_ONLY=0 INCLUDE_NOMERGE=no \
    bash experiments/run_phase_a.sh
```

All API keys come from environment variables; nothing is stored in the repo. Every experiment
reduces to one `experiments.benchmarks.run_dspy` invocation — flags are documented inline.

## This folder vs. the full artifact repo

This folder is the **core code + reports**. The complete submission bundle — including every run
directory referenced in the paper (~114 MB of `best_candidate.json` / `gepa_state.bin` /
`merge_quality.jsonl` / `test_eval.json` artifacts) — lives in its own repo:
**[ChongZZZZ/GEPA_MERGE](https://github.com/ChongZZZZ/GEPA_MERGE)**. Omitted here to keep this
portfolio repo light: `results/` run artifacts (only the small `analysis_output/` summaries are
kept), the vendored `experiments/vendor/` tree (re-cloned by `setup_benchmarks.sh`), and per-cell
figure dumps.

## License

MIT — see [LICENSE](LICENSE). The vendored benchmark programs are from
[gepa-ai/gepa-artifact](https://github.com/gepa-ai/gepa-artifact) under their own license.
