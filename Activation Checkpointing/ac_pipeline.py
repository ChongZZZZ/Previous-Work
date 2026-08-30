"""Activation-checkpointing pipeline

Exposes a factory `make_ac_graph_transformation` that returns a function with
the same signature as `Experiment.graph_transformation` in benchmarks.py. The
returned function:
  1. Profiles the graph (warmup + measure + aggregate_stats + print_stats).
  2. Optionally runs Phase 2 selection + Phase 3 rewrite.
  3. Stashes pre-AC and post-AC peak memory + recompute decisions into a
     caller-supplied results dict, so the sweep harness can read them
     without parsing CSVs.

Designed so benchmarks.py never has to import or know about AC.
"""

import csv
from typing import Any, Callable, Dict, Optional

import torch
import torch.fx as fx

from graph_prof import GraphProfiler
from mu_two_rewrite import apply_activation_checkpointing
from mu_two_select import select_recompute_set, simulate_peak_with_recompute


def _write_recompute_decisions(recomps, path: str = "recompute_decisions.csv") -> None:
    """Dump the Phase 2 decisions to CSV. One row per recomputed candidate."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name",
            "size_MB",
            "recomp_time_ms",
            "recomp_cnt",
            "total_recomp_time_ms",
            "recompute_ratio",
            "n_recomp_srcs",
            "n_recomp_middle",
            "n_shared_recomp_srcs",
        ])
        for ci in recomps.values():
            writer.writerow([
                ci.node.name,
                f"{ci.size_bytes / (1024 * 1024):.4f}",
                f"{ci.recomp_time:.4f}",
                ci.recomp_cnt,
                f"{ci.total_recomp_time:.4f}",
                f"{ci.recompute_ratio:.4f}",
                len(ci.recomp_srcs),
                len(ci.recomp_middle),
                len(ci.shared_recomp_srcs),
            ])


def make_ac_graph_transformation(
    enable_ac: bool = False,
    budget_fraction: float = 0.7,
    budget_bytes: Optional[int] = None,
    warm_up_iters: int = 2,
    profile_iters: int = 3,
    results: Optional[Dict[str, Any]] = None,
    decisions_csv: str = "recompute_decisions.csv",
) -> Callable[[fx.GraphModule, Any], fx.GraphModule]:
    """Factory. Returns a transform with signature ``(gm, args) -> gm,
    suitable to pass as the second argument of graph_tracer.compile.

    Parameters
    ----------
    enable_ac
        If False, behaves identically to the existing graph_transformation
    budget_fraction
        fwd_bwd_peak * budget_fraction
    budget_bytes
        Absolute memory budget
    warm_up_iters / profile_iters
        Same defaults as benchmarks.py in phase 1
    results
        Optional dict; populated with peak / decision stats so the sweep
        harness can read them without parsing CSVs.
    decisions_csv
        Path for the per-candidate decisions dump.
    """

    def _transform(gm: fx.GraphModule, args: Any) -> fx.GraphModule:
        graph_profiler = GraphProfiler(gm)

        with torch.no_grad():
            for _ in range(warm_up_iters):
                graph_profiler.run(*args)
            graph_profiler.reset_stats()

            for _ in range(profile_iters):
                graph_profiler.run(*args)
            graph_profiler.aggregate_stats()
            graph_profiler.print_stats()

        peak_pre = graph_profiler.fwd_bwd_peak_memory
        if results is not None:
            results["peak_fwdbwd_pre_ac"] = peak_pre

        if not enable_ac:
            if results is not None:
                results.setdefault("peak_fwdbwd_post_ac", peak_pre)
                results.setdefault("n_recomputed", 0)
                results.setdefault("budget_bytes", None)
            return gm

        if budget_bytes is not None:
            budget = int(budget_bytes)
        else:
            budget = int(peak_pre * budget_fraction)

        print(
            f"[AC] baseline fwd+bwd peak = "
            f"{peak_pre / (1024 * 1024):.1f} MB; "
            f"budget = {budget / (1024 * 1024):.1f} MB "
            f"(fraction={budget_fraction})"
        )

        recomps = select_recompute_set(graph_profiler, mem_limit_bytes=budget)
        peak_post_predicted = simulate_peak_with_recompute(
            graph_profiler, set(recomps)
        )
        print(
            f"[AC] picked {len(recomps)} candidate(s); "
            f"predicted post-AC fwd+bwd peak = "
            f"{peak_post_predicted / (1024 * 1024):.1f} MB"
        )

        _write_recompute_decisions(recomps, decisions_csv)

        gm = apply_activation_checkpointing(gm, recomps, graph_profiler)

        if results is not None:
            results["peak_fwdbwd_post_ac"] = peak_post_predicted
            results["n_recomputed"] = len(recomps)
            results["budget_bytes"] = budget

        return gm

    return _transform
