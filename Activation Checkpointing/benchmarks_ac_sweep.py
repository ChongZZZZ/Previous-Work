"""Phase 4 Steps 1 + 2 -- AC on/off sweep + iteration-latency measurement.

Runs Resnet-152 and Bert across batch sizes, twice each (config = baseline,
config = ac), and writes one CSV with per-config peak memory (predicted
fwd+bwd, post-hoc whole-iteration) and median iteration latency.

Latency protocol (per the plan):
  - 1st compiled_fn call triggers graph_transformation (profile + AC).
    NOT timed.
  - 5 warmup calls.                                     NOT timed.
  - 20 timed calls; each: cuda.synchronize() + perf_counter() + sync().
    Take the median.

Peak protocol:
  - pre_ac_peak  = profiler.fwd_bwd_peak_memory     (always; simulator)
  - post_ac_peak = simulate_peak_with_recompute(profiler, recomps)
                                                     (= pre_ac_peak in baseline)
  - posthoc_peak = cuda.max_memory_allocated()        (actual full-iter peak)
"""

import csv
import gc
import time
from typing import Dict, List

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
SWEEP_CONFIGS: List[str] = ["baseline", "ac"]

BUDGET_FRACTION = 0.7    # AC budget as a fraction of measured fwd+bwd peak
N_WARMUP        = 5
N_TIMED         = 20

OUT_CSV         = "ac_sweep_results.csv"


# --------------------------------------------------------------------------- #
# Single-config run                                                           #
# --------------------------------------------------------------------------- #
def run_one(model_name: str, bs: int, config: str) -> Dict[str, float]:
    """Run one (model, batch_size, config) cell. Returns a dict of metrics."""
    enable_ac = config == "ac"

    torch.cuda.empty_cache()
    gc.collect()

    exp = Experiment(model_name, bs)
    exp.init_opt_states()

    pipeline_results: Dict = {}
    transform = make_ac_graph_transformation(
        enable_ac=enable_ac,
        budget_fraction=BUDGET_FRACTION,
        results=pipeline_results,
        decisions_csv=f"recompute_decisions_{model_name}_bs{bs}.csv",
    )
    compiled_fn = compile(exp.train_step, transform)

    # First call: triggers graph_transformation (profile + AC)
    compiled_fn(exp.model, exp.optimizer, exp.example_inputs)

    #  Warm-up
    for _ in range(N_WARMUP):
        compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
    torch.cuda.synchronize()

    #  Timed iterations 
    #   cuda.Event is great for "how long did this kernel run on the device?" 
    #   It's a bad fit for "how long did one full training step take from the user's perspective?" 
    times_ms: List[float] = []
    for _ in range(N_TIMED):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
        torch.cuda.synchronize()
        times_ms.append((time.perf_counter() - t0) * 1000.0)
    times_ms.sort()
    median_ms = times_ms[len(times_ms) // 2]

    #  Post-hoc whole-iter peak (one isolated iteration)
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
    torch.cuda.synchronize()
    posthoc_peak_bytes = torch.cuda.max_memory_allocated()

    pre_ac = pipeline_results.get("peak_fwdbwd_pre_ac", 0)
    post_ac = pipeline_results.get("peak_fwdbwd_post_ac", pre_ac)
    n_rec = pipeline_results.get("n_recomputed", 0)
    budget = pipeline_results.get("budget_bytes", None)

    return {
        "model": model_name,
        "batch_size": bs,
        "config": config,
        "peak_pre_ac_MB":   pre_ac / (1024 * 1024),
        "peak_post_ac_MB":  post_ac / (1024 * 1024),
        "posthoc_peak_MB":  posthoc_peak_bytes / (1024 * 1024),
        "n_recomputed":     n_rec,
        "budget_MB":        (budget / (1024 * 1024)) if budget else "",
        "latency_median_ms": median_ms,
        "latency_min_ms":    times_ms[0],
        "latency_max_ms":    times_ms[-1],
    }


### Sweep driver
def main() -> None:
    fieldnames = [
        "model", "batch_size", "config",
        "peak_pre_ac_MB", "peak_post_ac_MB", "posthoc_peak_MB",
        "n_recomputed", "budget_MB",
        "latency_median_ms", "latency_min_ms", "latency_max_ms",
    ]
    rows: List[Dict] = []

    for model_name in SWEEP_MODELS:
        for bs in SWEEP_BATCH_SIZES[model_name]:
            for config in SWEEP_CONFIGS:
                tag = f"{model_name} bs={bs} config={config}"
                print("\n" + "=" * 72)
                print(f"Running {tag}")
                print("=" * 72)
                try:
                    row = run_one(model_name, bs, config)
                    rows.append(row)
                except RuntimeError as e:
                    if "out of memory" in str(e).lower():
                        print(f"  -> OOM, skipping {tag}")
                        torch.cuda.empty_cache()
                        gc.collect()
                    else:
                        print(f"  -> UNEXPECTED ERROR: {type(e).__name__}: {e}")
                except Exception as e:  
                    print(f"  -> UNEXPECTED ERROR: {type(e).__name__}: {e}")
                finally:
                    torch.cuda.empty_cache()
                    gc.collect()

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"\nWrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
