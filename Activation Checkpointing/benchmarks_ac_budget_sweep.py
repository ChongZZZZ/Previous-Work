"""Phase 4 -- AC sweep over (model, batch_size, budget_fraction).

Extends benchmarks_ac_sweep.py with a budget_fraction dimension so the
trade-off between memory and latency can be plotted from a single CSV.

Sweep:
  model x batch_size x budget_fraction
where budget_fraction = None marks the baseline (AC disabled).

Output: one row per cell, written to ``ac_budget_sweep_results.csv``.
A separate notebook reads this CSV and produces the deliverable plots:
  - Peak memory vs mini-batch size (bar, w/ vs w/o AC)
  - Iteration latency vs mini-batch size (line, w/ vs w/o AC)

Latency protocol (same as benchmarks_ac_sweep.py):
  - 1st compiled_fn call triggers graph_transformation (profile + AC). NOT timed.
  - N_WARMUP warmup calls. NOT timed.
  - N_TIMED timed calls; each: cuda.synchronize() + perf_counter() + sync().
    Take the median.

Peak protocol:
  - peak_pre_ac_MB  = profiler.fwd_bwd_peak_memory (predicted, fwd+bwd only)
  - peak_post_ac_MB = simulate_peak_with_recompute(...) (= pre in baseline)
  - posthoc_peak_MB = cuda.max_memory_allocated() over one isolated iteration
"""

import csv
import gc
import os
import shutil
import time
from typing import Dict, List, Optional

import torch

from ac_pipeline import make_ac_graph_transformation
from benchmarks import Experiment
from graph_tracer import compile

# --------------------------------------------------------------------------- #
# Sweep config                                                                #
# --------------------------------------------------------------------------- #
SWEEP_MODELS: List[str] = ["Resnet152", "Bert"]
SWEEP_BATCH_SIZES: Dict[str, List[int]] = {
    "Resnet152": [2, 4, 8, 16, 32],
    "Bert":      [1, 2, 4, 8, 16],
}
# None -> baseline (no AC). Floats -> budget = fwd_bwd_peak * fraction.
SWEEP_BUDGETS: List[Optional[float]] = [None, 0.5, 0.6, 0.7, 0.8, 0.9]

N_WARMUP = 5
N_TIMED  = 20

OUT_CSV = "ac_budget_sweep_results.csv"

# Phase 1 profile CSVs that print_stats() writes to fixed filenames.
# We archive these into a per-(model, batch_size) folder on baseline cells
# so they aren't overwritten by later cells in the sweep.
PROFILE_CSVS = ["node_stats.csv", "activation_lifetimes.csv", "peak_memory_summary.csv"]


def _archive_profile_outputs(model_name: str, bs: int) -> None:
    """Move the three Phase 1 profile CSVs into ``profile_<model>_bs<bs>/``.

    Called only on baseline cells -- profile output is identical across
    budgets for a given (model, batch_size), so one archive per pair is
    enough.
    """
    out_dir = f"profile_{model_name}_bs{bs}"
    os.makedirs(out_dir, exist_ok=True)
    for fname in PROFILE_CSVS:
        if os.path.exists(fname):
            shutil.move(fname, os.path.join(out_dir, fname))


# --------------------------------------------------------------------------- #
# Single-cell run                                                             #
# --------------------------------------------------------------------------- #
def run_one(
    model_name: str, bs: int, budget_fraction: Optional[float]
) -> Dict[str, float]:
    """Run one (model, batch_size, budget_fraction) cell."""
    enable_ac = budget_fraction is not None
    config_label = "baseline" if not enable_ac else f"ac_{budget_fraction:.2f}"

    torch.cuda.empty_cache()
    gc.collect()

    exp = Experiment(model_name, bs)
    exp.init_opt_states()

    pipeline_results: Dict = {}
    transform = make_ac_graph_transformation(
        enable_ac=enable_ac,
        budget_fraction=budget_fraction if enable_ac else 1.0,
        results=pipeline_results,
        decisions_csv=(
            f"recompute_decisions_{model_name}_bs{bs}_{config_label}.csv"
        ),
    )
    compiled_fn = compile(exp.train_step, transform)

    # ---- First call: triggers graph_transformation (profile + AC) ------- #
    compiled_fn(exp.model, exp.optimizer, exp.example_inputs)

    # ---- Warm-up -------------------------------------------------------- #
    for _ in range(N_WARMUP):
        compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
    torch.cuda.synchronize()

    # ---- Timed iterations ----------------------------------------------- #
    times_ms: List[float] = []
    for _ in range(N_TIMED):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
        torch.cuda.synchronize()
        times_ms.append((time.perf_counter() - t0) * 1000.0)
    times_ms.sort()
    median_ms = times_ms[len(times_ms) // 2]

    # ---- Post-hoc whole-iter peak --------------------------------------- #
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
    torch.cuda.synchronize()
    posthoc_peak_bytes = torch.cuda.max_memory_allocated()

    pre_ac  = pipeline_results.get("peak_fwdbwd_pre_ac", 0)
    post_ac = pipeline_results.get("peak_fwdbwd_post_ac", pre_ac)
    n_rec   = pipeline_results.get("n_recomputed", 0)
    budget  = pipeline_results.get("budget_bytes", None)

    return {
        "model":             model_name,
        "batch_size":        bs,
        "config":            config_label,
        "budget_fraction":   budget_fraction if enable_ac else "",
        "peak_pre_ac_MB":    pre_ac / (1024 * 1024),
        "peak_post_ac_MB":   post_ac / (1024 * 1024),
        "posthoc_peak_MB":   posthoc_peak_bytes / (1024 * 1024),
        "n_recomputed":      n_rec,
        "budget_MB":         (budget / (1024 * 1024)) if budget else "",
        "latency_median_ms": median_ms,
        "latency_min_ms":    times_ms[0],
        "latency_max_ms":    times_ms[-1],
    }


# --------------------------------------------------------------------------- #
# Sweep driver                                                                #
# --------------------------------------------------------------------------- #
def main() -> None:
    fieldnames = [
        "model", "batch_size", "config", "budget_fraction",
        "peak_pre_ac_MB", "peak_post_ac_MB", "posthoc_peak_MB",
        "n_recomputed", "budget_MB",
        "latency_median_ms", "latency_min_ms", "latency_max_ms",
    ]
    rows: List[Dict] = []

    for model_name in SWEEP_MODELS:
        for bs in SWEEP_BATCH_SIZES[model_name]:
            for budget in SWEEP_BUDGETS:
                bf_str = "baseline" if budget is None else f"ac_{budget:.2f}"
                tag = f"{model_name} bs={bs} {bf_str}"
                print("\n" + "=" * 72)
                print(f"Running {tag}")
                print("=" * 72)
                try:
                    row = run_one(model_name, bs, budget)
                    rows.append(row)
                    print(
                        f"  -> peak_pre={row['peak_pre_ac_MB']:.1f} MB  "
                        f"peak_post={row['peak_post_ac_MB']:.1f} MB  "
                        f"posthoc={row['posthoc_peak_MB']:.1f} MB  "
                        f"latency={row['latency_median_ms']:.2f} ms  "
                        f"n_rec={row['n_recomputed']}"
                    )
                    if budget is None:
                        _archive_profile_outputs(model_name, bs)
                except RuntimeError as e:
                    if "out of memory" in str(e).lower():
                        print(f"  -> OOM, skipping {tag}")
                        torch.cuda.empty_cache()
                        gc.collect()
                    else:
                        print(f"  -> UNEXPECTED ERROR: {type(e).__name__}: {e}")
                except Exception as e:  # noqa: BLE001 -- defensive sweep harness
                    print(f"  -> UNEXPECTED ERROR: {type(e).__name__}: {e}")
                finally:
                    torch.cuda.empty_cache()
                    gc.collect()

                # Persist after every cell so a later crash doesn't lose work.
                with open(OUT_CSV, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for r in rows:
                        writer.writerow(r)

    print(f"\nWrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
