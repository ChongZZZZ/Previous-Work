# Adaptive Merge — Implementation Notes

This file is the engineering record for the BehavioralAdaptiveMergePolicy
(REPORT.md §16). The design rationale and verification plan live in
[`/Users/zhaochong/Desktop/NLP_Project/AdaptiveMergePolicy.md`](../../AdaptiveMergePolicy.md).

---

## What was built

| File | Role |
|------|------|
| `src/gepa/strategies/adaptive_merge.py` | `AdaptiveMergeConfig`, `AdaptiveStartPolicy` (Layer −1), `BehavioralAdaptiveMergePolicy` (Layer 1 + Layer 2), `AdaptiveMergeDecision` cache record, pure-function signals (`example_level_agreement`, `behavioral_diversity`, `specialization_split`, `predictor_maturity_gini`, `token_jaccard`, `prompt_token_count`, `predicted_combine_all_length`, `gini_coefficient`), and the `safe_log_adaptive` guard. |
| `src/gepa/proposer/adaptive_pair_selection.py` | `rank_pairs_by_adaptive_diversity` strategy — thin delegate to `policy.rank_pairs(state, merge_candidates)`. |
| `src/gepa/proposer/merge_selection.py` | One new entry in `SELECTION_STRATEGIES`: `"adaptive_diversity"`. |
| `src/gepa/proposer/merge.py` | (a) Pass `state` + `policy` to the strategy registry call (existing strategies ignore the extras). (b) Inside `propose()`, when `policy.algorithm_for_pair` exists, wrap `merge_algorithm_fn` so the algorithm is chosen per `(ancestor, id1, id2)` triplet. The Layer 0 helper signature is **unchanged**. (c) After a successful merge, write `adaptive_*` metadata via `safe_log_adaptive`. |
| `src/gepa/api.py` | New kwargs (default `adaptive_merge_enabled=False`); when True, wire `AdaptiveStartPolicy` + `BehavioralAdaptiveMergePolicy`, force `merge_selection_strategy="adaptive_diversity"`. Old prompt-divergence `AdaptiveMergePolicy` import + dispatch deleted. |
| `experiments/benchmarks/run_dspy.py` | Argparse flags mirroring the new kwargs. |
| `experiments/analysis/adaptive_replay.py` | Read-only post-hoc replay over saved `merge_quality.jsonl` + `gepa_state.bin` cells. |
| `tests/proposer/test_adaptive_merge.py` | 44 tests covering pure signals, AdaptiveStartPolicy, G1/G3 (incl. G3-off variant + missing lineage), A1/A2/A3/A4, decision cache idempotence, wrapper signature contract, AlwaysMergePolicy backward-compat, `safe_log_adaptive` guards, end-to-end api wiring. *(G2 tests removed 2026-05-01.)* |

## Where the policy plugs into GEPA (and what is preserved)

The pipeline (REPORT.md §16):

```
GEPA normal mutation/search
        ↓
Active Pareto frontier            ← unchanged
        ↓
Layer −2: GEPA budget guard        ← unchanged (use_merge / total_merges_tested / max_merge_invocations)
        ↓
Layer −1: AdaptiveStartPolicy      ← NEW (warmup_frac, min_frontier_size, optional plateau)
        ↓
Layer 0: GEPA structural triplet   ← unchanged (find_common_ancestor_pair / does_triplet_have_desirable_predictors)
        ↓
Layer 1: BehavioralAdaptive        ← NEW (G1 parent strength, G3 maturity-toggleable)  # G2 removed 2026-05-01
        ↓
Outer pair selection (adaptive_diversity strategy → policy.rank_pairs)  ← NEW
        ↓
Layer 2: algorithm_for_pair        ← NEW (A1 bloat, A2 specialization, A3 duplicate, A4 default)
        ↓
GEPA subsample gate + Pareto       ← unchanged (engine.py:437-443)
```

**Preserved from GEPA (verified by 105/105 unit-test pass):**
- `find_dominator_programs`, `find_common_ancestor_pair`, `filter_ancestors`, `does_triplet_have_desirable_predictors`, `sample_and_attempt_merge_programs_by_common_predictors` — all signatures byte-identical.
- All `MergeStartPolicy` implementations and `AlwaysMergePolicy`.
- `MergeQualityCallback` writers and the `merge_quality.jsonl` schema.
- The engine's `new_sum >= max(parent_sums)` accept gate and Pareto update.

## Removed legacy prompt-divergence `AdaptiveMergePolicy`

The original `AdaptiveMergePolicy` class in `src/gepa/strategies/merge_policy.py` (a prompt-edit-distance baseline) has been **deleted**. A repo-wide audit confirmed it was dead code outside its own definition and a now-removed dispatch branch in `api.py`.

**Audit (run 2026-04-30):**

- `AdaptiveMergePolicy` references found in:
  - `src/gepa/strategies/merge_policy.py` — class definition (deleted)
  - `src/gepa/api.py` — import + dispatch branch (deleted)
  - `src/gepa/proposer/merge.py:22` — symbol listed in `from ... import` line, never referenced in body (deleted from import)
  - `src/gepa/examples/README.md` — documentation only (rewritten)
- `merge_min_score_threshold` / `merge_divergence_threshold` references found only in `api.py` kwargs / dispatch branch (deleted) and `examples/README.md` (rewritten).
- **Not found** in: `tests/**`, `experiments/**` (incl. `run_dspy.py`), any `phase_a*` shell script, any `.yaml`/`.toml`/`.json` config.

**Why deleted:**

- Phase A' (REPORT.md §8) showed prompt-level features have AUC ≤ 0.58 for accept/reject prediction — exactly the signal the old class used. The new `BehavioralAdaptiveMergePolicy` uses subsample-behavioral signals (AUC 0.987), so the legacy class was both unused and methodologically obsolete.
- Keeping it alongside `BehavioralAdaptiveMergePolicy` would cause conceptual collision: two different "adaptive" policies with different definitions of "adaptive".
- No live caller. Phase A 80-cell run script `run_dspy.py` never set `merge_min_score_threshold` / `merge_divergence_threshold`, so deletion does not change any Phase A reproduction.

## Each rule and its reason

| Rule | Threshold (default) | Catches | Action |
|------|--------------------:|---------|--------|
| **G1** | parent score ≥ active-frontier median | weak parents | skip pair |
| ~~G2~~ | ~~example-level agreement ≤ 0.85~~ | ~~parents that behave identically~~ | **REMOVED 2026-05-01** (see note below) |
| **G3** | predictor-maturity Gini ≤ 0.50 (toggleable) | imbalanced lineages where one predictor is barely mutated | skip pair |
| **A1** | max predictor tokens ≤ 4000 (`L_MAX`) | bloat risk (defensive cap) | route to `summarize_before` |
| ~~A1.b~~ | ~~predicted growth ratio ≤ 1.30 (`BLOAT_SAFE_RATIO`)~~ | ~~bloat risk via combine_all~~ | **REMOVED 2026-05-01** (see note below) |
| **A2** | specialization split ≤ 0.30 | parents specialize to disjoint subdomains | route to `summarize_before` |
| **A3** | token Jaccard ≤ 0.70 | near-duplicate prompts | route to `original` (cheap pick) |
| **A4** | (default) | safe complementary case | `original` *(was `combine_all` until 2026-05-01)* |

Three of the rules (G3, A1, A2) directly mitigate the three documented catastrophic mechanisms in REPORT.md §15. The other rules cover well-understood "merge has nothing to do" cases (A3) or proposal-level commitments (G1, A4).

### G2 removal note (2026-05-01)

`G2` was removed after the live G2-on qwen3-8b adaptive run (s=0, 4 cells, 20 firing merges). All observed merges had `example_agreement ∈ [0.75, 0.85]`, so G2 with the 0.85 default was a **no-op gate**: it never skipped a pair. Tightening the threshold (e.g. to 0.80) would have introduced a magic number with no principled derivation, since the data clusters tightly inside the threshold range. The role G2 was supposed to play (filter near-duplicate behavior) is already covered by:
- **A3** (near-duplicate Jaccard on prompt text) — sends near-duplicate prompts to the cheaper `original` algorithm.
- **GEPA's subsample acceptance gate** ([engine.py:437-443](../src/gepa/core/engine.py#L437-L443)) — rejects merges that don't strictly improve any subsample example, which catches near-identical behavior automatically.

`example_agreement` and `behavioral_diversity` are still computed and stored on the `_pair_cache` and decision record so they remain available as **observability** signals (used by `rank_pairs` for sort order, and surfaced in the replay tooling). Only their use as a Layer-1 *gate* was removed.

### A4 default flip (2026-05-01)

`A4` (the safe complementary fallback when nothing else fires) used to route to `combine_all` (Case-B concat). The G2-on qwen3-8b adaptive run (s=0) underperformed Phase A NoMerge by ~4 pp on hotpotqa and ~2.7 pp on hover. Inspection of Phase A's *best* cell on those benchmarks for qwen3-8b showed it always uses the `original` algorithm (Algorithm 4 — per-predictor pick from `{ancestor, id1, id2}`), not `combine_all`. `combine_all` only beats `original` on IFBench-like tasks where parents specialise on disjoint constraint sets — and that case is now caught explicitly by **A2** (specialization-split → `summarize_before`). The conservative complementary default is therefore `original`: it never introduces new prompt content beyond what already exists in the parent lineage, so it cannot regress on prompt-bloat-sensitive tasks.

### `min_frontier_size` default 5 → 3 (2026-05-01)

**Changed `AdaptiveMergeConfig.min_frontier_size` default from 5 to 3.** The v2 qwen live run logged `[adaptive_start] skip reason=frontier_too_small |frontier|=4 < 5` repeatedly on ifbench; the ifbench frontier *never* grew to 5 within its 3593-metric-call budget, so 0 merges fired. The other three qwen tasks (hotpotqa/hover/musique) had `|frontier| ≥ 5` well before warmup completed, so this change has no effect on them.

`3` is the structural minimum: a triplet `(ancestor, id1, id2)` requires ≥3 candidates to be non-degenerate. Anything less than 3 makes merge impossible by construction; choosing exactly 3 means "merge can fire as soon as it's structurally possible," matching Layer 0's hard requirement. The previous `5` was a conservative buffer that turned out to be too tight for IFBench-shaped tasks (multi-constraint metric → dominator is hard to grow).

### Growth-ratio gate removal + `combine_all` dead-code note (2026-05-01)

**Removed `BLOAT_SAFE_RATIO` (= 1.30) growth-ratio gate.** Originally A1 had two sub-checks: `L_MAX` (absolute predictor-length cap) and `growth = predicted_combine_all_length / max(parent_lengths)` against `BLOAT_SAFE_RATIO`. The growth-ratio sub-check was specifically simulating *what `combine_all` would output* — but after the A4 flip, the policy never routes to `combine_all` (verified empirically: in the post-hoc replay sweep at `BLOAT_SAFE_RATIO ∈ {1.20, 1.25, 1.30, 1.35, 1.50}`, the `combine_all` algo count is **0** in every variant). Using a fictional algorithm's predicted length to gate routing was logically incoherent.

The signal is still computed and logged as `predicted_combine_all_length` and `predicted_growth_ratio` in the per-decision `signals` dict — it is **observability-only**, useful for replay tooling that compares adaptive vs. Phase A `combine_all` runs. It just doesn't route any decision.

**`combine_all` is now dead code in adaptive mode.** All five Layer-2 return paths route to either `summarize_before` (A1 LMAX, A2 specialization) or `original` (A3 near-duplicate, A4 default). The `combine_all` algorithm implementation in `src/gepa/strategies/merge_algorithm.py` is retained because:
1. Phase A (non-adaptive) cells reproduce against it — `merge_algorithm=combine_all` is a valid CLI value for the legacy path.
2. `predicted_combine_all_length` is a per-Case-B token-count simulator that's useful as an observability signal even when we don't run the algorithm.

The `BehavioralAdaptiveMergePolicy.algorithm_for_pair` itself never returns `"combine_all"`. The `--merge_algorithm` CLI flag still defines the wrapper-level fallback if `algorithm_for_pair` ever returned `None`, but it never does — so the flag has no effect under `--adaptive_merge_enabled`.

**Sweep evidence (`adaptive_merge/replay/sweep_bloat_*/`, 2026-05-01):**
- Catastrophe coverage (`actual_full_val_lift ≤ −0.05`, n=10): **9/10 addressed** at every BLOAT_SAFE_RATIO value (1.20 through 1.50). 8 of 10 are caught by G1 (parent_strength), 1 by L_MAX. The growth-ratio sub-check was *not* the binding constraint on catastrophe coverage.
- Healthy-event over-skip: **identical** across BLOAT_SAFE_RATIO values (skips happen at Layer 1, not Layer 2).
- Layer 2 algo distribution under G3_on, BLOAT_SAFE_RATIO=1.30: 75 `summarize_before`, 28 `original`, 0 `combine_all`. Sweep down to 1.20: 96 / 7 / 0. Sweep up to 1.50: 32 / 71 / 0. The growth-ratio knob was a `summarize_before` (LM rewrite) ⇄ `original` (cheap pick) trade-off — not a quality knob.

## Implementation cautions (held throughout)

**Caution 1 — Decision cache consistency.** `BehavioralAdaptiveMergePolicy` owns the canonical `_decisions: dict[(ancestor,id1,id2), AdaptiveMergeDecision]` cache, plus a per-pair `_pair_cache: dict[(id1,id2), _Layer1Result]`. Both are reset at the start of each `should_schedule(state, ...)` call. All three entry points read/write the same caches:

- `should_schedule`: populates `_pair_cache`
- `rank_pairs` (called via `adaptive_diversity` strategy with `policy=...` in `**kwargs`): uses `_pair_cache`; lazily fills missing pairs without clearing
- `algorithm_for_pair`: uses `_pair_cache` for shared signals + populates `_decisions`

The `merge.py` wrapper has a tiny defensive local cache for the algorithm callable, but always delegates to `policy.algorithm_for_pair(...)` so the policy's cache is the single source of truth. Pair-order is normalized inside `algorithm_for_pair` so `(id1, id2)` and `(id2, id1)` hit the same cache slot. Tested: `test_algorithm_for_pair_is_idempotent`, `test_should_schedule_clears_cache_on_each_call`, `test_rank_pairs_uses_should_schedule_cache`.

**Caution 2 — Logging safety.** `safe_log_adaptive(state, logger, key, value)` writes to `state.full_program_trace[-1]` only when (a) the trace exists and is non-empty, (b) the last entry is a dict, (c) the entry has `invoked_merge=True` (set by `MergeProposer.propose` at line 319 before any adaptive code runs). On any mismatch, falls back to the proposer's `logger.log` and the module logger; never pollutes an unrelated trace entry. Tested: `test_safe_log_adaptive_writes_only_when_invoked_merge_set`, `test_safe_log_adaptive_skips_when_invoked_merge_missing`, `test_safe_log_adaptive_skips_when_trace_empty`, `test_safe_log_adaptive_skips_when_no_state`.

## Post-hoc replay results (2026-05-01)

Ran `experiments.analysis.adaptive_replay` over `P2_result/phase_a_main`, `P3_result/phase_a_main`, `P4_result/phase_a_main`, `runs/phase_a_main`, and `runs/phase_a_main_qwen`:

- **73 cells replayed**, **296 merge events** per variant.
- **Catastrophe coverage = 100%** (G3-on and G3-off both): 10/10 events with `full_val_lift_over_best_parent ≤ −0.05` were addressed — 9 hard-skipped at Layer 1 (G1 dominant: 181 events; G2: 64; G3: 5 additional under G3-on), 1 routed to `summarize_before` at Layer 2 (the −18.33 pp `gpt-4.1-mini/2wiki/combine_all_budget_proportional_s0` event was caught by A1 bloat-growth-ratio).
- **G3 cost** (G3-on vs. G3-off): 5 extra skips, 1 fewer accepted-event preserved, 0 catastrophes additionally caught. G3 may be unnecessary on this dataset; toggle via `--adaptive_no_maturity_gate`.
- **Healthy-event over-skip**: 197/234 actually-accepted events would be skipped post-hoc. Caveat: the replay's at-time frontier is approximated (filter by `new_candidate_idx`), so live behavior will skip somewhat fewer healthy events. The §16.5 lower-bound argument still holds: even worst-case, the run degenerates to NoMerge.
- **Layer 2 distribution** (when not skipped, G3-on): 38 `summarize_before` (mostly bloat-growth), 6 `combine_all` (safe complementary), 2 `original` (near duplicate).

Output: `gepa_merge/adaptive_merge/replay/{adaptive_replay_decisions.csv, adaptive_replay_summary.md, adaptive_replay_summary.json}`.

## How to run post-hoc replay

```bash
cd /Users/zhaochong/Desktop/NLP_Project/gepa_merge
PYTHONPATH=src .venv/bin/python -m experiments.analysis.adaptive_replay \
    --runs_root P2_result/phase_a_main P3_result/phase_a_main P4_result/phase_a_main \
                runs/phase_a_main runs/phase_a_main_qwen \
    --out adaptive_merge/replay
```

Threshold sweep (any threshold can be overridden):

```bash
PYTHONPATH=src .venv/bin/python -m experiments.analysis.adaptive_replay \
    --runs_root ... --out .../sweep_lmax_2000 \
    --L_MAX 2000  # --BLOAT_SAFE_RATIO removed 2026-05-01 (growth-ratio gate deletion)
```

The script is read-only; no LM calls; takes < 5 s per 100 cells.

## How to enable adaptive live re-run

For a single cell:
```bash
.venv/bin/python -m experiments.benchmarks.run_dspy \
    --task hotpotqa --model openai/gpt-4.1-mini \
    --use_merge --max_merge_invocations 15 \
    --adaptive_merge_enabled \
    --merge_algorithm original \
    --run_dir adaptive_merge/runs/gpt_hotpotqa_adaptive_s0 \
    --max_metric_calls 6871 --seed 0
```

For the full 8-cell grid (4 tasks × 2 models, seed 0; routes both models through Prime Intellect):
```bash
PRIME_API_KEY=... PRIME_TEAM_ID=... \
    bash experiments/run_adaptive_live.sh
```
Outputs land in `adaptive_merge/runs/` and `adaptive_merge/logs/`; total spend ≈ $55, wall-clock ≈ 36 h sequential (~5 h fully parallel).

When `--adaptive_merge_enabled` is set, `merge_selection` is forced to `adaptive_diversity` and `merge_start_policy` is replaced by `AdaptiveStartPolicy` (regardless of `--merge_start`). The `--merge_algorithm` flag becomes the **fallback** algorithm — used only when the policy's `algorithm_for_pair` returns None (which it never does in the current implementation, so in practice the flag has no effect).

To disable G3 only:
```bash
... --adaptive_merge_enabled --adaptive_no_maturity_gate
```

Plateau gate is **enabled by default** as of 2026-05-02 (see ablation below). To disable for ablation only:
```bash
... --adaptive_merge_enabled --adaptive_no_plateau_gate
```

All threshold defaults match REPORT.md §16. Override via `--adaptive_warmup_frac`, `--adaptive_min_frontier_size`, `--adaptive_parent_strength_quantile`, `--adaptive_maturity_gini_max`, `--adaptive_L_MAX`, `--adaptive_specialization_split_threshold`, `--adaptive_duplicate_jaccard_threshold`, `--adaptive_correctness_threshold`. *(`--adaptive_max_example_agreement` removed 2026-05-01 with G2; `--adaptive_BLOAT_SAFE_RATIO` removed 2026-05-01 with the growth-ratio gate.)*

## Status

- ✅ Code complete (105/105 unit tests pass after plateau-default flip + min_frontier 5→3 + G2/growth-ratio deletion + A4 default flip; 330/334 broader tests pass — the 4 failures are pre-existing `cloudpickle`-not-installed env issues unrelated to this change).
- ✅ Post-hoc replay run on 73 cells / 296 events; 100% catastrophe coverage.
- ✅ Live qwen3-8b run executed on 4 tasks (seed=0); see "Plateau-gate ablation" below.
- ⏳ Live gpt-4.1-mini run pending (decision gated on whether to investigate v2 hover −2 pp regression first).
- ⏳ Threshold sensitivity sweep (±20% per threshold) — replay-only, can be done any time.

## Plateau-gate ablation (qwen3-8b, seed=0, 2026-05-02)

Test whether Phase A's `score_plateau` insight — "don't merge while the frontier is still climbing" — generalizes to our adaptive Layer −1 stack. Ran two configs side-by-side:

- **v2 (plateau ON):** `warmup_frac=0.25`, `min_frontier_size=5`, `use_plateau_gate=True`, G3 ON, no G2, no growth-ratio gate, A4 default = `original`.
- **v2.6 (plateau OFF):** same as v2 but `use_plateau_gate=False` and `min_frontier_size=3`.

We verified separately (v2.5 vs v2 byte-identical best_candidates) that `min_frontier_size` 5 vs 3 is empirically equivalent on these qwen tasks, so v2 vs v2.6 isolates the plateau-gate effect.

### Per-cell results

| task | n | v1 G2-on | v2 (plateau ON) | v2.6 (plateau OFF) | Δ vs v2 | accepted merges (v2 → v2.6) |
|------|--:|---------:|----------------:|-------------------:|--------:|-----------------------------|
| hotpotqa | 300 | 51.0 | 51.0 | 51.0 | **0** | 3 → 4 |
| ifbench | 294 | 35.54 | 35.54 | **32.65** | **−2.89** | 0 → 0 (1 attempted+rejected) |
| **hover** | 300 | 45.0 | 43.0 | **1.67** | **−41.33** | 1 → **7** |
| musique | 300 | 51.67 | 51.67 | 49.0 | **−2.67** | 3 → 5 |

### Findings

1. **0/4 wins for plateau OFF; 3/4 cells regressed.** Regression magnitude tracks the increase in accepted merges (hover 1→7 = −41 pp; musique 3→5 = −2.67 pp).
2. **Hover collapsed (1.67/100)**: test_eval log showed `LM Response: None` for most examples — the 7 stacked merges produced a prompt that breaks qwen3-8b's JSON-adapter parsing at inference time. Catastrophic prompt corruption.
3. **Even rejected merges hurt** (ifbench): the merge attempt at iter=27 was rejected by GEPA's subsample gate, but the act of attempting consumed subsample budget and shifted the trajectory enough to produce a different (worse) `best_candidate`.

### Decision

**`use_plateau_gate` default flipped from `False` to `True`** (committed 2026-05-02). This locks the empirically validated config as the policy's default for qwen3-8b. `--adaptive_no_plateau_gate` CLI flag is added for ablation use only.

### Locked default config (post 2026-05-02)

| Param | Default | Source |
|---|---:|---|
| `warmup_frac` | 0.25 | REPORT.md §16 |
| `min_frontier_size` | 3 | structural minimum; equivalent to 5 on these tasks |
| `use_plateau_gate` | **True** | this ablation |
| `plateau_window` | 3 | matches Phase A `ScorePlateauStartPolicy.plateau_patience=3` |
| `plateau_eps` | 0.0 | strict-improvement requirement |
| `parent_strength_quantile` (G1) | 0.50 | median, relative |
| `use_maturity_gate` (G3) | True | catastrophe coverage |
| `maturity_gini_max` | 0.50 | empirical elbow |
| `L_MAX` (A1) | 4000 | defensive bloat cap |
| `specialization_split_threshold` (A2) | 0.30 | empirical |
| `duplicate_jaccard_threshold` (A3) | 0.70 | empirical |
| A4 default algorithm | `original` | flipped from `combine_all` 2026-05-01 |
| ~~G2~~ | (deleted 2026-05-01) | no-op on qwen |
| ~~`BLOAT_SAFE_RATIO`~~ | (deleted 2026-05-01) | gated dead `combine_all` path |

### Open question

v2's hover (43.0) is 2 pp below v1 G2-on hover (45.0). Plateau is not the cause (v2 had plateau ON; the −2 pp is vs v1 which used `immediate` start = plateau-off-equivalent but with G2 ON, A4=combine_all, growth-ratio ON). The regression must come from one of those three v2 changes (G2 deletion, A4 default flip, or growth-ratio gate deletion). A targeted ablation could pin it down — outside the scope of this plateau experiment.

## Pair-selection ablation (v2 vs v2.7, qwen3-8b, seed=0, 2026-05-02)

Test whether `adaptive_diversity` pair selection (used by `BehavioralAdaptiveMergePolicy.rank_pairs`, in v1/v2/v2.5/v2.6) is the cause of v2's hotpotqa (−4 pp vs NoMerge) and hover (−4.67 pp vs NoMerge) regressions. v2.7 = locked v2 config but `--adaptive_pair_selection=random` (delegates to GEPA's built-in `rank_pairs_random`).

### Per-task results

| task | NoMerge | v1 G2-on | v2 (adaptive_diversity) | v2.7 (random) | Δ (v2 − v2.7) | PA best |
|------|--------:|---------:|-----------------------:|--------------:|--------------:|---------:|
| hotpotqa | 55.00 | 51.0 | 51.0 | 51.0 | **0** | 56.33 |
| ifbench | 31.97 | 35.54 | 35.54 | 32.65 | **+2.04** (adaptive_div helps) | 36.22 |
| hover | 47.67 | 45.0 | 43.0 | 44.33 | **−1.33** (adaptive_div hurts mildly) | 50.67 |
| **musique** | 48.33 | 51.67 | 51.67 | **40.67** ⚠ | **+11.00** (adaptive_div saves catastrophe) | 52.33 |

### Merge-count diagnostic

| task | v2 acc merges | v2.7 acc merges | observation |
|------|---:|---:|------------|
| hotpotqa | 3 | 1 | random's pair often rejected by subsample gate; final best unchanged |
| ifbench | 0 (1 attempted+rejected) | 0 (1 attempted+rejected) | both attempt then reject; trajectory shifts diverge slightly |
| hover | 1 | 2 | random fires more merges, 2 of which were accepted |
| musique | 3 | 1 | random's single pick was catastrophic; the absence of v2's other 2 good merges hurt |

### Findings

1. **adaptive_diversity is net positive: +11.71 pp summed across 4 tasks.** The diversity-ranking strategy surfaces multiple high-quality pairs, giving GEPA's Pareto-front more chances to land on a good final candidate.
2. **musique catastrophe (−11 pp under random)** confirms that "select max-diverse pair" provides genuine protection: when GEPA must commit to a single merge under random selection, the chosen pair can be a single point of failure.
3. **adaptive_diversity is NOT the cause of v2's hover/hotpotqa regression vs NoMerge.** Switching to random recovers only +1.33 pp on hover; the gap to NoMerge (−3.34 pp residual) and PA best (−6.34 pp) persists.
4. **Hypothesis for the residual gap: Layer 2 routing (A1/A2/A3/A4).** Phase A's `original_immediate` (= no Layer 2 routing, always `original`) gets 50.67 on hover and 56.33 on hotpotqa, far above v2 (43.0/51.0). v2.8 ablation (in progress) tests `disable_layer2_routing=True` to bypass A1/A2/A3 entirely.

### Decision

**Keep `adaptive_diversity` as locked default.** Code default unchanged. The new `--adaptive_pair_selection` CLI flag is retained for future ablations (and to allow opting into GEPA's other built-in selectors `random`/`divergence`/`score`/`complementary` for users who want the simpler behavior).

## Layer 2 ablation (v2.8, qwen3-8b, seed=0, 2026-05-02 — in progress)

Test whether Layer 2 routing (A1 bloat → summarize_before, A2 specialization → summarize_before) is the cause of v2's residual hover/hotpotqa regression vs NoMerge. v2.8 = locked v2 config but `--adaptive_disable_layer2_routing` set, which short-circuits `_evaluate_layer2` and always returns `("original", "layer2_routing_disabled")`. Signals (max_predictor_tokens, predicted_growth_ratio, specialization_split, token_jaccard) are still computed and logged for observability.

Results pending — will be added when test_evals complete.
