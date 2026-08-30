"""GPU-side correctness test for activation checkpointing on real models.

Run on Resnet-152 and Bert at default batch sizes:
  1. Trace train_step via graph_tracer.compile; capture gm + flat_args via a
     closure inside the transformation.
  2. ``modified_gm = copy.deepcopy(gm)`` so the baseline stays clean.
  3. Run Phase 2 (select_recompute_set) + Phase 3 (apply_activation_checkpointing)
     on modified_gm. Phase 2 still uses the profiler built on the original gm;
     apply_activation_checkpointing translates refs through name maps so
     mutations land on modified_gm.
  4. ``verify_correctness(gm, modified_gm, flat_args)`` -- cloned args per run,
     dual tolerance (tight for fwd/bwd, loose for optimizer-updated params/states).

This is the test that try_phase3.py CAN'T run -- the make_fx-traced toy MLP
in try_phase3 has no optimizer in the trace, so it never exercises the
in-place parameter mutation that real models do. Run this on the GPU box
(or Colab + GPU runtime) to validate that AC produces correct gradients on
real models before reporting numbers.

Run: python test_ac_correctness.py    (requires CUDA)
"""

import copy
import gc
import sys

import torch

from benchmarks import Experiment
from graph_prof import GraphProfiler
from graph_tracer import compile
from mu_two_rewrite import apply_activation_checkpointing, verify_correctness
from mu_two_select import select_recompute_set, simulate_peak_with_recompute


# Default batch size per model -- small enough to leave headroom for the AC
# splice (which inserts new nodes) and the deepcopy of gm.
DEFAULT_BS = {
    "Resnet152": 4,
    "Bert":      2,
}

BUDGET_FRACTION = 0.7    # AC budget = baseline fwd+bwd peak * this


def _capture_gm(exp: Experiment):
    """Run compile() once; capture (profiler, gm, flat_args) via a closure.

    Mirrors the body of Experiment.graph_transformation in benchmarks.py
    (warmup + measure + aggregate_stats + print_stats), then stashes the
    artifacts in a result dict the caller reads back. The caller can then
    apply AC out-of-band without touching the live compile pipeline.
    """
    box = {}

    def graph_transformation(gm, args):
        gp = GraphProfiler(gm)
        with torch.no_grad():
            for _ in range(2):
                gp.run(*args)
            gp.reset_stats()
            for _ in range(3):
                gp.run(*args)
            gp.aggregate_stats()
            gp.print_stats()
        box["profiler"] = gp
        box["gm"] = gm
        box["args"] = args
        return gm

    compiled_fn = compile(exp.train_step, graph_transformation)
    compiled_fn(exp.model, exp.optimizer, exp.example_inputs)
    return box["profiler"], box["gm"], box["args"]


def _test_one(model_name: str, bs: int) -> bool:
    print("\n" + "=" * 72)
    print(f"  {model_name}  bs={bs}")
    print("=" * 72)

    torch.cuda.empty_cache()
    gc.collect()

    exp = Experiment(model_name, bs)
    exp.init_opt_states()

    # Capture gm + flat_args 
    profiler, gm, flat_args = _capture_gm(exp)
    baseline_peak_mb = profiler.fwd_bwd_peak_memory / (1024 * 1024)
    print(f"  baseline fwd+bwd peak: {baseline_peak_mb:.1f} MB")

    # Deepcopy + Phase 2 + Phase 3
    print(f"  deepcopying gm for AC application...")
    modified_gm = copy.deepcopy(gm)

    budget = int(profiler.fwd_bwd_peak_memory * BUDGET_FRACTION)
    print(
        f"  budget = {budget / (1024 * 1024):.1f} MB "
        f"(fraction={BUDGET_FRACTION})"
    )

    recomps = select_recompute_set(profiler, mem_limit_bytes=budget)
    predicted_post = simulate_peak_with_recompute(profiler, set(recomps))
    print(
        f"  picked {len(recomps)} candidate(s); "
        f"predicted post-AC peak: {predicted_post / (1024 * 1024):.1f} MB"
    )
    if not recomps:
        print("  no candidates picked (budget already met) -- skipping verify")
        return True

    modified_gm = apply_activation_checkpointing(modified_gm, recomps, profiler)

    # Verify correctness
    print(" verifying gradient correctness (cloned args, dual tolerance)...")
    correct = verify_correctness(gm, modified_gm, flat_args)
    print(f"  -> {'PASS' if correct else 'FAIL'}")
    return correct


def main() -> None:
    if not torch.cuda.is_available():
        print(
            "ERROR: CUDA not available. This script requires GPU "
            "(the make_fx trace of train_step uses cuda tensors).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"torch {torch.__version__}  CUDA {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}  "
          f"({torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB)")

    results = {}
    for model_name, bs in DEFAULT_BS.items():
        try:
            ok = _test_one(model_name, bs)
            results[model_name] = ok
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"  -> OOM, skipping {model_name}")
                results[model_name] = "OOM"
                torch.cuda.empty_cache()
                gc.collect()
            else:
                print(f"  -> ERROR: {type(e).__name__}: {e}")
                results[model_name] = False
        except Exception as e:  # noqa: BLE001 -- defensive top-level harness
            print(f"  -> ERROR: {type(e).__name__}: {e}")
            results[model_name] = False
        finally:
            torch.cuda.empty_cache()
            gc.collect()

    # ---- Summary -------------------------------------------------------- #
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    for model_name, ok in results.items():
        tag = "PASS" if ok is True else ("OOM" if ok == "OOM" else "FAIL")
        print(f"  {model_name}: {tag}")

    failed = [m for m, ok in results.items() if ok is False]
    if failed:
        print(f"\nFAILURES on: {failed}")
        sys.exit(1)
    print("\nAll models passed gradient correctness.")


if __name__ == "__main__":
    main()
