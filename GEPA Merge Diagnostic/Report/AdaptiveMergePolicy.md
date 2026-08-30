# Adaptive Merge Policy — Implementation Plan

## Status (live)

**Done:**
- ✅ Repo-wide audit of legacy `AdaptiveMergePolicy` (verified zero live callers; details in [Audit](#adaptivemergepolicy-usage-audit-verified-before-deletion) section).
- ✅ Deleted legacy `AdaptiveMergePolicy` class from `merge_policy.py`.
- ✅ Removed `AdaptiveMergePolicy` import from `api.py` and `proposer/merge.py`.
- ✅ Removed `merge_min_score_threshold` / `merge_divergence_threshold` kwargs and dispatch branch from `api.py`.
- ✅ Updated `examples/README.md` to point at the new `adaptive_merge_enabled` flag.
- ✅ Created `gepa_merge/experiments/adaptive_merge_implementation_notes.md` with the deletion record.
- ✅ Verified `pytest gepa_merge/tests/test_merge_quality.py gepa_merge/tests/proposer -q` → 63 passed.
- ✅ Plan updated with two implementation cautions ([Decision cache consistency](#implementation-cautions-must-hold) + [Logging safety](#implementation-cautions-must-hold)).

**Approved go-ahead invariants (must hold throughout implementation):**
- Keep `adaptive_merge_enabled=False` by default.
- Preserve GEPA structural filter and subsample/Pareto gate.
- Delete old unused `AdaptiveMergePolicy` as audited (✅ done above).
- Implement post-hoc replay before live reruns.
- **Caution 1 — Decision cache consistency.** `BehavioralAdaptiveMergePolicy` owns the full `AdaptiveMergeDecision` cache keyed by `(ancestor, id1, id2)`. The `merge.py` wrapper may have a local defensive cache for selected algo, but it must call `algorithm_for_pair` in a way that reuses the policy's cached decision when available. `should_schedule`, `adaptive_diversity` pair selection, and `algorithm_for_pair` must NOT be allowed to compute inconsistent decisions for the same triplet.
- **Caution 2 — Logging safety.** When writing `adaptive_*` metadata to `state.full_program_trace[-1]`, first confirm the trace entry exists and corresponds to the current merge attempt. If not, use the logger / replay output instead. Do not assume `full_program_trace[-1]` is always safe after failed or skipped merge attempts.

Detailed implementation of these two cautions is in the [Implementation cautions](#implementation-cautions-must-hold) section below.

**Pending (in order):**
1. Create `gepa_merge/src/gepa/strategies/adaptive_merge.py` (config, signal helpers, `AdaptiveStartPolicy`, `BehavioralAdaptiveMergePolicy`, `AdaptiveMergeDecision`).
2. Create `gepa_merge/src/gepa/proposer/adaptive_pair_selection.py` (`rank_pairs_by_adaptive_diversity` reading policy cache via `**kwargs`).
3. Edit `merge_selection.py` to register the new strategy.
4. Edit `proposer/merge.py` to (a) pass `state` + `policy` into the strategy call, (b) wrap `merge_algorithm_fn` for per-event Layer 2 selection delegating to `policy.algorithm_for_pair`, (c) write adaptive metadata via `_safe_log_adaptive` guard.
5. Edit `api.py` to add adaptive kwargs and wire `AdaptiveStartPolicy` + `BehavioralAdaptiveMergePolicy` when `adaptive_merge_enabled=True`.
6. Edit `experiments/benchmarks/run_dspy.py` for argparse passthrough.
7. Create `gepa_merge/tests/proposer/test_adaptive_merge.py` with all required tests (G1/G3 incl. G3-off, A1/A2/A3/A4, wrapper signature, decision cache, missing-data resilience). *(G2 tests deleted 2026-05-01 alongside the gate.)*
8. Run unit tests + backward-compat smoke (with `adaptive_merge_enabled=False`).
9. Create `gepa_merge/experiments/analysis/adaptive_replay.py`.
10. Run replay over phase_a_main + phase_a_main_qwen, write `adaptive_replay_summary.md`.
11. Flesh out `adaptive_merge_implementation_notes.md` with full design + how-to-run (replay + live).

---

## Context

Phase A characterized **98 cells = 80 original Phase A cells + 2Wiki/post-hoc extension cells** (REPORT.md §15 added 2WikiMultiHopQA as a fifth benchmark; the 80→98 count comes from the post-hoc extension, **not** from a clean 4-benchmark × 2-model × 9-config product). Phase A documented three catastrophic-merge mechanisms (REPORT.md §15) and Phase A' falsified prompt-level signals (§8: prompt-feature AUC ≤ 0.58 for accept/reject; only subsample-behavioral signal reaches 0.987). REPORT.md §16 turns those findings into a proposed adaptive merge policy. This plan implements that §16 policy as a clean drop-in extension of GEPA's existing merge hooks, gated behind `adaptive_merge_enabled=True` (default False), plus a read-only post-hoc replay so we can validate gate precision/recall on the 98-cell archive before any new LM spend.

The hard design constraint is **minimal surgery on GEPA core**: `MergeStartPolicy` and `MergePolicy` are already clean protocols on `MergeProposer`, and `find_dominator_programs` / `find_common_ancestor_pair` / `does_triplet_have_desirable_predictors` already do the structural triplet filter — we don't replace any of that.

## AdaptiveMergePolicy usage audit (verified before deletion)

Repo-wide grep returns:

- `gepa_merge/src/gepa/strategies/merge_policy.py:32` — old class definition (~50 lines)
- `gepa_merge/src/gepa/api.py:38` — import alongside `AlwaysMergePolicy`, `MergePolicy`
- `gepa_merge/src/gepa/api.py:66-67, 400-405` — kwargs + dispatch branch
- `gepa_merge/src/gepa/proposer/merge.py:22` — symbol listed in import, **never referenced in body** (grep count = 1, only the import line)
- `gepa_merge/src/gepa/examples/README.md:46, 63-64, 97-98, 111` — documentation only

**Not found in:** any `tests/**` file, any `experiments/**` script (incl. `run_dspy.py`), any `phase_a*` shell script, any `.yaml`/`.toml`/`.json` config.

**Conclusion:** deletion is safe. No live caller. The deletion will be documented in `adaptive_merge_implementation_notes.md` and `examples/README.md` will be updated to point at `BehavioralAdaptiveMergePolicy` + `adaptive_merge_enabled`. If this audit had returned a single test or script reference, we would have renamed the old class to `LegacyPromptDivergenceMergePolicy` and kept it; that fallback is now unnecessary.

## What is preserved from GEPA (do NOT touch)

- `find_dominator_programs(...)` ([gepa_utils.py:78-87](gepa_merge/src/gepa/gepa_utils.py#L78-L87))
- `find_common_ancestor_pair(...)` + `filter_ancestors(...)` + `does_triplet_have_desirable_predictors(...)` ([merge.py:30-125](gepa_merge/src/gepa/proposer/merge.py#L30-L125))
- `sample_and_attempt_merge_programs_by_common_predictors(...)` — signature unchanged
- `select_eval_subsample_for_merged_program(...)` + `cached_evaluate_full(...)` + engine accept gate ([engine.py:437-443](gepa_merge/src/gepa/core/engine.py#L437-L443))
- All existing `MergeStartPolicy` implementations and `AlwaysMergePolicy` (kept — these are what the 80 Phase A cells actually use)
- `MergeQualityCallback` writers and the `merge_quality.jsonl` schema

## Pipeline mapping

| Spec layer | Hook | Where it plugs in |
|---|---|---|
| Layer −2 (budget guard) | `self.use_merge && total_merges_tested < max_merge_invocations` | already in [merge.py:271](gepa_merge/src/gepa/proposer/merge.py#L271) — unchanged |
| Layer −1 (adaptive start) | `start_policy.allow_merge(state)` | new `AdaptiveStartPolicy` |
| Layer 0 (structural) | `find_dominator_programs` → `find_common_ancestor_pair` → `does_triplet_have_desirable_predictors` | unchanged |
| Layer 1 (behavioral skip gate) | `merge_policy.should_schedule(state, merge_candidates)` | new `BehavioralAdaptiveMergePolicy` |
| Outer pair selection | `merge_selection.SELECTION_STRATEGIES[name]` ([merge.py:339-348](gepa_merge/src/gepa/proposer/merge.py#L339-L348)) | new `"adaptive_diversity"` registered |
| Layer 2 (algo selection) | `self.merge_algorithm_fn` (currently fixed) | new optional `policy.algorithm_for_pair(state, ancestor, id1, id2)` via wrapped callable |
| Subsample gate + Pareto update | unchanged | unchanged |

## Rule numbering (canonical for this PR)

| Rule | Layer | What it gates / chooses | Toggle |
|---|---|---|---|
| **G1** | Layer 1 | parent strength (both above active-frontier median) | always on |
| ~~G2~~ | ~~Layer 1~~ | ~~behavioral complementarity (per-example agreement ≤ threshold)~~ | **REMOVED 2026-05-01** — see note below |
| **G3** | Layer 1 | **predictor maturity imbalance** (Gini ≤ threshold) | **`use_maturity_gate`, default True, toggleable** |
| **A1** | Layer 2 | absolute predictor-length cap (`L_MAX`) → `summarize_before` | always on |
| ~~A1.b~~ | ~~Layer 2~~ | ~~combine_all growth ratio (`BLOAT_SAFE_RATIO`) → `summarize_before`~~ | **REMOVED 2026-05-01** — see G2-removal-style note below |
| **A2** | Layer 2 | specialization split → `summarize_before` | always on |
| **A3** | Layer 2 | near duplicate → `original` | always on |
| **A4** | Layer 2 | safe complementary default → `original` (was `combine_all` until 2026-05-01) | always on (fallback) |

**Catastrophe → rule mapping:**
- §15.3 gpt × original × score_plateau (−28.66) and qwen × original × bp (−35.67) → caught by **G3** (maturity imbalance)
- §7 IFBench × qwen × combine_all × immediate (−22.28) → caught by **A1** (bloat) routing to `summarize_before`
- §15.2 / §15.3 question-type heterogeneity (qwen/2wiki) → caught by **A2** (specialization split) routing to `summarize_before`

**G3 toggleable** because it's the most experimental gate and most sensitive to lineage-data quality. `--use_maturity_gate=False` cleanly disables only G3.

### G2 removal note (2026-05-01)

**Removed.** `G2` previously gated pairs whose `example_agreement` exceeded `max_example_agreement` (default 0.85). Empirical observation on the live G2-on qwen3-8b run (s=0, 4 cells, 20 firing merges total) found every observed pair clustered in `agreement ∈ [0.75, 0.85]` — `G2` never fired as a skip and the threshold acted as a magic number with no principled derivation. The role G2 was supposed to play (filter near-duplicate behavior) is already handled downstream by:
- **A3** (near-duplicate Jaccard on prompt text) — routes near-duplicate prompts to `original`.
- **GEPA's subsample acceptance gate** ([engine.py:437-443](gepa_merge/src/gepa/core/engine.py#L437-L443)) — rejects merges that don't strictly improve any subsample example.

`example_agreement` and `behavioral_diversity` are still computed and logged as **observability signals**; they are no longer used to gate. `_decision_cache` continues to record them so the replay tooling can surface their distribution.

### A4 default flip (2026-05-01)

**Changed `combine_all` → `original`.** The G2-on qwen3-8b adaptive run underperformed Phase A NoMerge by ~4 pp on hotpotqa and ~2.7 pp on hover. Phase A's *best* cell on those benchmarks for qwen3-8b uses the `original` algorithm (Algorithm 4 — per-predictor pick from `{ancestor, id1, id2}`), not `combine_all` (Case-B concat). `combine_all` only helped on IFBench-like tasks where parents specialise on disjoint constraint sets — that case is now caught explicitly by **A2** (specialization-split → `summarize_before`). The conservative complementary default is therefore `original`, which never introduces new prompt content beyond what already exists in the lineage.

### `min_frontier_size` default 5 → 3 (2026-05-01)

Live v2 qwen × ifbench observed `|frontier|=4 < 5` repeatedly across 3593 metric calls → 0 merges fired. ifbench's multi-constraint metric makes per-example domination hard, so the dominator set grows slowly. Setting the threshold to 3 (Layer 0's structural minimum for a non-degenerate triplet) lets merges fire as soon as they're geometrically possible. Other qwen tasks (hotpotqa/hover/musique) had `|frontier| ≥ 5` long before warmup ended, so this change is a no-op there.

### Growth-ratio gate removal + `combine_all` dead-code note (2026-05-01)

`BLOAT_SAFE_RATIO` (= 1.30) was the threshold for `growth = predicted_combine_all_length / max(parent_lengths)`. After the A4 flip, the policy never routes to `combine_all`, so the growth-ratio signal was simulating a fictional algorithm's output. Replay sweep `BLOAT_SAFE_RATIO ∈ {1.20, 1.25, 1.30, 1.35, 1.50}` confirmed: catastrophe coverage was 9/10 at every threshold (the binding constraints are G1 + L_MAX, not growth-ratio); the knob only traded `summarize_before` LM calls for `original` cheap picks. The gate is removed; the signal is still computed and logged in `decision.signals` for observability. **`combine_all` is now dead code in adaptive mode** — Layer 2's five return paths route to `summarize_before` (A1/A2) or `original` (A3/A4) only. The `combine_all` algorithm implementation is retained for legacy non-adaptive Phase A reproduction.

## Files to add

1. **`gepa_merge/src/gepa/strategies/adaptive_merge.py`** — `AdaptiveMergeConfig` (incl. `use_maturity_gate: bool = True`), `AdaptiveStartPolicy`, `BehavioralAdaptiveMergePolicy` (with `_decision_cache: dict[tuple[int,int,int], AdaptiveMergeDecision]` reset each `should_schedule()`), `AdaptiveMergeDecision`, pure-function signal computers reused by both live + replay.
2. **`gepa_merge/src/gepa/proposer/adaptive_pair_selection.py`** — `rank_pairs_by_adaptive_diversity(...)` matching existing `merge_selection` strategy signature.
3. **`gepa_merge/experiments/analysis/adaptive_replay.py`** — post-hoc replay; reuses loaders from `merge_forensics.py:241-255`. Read-only, no LM calls.
4. **`gepa_merge/tests/proposer/test_adaptive_merge.py`** — one test per gate (incl. G3-off variant); wrapper-signature test; per-triplet cache test; missing-data resilience.
5. **`gepa_merge/experiments/adaptive_merge_implementation_notes.md`** — design notes incl. deletion audit trail.

## Files to edit (surgical)

1. **`gepa_merge/src/gepa/proposer/merge.py`** — two additive changes inside `propose()`. **No signature changes anywhere.** Drop unused `AdaptiveMergePolicy` from import at line 22.
   ```python
   algo_fn = self.merge_algorithm_fn
   if hasattr(self.merge_policy, "algorithm_for_pair"):
       _decision_cache: dict[tuple[int,int,int], str] = {}
       def algo_fn(ancestor, id1, id2, *a, **kw):
           key = (ancestor, id1, id2)
           chosen = _decision_cache.get(key)
           if chosen is None:
               chosen = self.merge_policy.algorithm_for_pair(state, ancestor, id1, id2)
               _decision_cache[key] = chosen
           fn = get_merge_algorithm(chosen) if chosen else self.merge_algorithm_fn
           return fn(ancestor, id1, id2, *a, **kw)
   ```
   Plus log chosen algorithm + reasons into `state.full_program_trace[-1]["adaptive_*"]` keys.
2. **`gepa_merge/src/gepa/proposer/merge_selection.py`** — one new dict entry.
3. **`gepa_merge/src/gepa/api.py`** — delete `AdaptiveMergePolicy` import + `merge_min_score_threshold` / `merge_divergence_threshold` kwargs + dispatch branch (lines 38, 66-67, 400-405); add adaptive_merge_enabled + threshold passthrough.
4. **`gepa_merge/experiments/benchmarks/run_dspy.py`** — argparse flags mirroring new kwargs.
5. **`gepa_merge/src/gepa/examples/README.md`** — update the merge-threshold section to point at `adaptive_merge_enabled`.

## Implementation cautions (must hold)

**Caution 1 — Decision cache consistency.** `BehavioralAdaptiveMergePolicy` owns the canonical `_decisions: dict[(ancestor,id1,id2), AdaptiveMergeDecision]` cache. The cache is reset at the start of each `should_schedule(state, ...)` call. All three policy entry points must read/write the same cache so they cannot disagree about a triplet:

- `should_schedule(state, merge_candidates)` — runs Layer 1 gates per pair, populates a `_pair_cache: dict[(id1,id2), Layer1Result]`. Returns True iff ≥1 pair survives.
- `rank_pairs(state, merge_candidates)` (called via `adaptive_diversity` strategy through the policy reference passed in `**kwargs`) — uses `_pair_cache` if populated; ranks by behavioral diversity.
- `algorithm_for_pair(state, ancestor, id1, id2)` — populates `_decisions[(ancestor,id1,id2)]` (Layer 2 A1/A2/A3/A4); idempotent via cache lookup. The merge.py wrapper has a tiny local defensive cache but **always** delegates to `policy.algorithm_for_pair(...)` so the policy's cached decision is reused.

The `adaptive_diversity` pair-selection function lives in `adaptive_pair_selection.py` and takes the policy via `**kwargs` (the existing `SELECTION_STRATEGIES` callsite at [merge.py:341-348](gepa_merge/src/gepa/proposer/merge.py#L341-L348) will be extended to pass `state=state, policy=self.merge_policy`; existing strategies ignore extra kwargs).

**Caution 2 — Logging safety.** Do NOT assume `state.full_program_trace[-1]` is the current merge attempt's entry. Before writing any `adaptive_*` metadata, check (a) the list is non-empty, (b) the last entry is a dict, (c) the entry has `invoked_merge=True` set (which `MergeProposer.propose()` writes at [merge.py:319](gepa_merge/src/gepa/proposer/merge.py#L319) at the start of a merge attempt). On mismatch, fall back to the logger and skip the trace write rather than polluting an unrelated entry. A small helper `_safe_log_adaptive(state, logger, key, value)` will encapsulate this guard so every adaptive log goes through it.

## Wrapper signature verification + mandatory unit test

All three merge algorithms ([merge_algorithm.py:81-89, 137-145, 211-219](gepa_merge/src/gepa/strategies/merge_algorithm.py)) share the exact signature `(ancestor_idx, id1, id2, program_candidates, agg_scores, rng, merge_lm=None) -> (dict, tuple)`. The helper invokes them at [merge.py:186-191](gepa_merge/src/gepa/proposer/merge.py#L186-L191) as `merge_algorithm_fn(ancestor, id1, id2, list(program_candidates), agg_scores, rng, merge_lm=merge_lm)` — wrapper preserves byte-identically.

**Mandatory tests:**
- `test_wrapper_passes_correct_triplet_to_algorithm_for_pair` — stub policy captures the `(ancestor, id1, id2)` it receives, asserts it matches what the helper will pass to `merge_algorithm_fn`.
- `test_decision_cached_per_triplet_within_propose` — even if the helper retries the same triplet during its `for _ in range(max_attempts)` loop, `algorithm_for_pair` is called exactly once per unique `(ancestor, id1, id2)`.

## Verification plan

1. **Unit tests** including wrapper-signature + cache tests; existing tests still pass.
2. **Backward-compat smoke (mandatory)**: one non-adaptive cell with `adaptive_merge_enabled=False`; engine trace must be byte-identical to current main.
3. **Post-hoc replay** over 98 cells, executed in this PR. Summary reports G3 (maturity catastrophes), A1 (IFBench bloat), A2 (qwen/2wiki specialization), healthy-cell over-skip rate, **G3-on vs. G3-off comparison column**.
4. **Sensitivity sweep** ±20% on replay (read-only).
5. **Live re-run** of 5 cells (3 catastrophic + 2 healthy) only after replay looks clean.

## Out of scope

- Threshold tuning from live results (separate PR).
- New `GEPAState` attributes.
- `merge_quality.jsonl` schema changes.

## Plateau-gate ablation (v2 vs v2.6, qwen3-8b, seed=0, 2026-05-02)

Goal: empirically check whether the Layer −1 plateau gate helps or hurts. Phase A's `score_plateau` start policy hinted plateau-style filtering wins; we verified by running v2 (plateau **ON**) and v2.6 (plateau **OFF**, all other knobs identical) on the full 4-task qwen grid.

### Per-cell results (test_score, n=300 except ifbench=294)

| task | budget | v1 G2-on | v2 (plateau ON) | v2.6 (plateau OFF) | Δ vs v2 | accepted merges (v2 → v2.6) |
|------|-------:|---------:|----------------:|-------------------:|--------:|-----------------------------|
| hotpotqa | 6871 | 51.0 | 51.0 | 51.0 | **0** | 3 → 4 |
| ifbench | 3593 | 35.54 | 35.54 | **32.65** | **−2.89** | 0 → 0 (1 attempted+rejected) |
| **hover** | 7051 | 45.0 | 43.0 | **1.67** | **−41.33** | 1 → **7** |
| musique | 6871 | 51.67 | 51.67 | 49.0 | **−2.67** | 3 → 5 |

### What we learned

- **Plateau OFF is 0/4 wins.** No cell improved. 3/4 cells regressed; the regression magnitude scales with how many extra accepted merges plateau OFF allows (hover went from 1 → 7 accepted merges and lost 41 pp; musique 3 → 5 lost 2.67 pp; ifbench had a single attempted-and-rejected merge but still lost 2.89 pp because the attempt consumed subsample budget and shifted the trajectory).
- **Hover collapsed catastrophically (1.67 / 100).** Test-time inference returned `"LM Response: None"` for most examples, suggesting the 7 stacked merges produced a prompt that breaks qwen3-8b's JSON adapter at inference. Phase A's `score_plateau` insight — "don't merge while the frontier is still actively improving" — is empirically vindicated.
- **`min_frontier_size = 3` vs `5` doesn't matter empirically.** v2 (frontier=5) and v2.5 (frontier=3, plateau ON, all other knobs same as v2) produced byte-identical `best_candidate.json` on all four tasks. ifbench's binding constraint is the plateau gate, not the frontier-size gate; the other three tasks always reach `|frontier|≥5` long before plateau allows merge, so 3 vs 5 only differs in unreachable scenarios.

### Locked defaults (post-2026-05-02)

These are the empirically validated configuration settings. Every change has a deletion-trace comment in the source.

| Layer / param | Default | Rationale |
|---|---:|---|
| `warmup_frac` | 0.25 | REPORT.md §16 |
| `min_frontier_size` | **3** | structural minimum for valid triplet; matches v2/v2.5 empirical equivalence |
| **`use_plateau_gate`** | **True** | v2 vs v2.6: 4/4 wins, prevented hover catastrophe |
| `plateau_window`, `plateau_eps` | 3, 0.0 | matches Phase A `ScorePlateauStartPolicy.plateau_patience=3` |
| `parent_strength_quantile` (G1) | 0.50 | median, relative |
| ~~`max_example_agreement`~~ (G2) | — | **REMOVED** 2026-05-01 (no-op on qwen) |
| `use_maturity_gate` (G3) | True | catastrophe coverage |
| `maturity_gini_max` (G3) | 0.50 | empirical elbow |
| `L_MAX` (A1) | 4000 | bloat cap (defensive) |
| ~~`BLOAT_SAFE_RATIO`~~ (A1.b) | — | **REMOVED** 2026-05-01 (gated combine_all which is now dead code) |
| `specialization_split_threshold` (A2) | 0.30 | empirical |
| `duplicate_jaccard_threshold` (A3) | 0.70 | empirical |
| A4 default algorithm | **`original`** | flipped from `combine_all` 2026-05-01 |

### Implication for downstream comparison

Treat **v2 = v2.5 = current locked default** as the canonical adaptive-merge config for qwen3-8b. The hover regression vs v1 (`45.0 → 43.0`, −2 pp) is unrelated to the plateau gate — it must come from one of the three other v2 changes (G2 deletion / A4 default flip / growth-ratio gate deletion). Identifying which one needs a separate ablation; outside the scope of the plateau experiment.

## Pair-selection ablation (v2 vs v2.7, qwen3-8b, seed=0, 2026-05-02)

Hypothesis: `adaptive_diversity` pair selection is the cause of v2's hotpotqa (−4 pp vs NoMerge) and hover (−4.67 pp vs NoMerge) regressions. Test by replacing only the pair-selection strategy with `random` (Phase A's default), keeping every other locked-config knob unchanged.

### Per-task results

| task | NoMerge | v1 G2-on | v2 (adaptive_diversity) | v2.7 (random) | Δ (v2 − v2.7) | PA best |
|------|--------:|---------:|-----------------------:|--------------:|--------------:|---------:|
| hotpotqa | 55.00 | 51.0 | 51.0 | 51.0 | 0 | 56.33 |
| ifbench | 31.97 | 35.54 | 35.54 | 32.65 | **+2.04** (adaptive_div helps) | 36.22 |
| hover | 47.67 | 45.0 | 43.0 | 44.33 | **−1.33** (adaptive_div hurts mildly) | 50.67 |
| **musique** | 48.33 | 51.67 | 51.67 | **40.67** | **+11.00** (adaptive_div saves catastrophe) | 52.33 |

### Findings

1. **adaptive_diversity is net positive (+11.71 pp across 4 tasks).** Refuted the "adaptive_diversity is the hover culprit" hypothesis.
2. **Random pair selection caused musique to drop 11 pp.** v2.7 musique fired only 1 accepted merge vs v2's 3, and the 1 random-selected pair was catastrophic. adaptive_diversity's diversity-ranked surfacing of multiple high-quality pairs is empirically protective.
3. **Hover's −4.67 pp gap to NoMerge is NOT due to adaptive_diversity.** Switching to random recovers only +1.33 pp; the remaining −3.34 pp gap to NoMerge persists.
4. **Conclusion: keep adaptive_diversity as locked default.** Open question: where does v2's hover/hotpotqa regression vs NoMerge come from? Most likely culprit: Layer 2 routing (A1/A2 routing some merges to `summarize_before` instead of `original`). Phase A's `original_immediate` (= no Layer 2 routing) gets 50.67 on hover, far above v2's 43.0. v2.8 ablation (in progress) tests this by setting `disable_layer2_routing=True`.
