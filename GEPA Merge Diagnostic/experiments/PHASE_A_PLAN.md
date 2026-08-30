# Project Plan — 21-day timeline, poster-first

**Deadline**: Poster v1 due **2026-05-07** (Thu). Paper final due
**2026-05-12** (Tue). Today: 2026-04-23.

This file replaces the earlier "Phase A-only" plan. It spans Phase A main
runs, Phase B.2 cross-scale validation, analysis, writeup, and poster
milestone.

---

## Ablation config (locked)

```
MERGE_ALGORITHMS = [original, combine_all, summarize_before]        # 3
START_POLICIES   = [immediate, score_plateau, budget_proportional]  # 3  (periodic dropped)
SEEDS            = [0]                                               # 1
BENCHMARKS       = [ifbench, pupa, hotpotqa, hover]                 # 4
MODELS (Phase A) = [openai/gpt-4.1-mini, together_ai/Qwen/Qwen3-8B] # 2
```

### Phase A grid (80 runs)
```
  9 configs × 4 benches × 2 models × 1 seed = 72 merge runs
+ 4 benches × 2 models × 1 seed NoMerge    =  8 baseline runs
─────────────────────────────────────────────────────────────
                                              80 runs total
```

### Phase B.2 cross-scale (4 extra runs)
On HotpotQA only, winner + NoMerge × {Qwen3-4B, Qwen3-14B} × 1 seed.
Validates that the winner strategy transfers across Qwen3 capability tiers.

**Grand total**: 84 runs, ~$490, ~2.5 days wall-clock with 4 teammates.

### Paper-aligned methodology
- Reflection LM = Task LM (paper `teacher_lm=None` fallback)
- Per-benchmark rollout budget matches MIPROv2's usage (paper §E.4):
  HotpotQA=6871, IFBench=3593, HoVer=7051, PUPA=2426
- `minibatch=3` (paper default)
- `max_merge_invocations=15` — **deviates from paper's 5**. Reason: cap=5
  binds asymmetrically across start policies (`immediate` hits it early and
  then behaves like NoMerge for the rest of the budget; `score_plateau` /
  `budget_proportional` may never reach it). That contaminates the policy
  ablation. Raising to 15 lets each policy reveal its actual triggering
  behavior. Not set to ∞ because `combine_all` concatenates prompts every
  merge — unbounded growth risks context-window overflow on HoVer/HotpotQA.
- `budget_proportional`'s `budget_fraction=0.33` (was default 0.25). Reason:
  on small-budget benches (PUPA=2426, IFBench=3593) a 0.25 trigger lands
  around iter ~15 out of ~60 total iter — too close to `immediate`'s iter
  ~3 trigger, the two policies produce near-identical search trees.
  0.33 shifts first trigger to iter ~20–25, giving clearer separation
  across the three policies. `score_plateau(patience=3)` kept at default —
  its behavior is task-adaptive by design.
- Single-model Qwen3 scaling on HotpotQA only (fastest signal)

**Scientific caveat**: n=1 per cell → no error bars. Claims are
qualitative ("winner consistent across task LMs and scale tiers"), not
statistically significant. Top-priority follow-on if budget allows:
seeds 1,2 on the winner config (+8 runs, ~$50).

---

## Per-run time & cost (paper budget in full)

| Bench | Budget | gpt-4.1-mini time | Qwen3-8B time | $/run mini | $/run qwen |
|---|---|---|---|---|---|
| IFBench | 3593 | ~2.5h | ~1.8h | $7 | $1.5 |
| PUPA | 2426 | ~1.7h | ~1.2h | $5 | $1 |
| HotpotQA | 6871 | ~4.6h | ~3.5h | $14 | $2.8 |
| HoVer | 7051 | ~5h | ~3.7h | $14 | $2.8 |

## Total cost

Derived from per-run estimates × 10 repetitions per bench (9 merge
configs + 1 NoMerge):

| Person × Benches | Calc | $ est |
|---|---|---|
| **P1** gpt-4.1-mini · HoVer + PUPA | 10×$14 + 10×$5 | **~$190** |
| **P2** gpt-4.1-mini · HotpotQA + IFBench | 10×$14 + 10×$7 | **~$210** |
| **P3** Qwen3-8B · HoVer + IFBench | 10×$2.8 + 10×$1.5 | **~$43** |
| **P4** Qwen3-8B · HotpotQA + PUPA + Phase B.2 | 10×$2.6 + 10×($0.7+$13.1) + $15 | **~$180** |
| **Phase A subtotal** | | **~$623** |

**P4 cost note** (revised 2026-04-24, was $51): PUPA uses a fixed LLM-judge
(`gpt-4.1-mini`, hardcoded per paper). For gpt-4.1-mini task LM (P1) the judge
is the same model, cost bundled. For Qwen3-8B task LM (P4), the judge is a
**separate OpenAI model call** — adds ~$13.1/run on PUPA (2426 rollouts ×
3 judge calls × ~3000 tokens each at gpt-4.1-mini rates). Originally omitted
from budget estimation. Paper-faithful setup requires this judge; cheaper
alternatives (gpt-4o-mini judge, Qwen3 self-judge) break cross-model PUPA
comparability and were rejected. See `setup_benchmarks.sh` for the
`PUPA_JUDGE_LM` env override mechanism that lets P4 route the judge through
OpenRouter instead of requiring a direct OpenAI key.
| Phase B.2 (bundled into P4 above) | 2×$1.5 + 2×$5 | $13 |
| **Required total (Phase A + Phase B.2)** | | **~$494** |

(Earlier plan had $401 — that under-estimated gpt-4.1-mini cost. Paper's
Table 2 reports $86 for GEPA × 6 benchmarks × 1 seed on gpt-4.1-mini;
extrapolating to our 40 gpt-4.1-mini runs gives ~$400 → consistent with
the updated $475 total including both Phase-A models.)

Cost is uneven (OpenAI is ~4-7× Together). Recommended: **share total
equally across the 4 teammates** (~$125 each), or arrange reimbursement
from OpenAI-slice teammates to Together-slice teammates.

### Optional add-ons (if time/budget permits after 5/3)

| Add-on | Extra runs | Extra $ | Gain |
|---|---|---|---|
| Seeds 1, 2 on winner config × all cells | 16 | ~$80 | n=3 error bars on headline number |
| Qwen3-32B on HotpotQA winner+NoMerge | 2 | ~$40 | Extends cross-scale to full 4B→32B range |
| Paper-exact math benchmarks (AIME + LiveBench-Math) | 16 | ~$70 | Matches all 6 paper benchmarks |

Grand total with **all** optional add-ons: ~$590 (still well under the
paper's total Table 2 spend of ~$500 per method).

### Why Qwen via Together is so much cheaper

Token pricing Jan-2026:
- `openai/gpt-4.1-mini`: **$0.40/M input + $1.60/M output**
- `together_ai/Qwen/Qwen3-8B`: **$0.18/M input + $0.18/M output**

Together's symmetric pricing + lower rate → ~3-5× cheaper per run. This
is also why P3/P4 slices finish cost-wise at $45-50 despite matching
P1/P2 in # runs and wall-clock.

---

## 4-person Phase A split — 1 model × 2 benches each

| Person | Model | Benchmarks | Runs | Est. time | Est. cost |
|---|---|---|---|---|---|
| **P1** | `openai/gpt-4.1-mini` | HoVer + PUPA | 20 | ~62h | ~$190 |
| **P2** | `openai/gpt-4.1-mini` | HotpotQA + IFBench | 20 | ~63h | ~$210 |
| **P3** | `together_ai/Qwen/Qwen3-8B` | HoVer + IFBench | 20 | ~62h | ~$43 |
| **P4** | `together_ai/Qwen/Qwen3-8B` | HotpotQA + PUPA (+ Phase B.2) | 20 + 4 | ~52h + overnight | ~$51 |

Each slice = 10 runs × 2 benches = 9 merge configs + 1 NoMerge per bench.

P1/P2 share gpt-4.1-mini; P3/P4 share Qwen3-8B via Together — **each
teammate needs their own API key** to avoid RPM throttling.

### Commands

```bash
# P1 (gpt-4.1-mini · HoVer + PUPA)
export OPENAI_API_KEY='sk-p1-...'
MODEL=openai/gpt-4.1-mini TASK_LIST="hover pupa" SEED_ONLY=0 \
  INCLUDE_NOMERGE=yes RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh

# P2 (gpt-4.1-mini · HotpotQA + IFBench)
export OPENAI_API_KEY='sk-p2-...'
MODEL=openai/gpt-4.1-mini TASK_LIST="hotpotqa ifbench" SEED_ONLY=0 \
  INCLUDE_NOMERGE=yes RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh

# P3 (Qwen3-8B · HoVer + IFBench)
export TOGETHER_API_KEY='...'
MODEL=together_ai/Qwen/Qwen3-8B TASK_LIST="hover ifbench" SEED_ONLY=0 \
  INCLUDE_NOMERGE=yes RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh

# P4 (Qwen3-8B · HotpotQA + PUPA)
export TOGETHER_API_KEY='...'
MODEL=together_ai/Qwen/Qwen3-8B TASK_LIST="hotpotqa pupa" SEED_ONLY=0 \
  INCLUDE_NOMERGE=yes RUNS_ROOT=runs/phase_a_main \
  bash experiments/run_phase_a.sh
```

---

## 21-day Timeline (parallel streams, poster-first)

Runs are mostly unattended (overnight) — **daytime is writeup/analysis time**.

| Date | Day | Runs status | Writeup / Poster |
|---|---|---|---|
| **4/24 Fri** | Setup | Pipeline done, keys distributed, `hypotheses.md` committed | Poster outline skeleton |
| **4/25 Sat** | Phase A #1 | 4 teammates launch overnight | § Introduction |
| **4/26 Sun** | Phase A #2 | Second overnight | § Related Work + § Method 3.2/3.3 |
| **4/27 Mon** | Phase A end | Final overnight + cleanup reruns | § Method 3.4 (Tier A metrics) + § Experimental Setup + **Poster layout v0** |
| **4/28 Tue** | **Winner analysis** | 80 runs aggregated → heatmap | § Results 5.1 Winner + **Poster "Main Result" panel** |
| **4/29 Wed** | Phase B.2 scaling | Qwen3-4B + Qwen3-14B overnight on HotpotQA | § Results 5.2 Per-benchmark + **Poster "Cross-model" panel** |
| **4/30 Thu** | Scaling integrate | 4 runs complete, cross-scale data in | § Cross-scale validation + **Poster "Cross-scale" bars** |
| **5/1 Fri** | Deep analysis | 4-quadrant merge-behavior plot from sidecars (offline) | § Merge behavior + **Poster "Diagnostic" panel** |
| **5/2 Sat** | Discussion | Write why Qwen3-8B merge-failure is fixed | § Discussion + **Poster "Why it works" takeaway** |
| **5/3 Sun** | Integrate v1 | First full paper draft | **Poster v1 all panels placed** |
| **5/4 Mon** | Polish data + **Phase C setup** | All 4 teammates redeem Prime Intellect $100 each; add `DISABLE_NO_THINK=1` env-var to `_make_lm`; launch Tier 1 thinking-on winner re-runs on all 4 Qwen3 benches | Poster figures polished |
| **5/5 Tue** | Poster layout + **Phase C runs** | Tier 1 thinking-on runs complete; numbers fed into paper draft | Poster v1 complete |
| **5/6 Wed** | Poster review | External feedback from 1–2 non-teammates | Poster v2 revised |
| **5/7 Thu** | **🎯 POSTER v1 DUE** | — | **Submit poster** |
| **5/8 Fri** | Paper integrate | Full paper walk-through | Paper polish pass |
| **5/9 Sat** | External proof | External reader for paper | Paper v2 |
| **5/10 Sun** | Final | Last-mile fixes | Paper final |
| **5/11 Mon** | **📄 Paper submit** | — | Submit paper |
| **5/12 Tue** | — | Emergency buffer | — |

---

## Poster v1 panels (6, each with data-lock deadline)

| Panel | Required data | Lock-by |
|---|---|---|
| Motivation | Paper Obs 5 quote (Qwen3 merge regression) | 4/24 |
| Method overview | 3 algos × 3 policies table | 4/27 |
| Experimental setup | 2 models × 4 benches matrix | 4/27 |
| **Main result: Winner** | Phase A heatmap | **4/28** |
| **Cross-scale**: 4B / 8B / 14B / gpt-4.1-mini | Phase B.2 scaling | **4/30** |
| **Merge behavior**: 4-quadrant plot (entropy × coverage × lift) | Offline analysis of sidecars | **5/2** |

---

## Phase C: Paper-exact validation (5/4–5/6, post-poster-submission)

### Why Phase C exists

Phase A runs Qwen3-8B with `/no_think` to control OpenRouter API cost. This
deviates from paper's thinking-on config and produces:
- HotpotQA baseline 41.3% (≈ paper 42.33%, n.s.) — free-form QA unaffected
- PUPA baseline ~60% vs paper 80.82% — structured-output task degenerates;
  mutation acceptance ≈ 0, merge ablation collapses to NoMerge baseline

Phase C re-runs the Phase A winner config with **thinking-on** to verify
that the Qwen3 merge-algorithm ranking is robust to thinking-mode choice.
Strengthens Paper v1 (5/11); not required for Poster v1 (5/7).

### Funding: $400 Prime Intellect credits

Each MIT 6.8610 student gets **$100 Prime Intellect credit** (promo code
`MITSPRING2026`, redeem at https://app.primeintellect.ai). 4 teammates × $100
= **$400 team budget**. Class-restricted — don't share outside 6.8610.

Credits are fungible across: **Inference (OpenRouter pass-through)**, hosted
GPUs, hosted training, sandboxes. Phase C uses the **OpenRouter pass-through
path**: same API as Phase A, just swap `OPENROUTER_API_KEY` to Prime
Intellect's pass-through key. No vLLM setup. No GPU rental. Zero code change
beyond a one-line `DISABLE_NO_THINK=1` env-var branch in `_make_lm`.

### What changes vs Phase A

| Component | Phase A (now) | Phase C |
|---|---|---|
| Qwen3-8B task LM | OpenRouter + `/no_think` injected | Prime Intellect OpenRouter pass-through + `DISABLE_NO_THINK=1` (thinking on) |
| gpt-4.1-mini PUPA judge | OpenRouter (Chong's $200 balance) | **unchanged** — keep on Chong's existing OpenRouter account to not burn Prime Intellect credit on judge |
| gpt-4.1-mini for P1/P2 | Own OpenAI keys | **unchanged** — Phase C only re-runs the Qwen3 side |

The only moving part is the Qwen3-8B endpoint. Judge and P1/P2 stuff stay
exactly as they are now.

### Winner definition (Phase A → Phase C input)

Phase C's "winner" is the single **(merge_algo, start_policy)** combination
with the best **aggregate score across all 8 Phase-A cells** (4 benchmarks ×
2 task LMs: Qwen3-8B + gpt-4.1-mini). This is a cross-model winner — the
combo that performs best averaged across both Qwen3-8B and gpt-4.1-mini.

If top-1 differs between the two models' aggregates (i.e., Qwen3's best ≠
gpt-4.1-mini's best), we run BOTH combos in Phase C and report both as
"cross-model top-2". Each adds ~$100 to Tier 1 scope.

### Scope (3 tiers, n=1 per cell — team pools $400 credit, decide cut on 5/3)

**No multi-seed**. n=1 per cell matches Phase A's seed protocol (paper itself
runs n=1 on most benches). Keeps Phase C's story simple: "we re-ran the
single-seed winner under thinking-on and the ranking held" — no need to
explain error-bar changes across configurations.

All 4 teammates redeem $100 each via `MITSPRING2026`. Credits can't transfer
across accounts, so we **treat team's $400 as a pool** — teammates run
their assigned slice from their own $100 credit.

**Tier 1 — Required** (winner + NoMerge × 4 Qwen3 benches × 1 seed)

| Config | Task LM | Judge | Total |
|---|---|---|---|
| PUPA Qwen3 thinking-on (winner + NoMerge) | ~$10 | ~$26 | ~$36 |
| IFBench Qwen3 thinking-on (winner + NoMerge) | ~$30 | — | ~$30 |
| HoVer Qwen3 thinking-on (winner + NoMerge) | ~$70 | — | ~$70 |
| HotpotQA Qwen3 thinking-on (winner + NoMerge) | ~$70 | — | ~$70 |
| **Tier 1 subtotal** | | | **~$206** |

**Tier 2 — Runner-up sanity check** (second-place combo × 4 benches × 1
seed; tests "winner margin robust?"): **~$90**

**Tier 3 — Phase B.2 14B thinking-on** (winner + NoMerge × HotpotQA on
Qwen3-14B, matching paper's cross-scale setting): **~$150-200**

Total if all 3 tiers = ~$446-496. **Slightly over $400 budget** if Tier 3
goes high. Cut order on 5/3 based on Phase A results:
1. Tier 1 (always required)
2. Tier 2 if winner's margin over runner-up is tight (<5% aggregate)
3. Tier 3 if Phase B.2 /no_think cross-scale looks unstable (trends don't
   fit a clean 4B<8B<14B monotonic story, suggesting /no_think artifact)
4. Drop Tier 2 or 3 if over budget

**Minimum viable = Tier 1 only** ($206). Leaves ~$194 buffer for debugging
/ retries / extending.

### Team split

Each teammate signs up Prime Intellect with their own @mit.edu email and
redeems $100 via `MITSPRING2026`.

| Teammate | Phase C slice | Est. spend |
|---|---|---|
| P1 (credit 1) | PUPA + HoVer Qwen3 thinking-on (Tier 1 half) | ~$106 |
| P2 (credit 2) | IFBench + HotpotQA Qwen3 thinking-on (Tier 1 half) | ~$100 |
| P3 (credit 3) | Tier 2 runner-up × 4 benches (decide 5/3 if run) | ~$90 |
| P4 (credit 4) | Tier 3 14B thinking-on (decide 5/3 if run) | ~$150-200 |

If Tier 3 runs, P4 might burn $150-200 which exceeds their $100 credit.
In that case P3/P4 split: P3 takes 14B HotpotQA winner ($75), P4 takes 14B
HotpotQA NoMerge ($75). Tier 2 (runner-up) then has to be skipped or
absorbed by unused credit from P1/P2 slice.

Judge calls (gpt-4.1-mini for PUPA) continue on Chong's existing OpenRouter
account ($200 balance, ~$26 needed for Tier 1 PUPA judges). Chong tops up
by ~$30 on 5/3 if needed.

### Execution (5/3 evening → 5/6)

1. **5/3 Sun evening** — Aggregate Phase A scores across 8 cells (4 benches
   × 2 task LMs). Identify:
   - **Cross-model winner** = (merge_algo, start_policy) with best aggregate
   - **Runner-up** (for potential Tier 3)
   - Whether Phase B.2 /no_think numbers look clean enough to skip Tier 4,
     or need thinking-on re-run
2. **5/3 Sun evening** — Commit `DISABLE_NO_THINK=1` env-var support in
   `_make_lm` (`run_dspy.py`): one-line branch to skip `/no_think` injection
   when env is set.
3. **5/4 Mon 9am** — All 4 teammates redeem Prime Intellect $100, generate
   OpenRouter pass-through keys.
4. **5/4 Mon 10am** — Launch slices:
   ```bash
   DISABLE_NO_THINK=1 \
   OPENROUTER_API_KEY=<prime-intellect-pass-through-key> \
   PUPA_JUDGE_LM="openrouter/openai/gpt-4.1-mini" \
   MODEL="openrouter/qwen/qwen3-8b" \
   REFLECTION_LM="openrouter/qwen/qwen3-8b" \
   MERGE_ALGO_ONLY="<winner_algo>" \
   START_ONLY="<winner_policy>" \
   INCLUDE_NOMERGE=yes \
   TASK_LIST="<my assigned benches>" \
   SEED_ONLY=0 \
   RUNS_ROOT=runs/phase_c_paper_exact \
   bash experiments/run_phase_a.sh 2>&1 | tee phase_c_<teammate>.log
   ```
   Judge calls silently route to Chong's main OpenRouter account (PUPA
   judge model string `openrouter/openai/gpt-4.1-mini` will use the
   `OPENROUTER_API_KEY` env — so for PUPA runs only, teammate needs to
   provide Chong's OpenRouter key for judge **or** we separate task-LM key
   from judge key via a second code change).
5. **5/5 Tue evening** — Tier 1 runs complete; integrate numbers.
6. **5/6 Wed** — Add Tier 2/3/4 if budget allows.

### Paper section draft (for 5/8–5/10 writeup)

> "To verify that the `/no_think` constraint in Phase A does not bias the
> merge-algorithm ranking, we re-ran the winning configuration under
> paper-exact thinking-on settings (Qwen-team-recommended temp=0.6,
> top-p=0.95, top-k=20) on all four Qwen3-8B benchmarks. The winner ranking
> held across all four benchmarks, with Qwen3 baselines recovering to within
> ±1% of paper's reported values (e.g., PUPA 80.9% vs paper 80.82%). This
> confirms our merge-algorithm conclusions are robust to thinking-mode
> choice, and isolates the `/no_think` → PUPA-degeneracy finding as a
> structured-output inference concern, not an ablation artifact."

**Reviewer defense**: anyone arguing "your `/no_think` might have confounded
the merge comparison" gets pointed to this section with direct evidence.

---

## Critical path

```
4/24 setup → 4/26-27 Phase A → 4/28 winner → 4/30 scaling done → 5/2 deep analysis →
5/3 poster v1 → 5/7 poster submit → 5/8-10 paper polish → 5/11 paper submit → 5/12 buffer
```

**Hardest checkpoint**: 4/28 must have "winner is X" conclusion. If Phase A
slips, poster v1 loses its main result panel.

**Softest task** (pure optional, paper-only): Phase C paper-exact validation
via Prime Intellect $400 credits (5/4–5/6). Re-runs Qwen3-8B winner config
with thinking-on to kill the "did /no_think bias the merge ranking?"
reviewer objection. Skippable if time-crunched; does not affect poster v1
(5/7 submission). Strengthens paper v1 (5/11).

---

## Risk register

### 🔴 HIGH: Phase A slips past 4/27
- Mitigation: `run_phase_a.sh` is idempotent (skips completed runs).
  Spare capacity on 4/28 to rerun failed ones. Writeup schedule has 1-day
  slack absorbed by compressing 4/30 cross-scale writeup into 5/1.

### 🟡 MEDIUM: Qwen3-14B on Together throttles or queues
- Mitigation: On 4/29 early morning, dry-run 1 14B rollout to check
  throughput. If unacceptable, drop to `{4B, 8B}` (2 runs instead of 4),
  cross-scale panel becomes "small vs medium" only.

### 🟡 MEDIUM: OpenAI rate limits on gpt-4.1-mini
- Mitigation: P1 and P2 use separate keys. If tier-1 RPM is hit, upgrade
  to tier-2 ($50 prepay).

### 🟢 LOW: 4-quadrant offline analysis
- Deterministic from sidecars. Minimal risk.

---

## Immediate actions (today / tomorrow)

### Today (4/23)
- [x] Pipeline code ready (`run_dspy.py` + `run_phase_a.sh`)
- [x] Smoke: `combine_all` on HoVer, `summarize_before` on IFBench
- [x] Plan doc (this file)
- [ ] Git commit all pipeline changes

### Tomorrow (4/24)
- [ ] Rotate `OPENAI_API_KEY` (key exposed in prior logs)
- [ ] 4 teammates each clone repo + run 1 IFBench smoke on their env/key
- [ ] Pre-register `hypotheses.md` with predictions:
      - winner prediction per (merge_algo, start_policy)
      - effect-size threshold for "beats NoMerge"
      - how cross-model agreement is evaluated (e.g., winner must
        beat NoMerge on ≥3 of 4 benches per model)
- [ ] Poster outline `experiments/poster/v0_outline.md` (5 min scaffold)

### Launch (4/25 morning)
- 4 teammates `bash experiments/run_phase_a.sh` with their assigned slice
