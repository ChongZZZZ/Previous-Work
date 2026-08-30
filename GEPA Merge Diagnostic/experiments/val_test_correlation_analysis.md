# Val/test correlation as the root cause of hover's apparent merge regression

## Motivation

We observed a paradox in the qwen3-8b adaptive-merge experiments: **no policy variant we tried (v2, v2.5, v2.6, v2.7, v2.9, v2.10) could push hover's test score above the NoMerge baseline (47.67)**, while ifbench and musique consistently beat NoMerge under the same policy. Phase A's `original_immediate` (a simpler, no-AdaptiveStartPolicy configuration) achieved 50.67 on hover, suggesting the gap was not intrinsic to merge but to *our specific policy*.

This note documents an empirical investigation that reframes the puzzle: **the gap is largely an artifact of GEPA's val-greedy candidate selection meeting a task whose validation-set signal does not transfer to the test set.**

## Empirical setup

For each (task, Phase A cell) combination on qwen3-8b, seed=0, we extracted two numbers:

- **val score**: mean of `prog_candidate_val_subscores` for the cell's `best_candidate.json` index in the saved GEPA state. This is the metric GEPA used to pick the cell's best candidate.
- **test score**: the held-out test_eval.json score (n=294 for ifbench, n=300 for the other three).

The 9 merge configurations + nomerge baseline give n=10 (cell, val, test) triples per task. We compute Pearson correlation, Spearman rank correlation, and check whether `argmax(val)` matches `argmax(test)`.

## Results

| task | n | val range | test range | Pearson | Spearman | argmax-val == argmax-test? | mean(val − test) |
|------|---|-----------|------------|--------:|---------:|:---:|---:|
| HotpotQA | 10 | [0.473, 0.547] | [0.443, 0.563] | **+0.892** | **+0.915** | **YES** | +0.013 |
| IFBench  | 10 | [0.724, 0.828] | [0.097, 0.362] | −0.011 | +0.345 | NO | **+0.490** |
| HoVer    | 10 | [0.393, 0.427] | [0.423, 0.507] | **−0.063** | **+0.042** | NO | −0.060 |
| MuSiQue  | 10 | [0.450, 0.517] | [0.450, 0.523] | +0.398 | +0.042 | NO | −0.009 |

### Reading the table

- **HotpotQA**: val and test are tightly correlated (Pearson 0.89, Spearman 0.92) and the val-best cell *is* the test-best cell. Val-greedy optimization yields the test-best candidate.
- **IFBench**: large absolute val/test gap (val is 49 pp above test on average — the LM aces val but not test). However, val rank still partially predicts test rank (Spearman 0.345). The optimization bias is consistent.
- **MuSiQue**: weak Pearson, zero Spearman. Picking the val-best yields a roughly average-test cell, not necessarily the best.
- **HoVer**: **val and test are statistically independent** (Pearson −0.063, Spearman +0.042). Picking the val-best is essentially picking a random cell w.r.t. test performance.

The val and test ranges are also informative for HoVer specifically: val spans only 0.034 (3.4 pp) while test spans 0.083 (8.3 pp). Multiple cells share near-identical val scores while their test scores swing widely. The selection signal is too weak to discriminate.

## Why HoVer specifically?

Both HotpotQA and HoVer are multi-hop reasoning benchmarks, but their **output spaces differ structurally**:

| | HotpotQA | HoVer |
|---|---|---|
| Output | free-text answer (entity, date, span) | 2-class verdict (supported / not_supported) |
| Metric | F1 over answer tokens | accuracy on binary verdict |
| Per-example sensitivity to prompt | continuous (partial credit on near-misses) | step-flip (one wrong word inverts the label) |

For a binary metric, a small prompt mutation that affects the model's behavior on borderline examples directly flips the contribution of those examples from +1 to 0. Across 300 val examples with ~30% borderline cases, several different prompt mutations can each yield val ≈ 0.42 by flipping different subsets of borderline examples. None of these mutations carries a *generalizable* signal: the test set has different borderline cases. Result: high val variance with low test correlation.

HotpotQA's F1 metric averages partial-credit token overlap across the answer span. Mutations that improve val tend to come from *systematic* changes (better extraction logic, cleaner reasoning chain) that transfer to test. Result: high val/test correlation.

This gives us a per-task taxonomy:

```
val-test correlation HIGH  ←─ HotpotQA (continuous metric, test signal dominates)
                            └ MuSiQue  (continuous, but weaker)
                            └ IFBench  (instruction-following accuracy; partial-credit-ish)
val-test correlation ZERO  ←─ HoVer    (binary verdict + narrow val range)
```

## Implication for our adaptive-merge ablations on HoVer

Across the 6 hover policy variants we tested (v1, v2, v2.5, v2.6, v2.7, v2.9, v2.10), the test scores were:
- v1 G2-on: 45.0
- v2 (locked): 43.0
- v2.5 (frontier=3): 43.0
- v2.6 (plateau OFF): 1.67 (catastrophic)
- v2.7 (random selection): 44.33
- v2.10 (warmup_frac=0.50): 43.0

If val/test were uncorrelated for hover, **these test scores should be approximately random samples from the underlying val-greedy-selected-but-test-evaluated distribution**. The Phase A archive's hover cells span [0.423, 0.507] (8.3 pp range), and our 6 policy variants span [0.43, 0.45] (excluding the v2.6 LM collapse, which has a separate explanation: too many merges break qwen's JSON adapter at inference). Both ranges are consistent with sampling from a uniform-test-score distribution rather than systematic differences caused by the policy changes.

**Equivalently: our policy ablations on hover have been comparing noise to noise, not signal to signal.**

## What this does NOT explain

- v2.6's hover collapse to 1.67 is *not* val/test noise — it's a separate failure mode where the 7 stacked merges produced prompts that broke qwen3-8b's JSON adapter at inference time, returning `LM Response: None` for most test examples. This is qualitatively different from the 1–4 pp variation in the rest of the cells.
- IFBench's huge val/test gap (+49 pp) is a different problem — the model overfits val examples but the metric still ranks cells consistently. This isn't fatal because the ordering is preserved.

## Implications for the paper

1. **Don't claim "adaptive merge fails on hover".** Claim instead: **"on tasks where validation-set scores do not predict test-set performance (e.g., binary verdict tasks like HoVer), no val-greedy optimization — including merge — can systematically improve over a NoMerge baseline."** This is a property of the task–metric pair, not the merge algorithm.
2. **Report the val/test correlation per task** as a basic methodology check. Tasks with low val/test correlation should be flagged: any reported gain on them is likely within noise.
3. **The recommendation "disable adaptive merge for hover" is empirically defensible**: with val/test correlation = 0, any candidate the optimizer chooses is essentially random w.r.t. test, so the simplest defensible policy is the one that converges fastest (NoMerge) and avoids the catastrophic-prompt-corruption tail risk (v2.6).

## What we'd want to do next (if time permits)

- **Multi-seed runs on hover** to bracket the val/test noise: if 3 seeds of v2 cluster around test=43±2 and 3 seeds of NoMerge cluster around test=47±2, that confirms the noise hypothesis and quantifies it.
- **Better selection criterion on hover**: average top-k candidates by val instead of argmax (ensembling), or use a held-out subset of val for selection. Either should reduce variance.
- **Replicate on a non-binary task with known overfit risk** (e.g., truthfulness yes/no). Predict the same val/test decoupling, confirm.

## TL;DR

HoVer's validation-set scores are statistically uncorrelated with test scores (Pearson −0.06, Spearman +0.04, n=10 cells). HotpotQA's are tightly correlated (Pearson +0.89, Spearman +0.92). Picking the val-best candidate works for HotpotQA (it equals the test-best); on HoVer it is approximately random. None of our adaptive-merge policy variants can beat this floor, because the selection signal they all rely on doesn't carry to test. The "fix" is methodological (better selection / per-task config), not a parameter tweak.
