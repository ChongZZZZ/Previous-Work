# Activation Checkpointing for PyTorch Training (μ-TWO)

A from-scratch implementation of the activation-checkpointing system from the
[μ-TWO paper (MLSys 2023)](https://proceedings.mlsys.org/paper_files/paper/2023/file/a72071d84c001596e97a2c7e1e880559-Paper-mlsys2023.pdf),
built on `torch.fx` for the Harvard CS265 (Machine Learning Systems) project.
The system traces a **full training iteration** (forward + backward + optimizer) into a single
computation graph, profiles it, decides which activations to discard-and-recompute under a memory
budget, and rewrites the graph to enact those decisions — with end-to-end gradient correctness
verified against the unmodified graph on ResNet-152 and BERT-base.

**Headline result:** on ResNet-152 at batch size 128, a 0.5× memory budget cuts predicted
forward+backward peak memory by **~11.2 GB (≈50%)** for only **~16% added iteration latency**
(median over 20 timed iterations on an H100).

## How it works

The system is organized as a three-phase pipeline (wired together in `ac_pipeline.py`):

**Phase 1 — Graph profiler** (`graph_prof.py`, `graph_tracer.py`)
Traces one training step into a single FX graph, partitions it into forward / backward / optimizer
regions via separator ops, classifies every node (parameter, gradient, activation, optimizer state,
other), measures per-operator runtime (CUDA events) and memory delta, and records each activation's
lifetime: last forward use, first/last backward use, and idle interval in between.

**Phase 2 — Greedy recompute selection** (`mu_two_select.py`)
Implements μ-TWO's greedy scheduler: repeatedly evict the activation with the highest
`recompute_ratio = size_bytes / total_recompute_time` until a memory simulator predicts the peak
meets the budget. Handles the tricky parts of the paper's Algorithms E–G: when an activation is
evicted, every candidate that depends on it inherits its recomputation cost, and each candidate's
recomputation-source set must stay closed under the invariant *placeholder ∨ retained activation ∨
already-recomputed activation whose backward window covers ours*.

**Phase 3 — FX graph rewriter** (`mu_two_rewrite.py`)
For each activation chosen for recomputation, extracts the minimal forward subgraph that produces
it, splices a copy **just before its first backward use** (so the recomputed tensor lives as briefly
as possible), and redirects only the backward consumers to the copy — the forward pass is left
untouched. Correctness is verified end-to-end with a dual-tolerance `torch.allclose` scheme that
separates real bugs from expected float-reduction-order drift amplified by Adam.

## Results

Full write-ups with analysis are in [Report/REPORT.md](Report/REPORT.md) (profiler) and
[Report/PHASE2_PHASE3_REPORT.md](Report/PHASE2_PHASE3_REPORT.md) (algorithm + rewriter + sweep).
The sweep covers `(model, batch size, budget fraction)` over ResNet-152 (bs 4–128) and BERT-base
(bs 2–64) with budgets 0.5–0.9× of the baseline peak; raw numbers are in
[results/ac_budget_sweep_results.csv](results/ac_budget_sweep_results.csv).

![Predicted fwd+bwd peak memory vs batch size](figures/ac_sweep_peak_memory.png)

![Latency overhead vs batch size (healthy zone)](figures/ac_sweep_latency_overhead_healthy.png)

Highlights:

- **ResNet-152** shows the textbook trade-off: AC curves are strictly ordered by budget at every
  batch size, and the saving grows from ~430 MB (bs=4) to ~11.2 GB (bs=128). Budget 0.9 costs 1–3%
  latency; budget 0.5 costs 16–39%.
- **BERT at small batch sizes** exposes a real algorithmic limit: parameters + Adam state
  (~1.3 GB) already exceed a 0.5× budget, so no selection of activations can reach the target — the
  greedy loop evicts *every* candidate and latency blows up ~30× on a launch-bound GPU. The reports
  trace this to a hard memory floor and quantify it.
- **Profiler accounting matters:** BERT's candidates are dominated by view-class ops whose
  "size" is logical, not allocated, which skews the greedy ratio. The reports analyze how the real
  savings at large batch sizes come from the parent tensors recomputed alongside the picked views.
- **Correctness:** the rewritten graphs pass gradient verification against the baseline on both
  real models (`test_ac_correctness.py`).

## Repository layout

| File | Role |
|------|------|
| `graph_tracer.py` | Traces a full training step into one FX graph (separator ops mark region boundaries) |
| `graph_prof.py` | Phase 1: per-op runtime/memory profiling, node classification, activation lifetimes, peak-memory simulation |
| `mu_two_select.py` | Phase 2: candidate construction, recompute-ratio greedy loop, memory simulator |
| `mu_two_rewrite.py` | Phase 3: subgraph extraction, just-in-time splicing, use redirection, correctness verification |
| `ac_pipeline.py` | Wires Phases 1–3 into a single `graph_transformation` for the compile hook |
| `activation_checkpoint.py` | Minimal demo of the rewrite technique on a toy two-layer network |
| `test_ac_correctness.py` | End-to-end gradient verification of the rewritten graph (GPU) |
| `benchmarks_ac_budget_sweep.py` | 3D sweep driver: `(model, batch size, budget)` → CSVs |
| `benchmarks.py`, `benchmarks_ac_sweep.py`, `plot_ac_sweep.py` | Earlier benchmark drivers and plotting |
| `analysis.ipynb`, `analysis_ac_sweep.ipynb` | Analysis notebooks that produce the report figures |
| `starter_code.py`, `utils.py` | Course starter harness (models, training-step wrapper) |

## Running it

Requires a CUDA GPU (developed against PyTorch 2.5.1 / CUDA 12.4, Python 3.12).

```bash
python starter_code.py                  # profile a model (Phase 1)
python test_ac_correctness.py           # verify rewritten-graph gradients (Phases 2+3)
python benchmarks_ac_budget_sweep.py    # full sweep (~70–80 min on H100)
```

## References

- Purandare, Wasay, Jain, Idreos. *μ-TWO: 3× Faster Multi-Model Training with Orchestration and
  Memory Optimization.* MLSys 2023.
- Built on the [Harvard CS265](http://daslab.seas.harvard.edu/classes/cs265) starter code
  (`graph_tracer.py`, `starter_code.py`, `utils.py` scaffolding; MPL-2.0, see `LICENSE`).
