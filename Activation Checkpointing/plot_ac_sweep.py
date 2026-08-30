"""Phase 4 Step 3 -- plots from ac_sweep_results.csv.

Produces two figures:
  ac_sweep_peak_memory.png  - grouped bar chart of fwd+bwd peak memory
                              (baseline vs AC) per (model, batch_size).
  ac_sweep_latency.png      - line chart of median iteration latency
                              (baseline vs AC) per (model, batch_size).

Reads ac_sweep_results.csv produced by benchmarks_ac_sweep.py. Skips models
or batch sizes that don't have both configs (e.g., one OOMed).

Run: python plot_ac_sweep.py
"""

import csv
from collections import defaultdict
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


CSV_PATH = "ac_sweep_results.csv"


def _load(csv_path: str) -> Dict[Tuple[str, int, str], Dict]:
    """Load CSV into a dict keyed by (model, batch_size, config)."""
    rows: Dict[Tuple[str, int, str], Dict] = {}
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r["model"], int(r["batch_size"]), r["config"])
            rows[key] = r
    return rows


def _models_in(rows) -> List[str]:
    return sorted({k[0] for k in rows})


def _matched_bs(rows, model: str) -> List[int]:
    """Batch sizes that have BOTH baseline and ac results for the given model."""
    bs_baseline = {k[1] for k in rows if k[0] == model and k[2] == "baseline"}
    bs_ac       = {k[1] for k in rows if k[0] == model and k[2] == "ac"}
    return sorted(bs_baseline & bs_ac)


def plot_peak_memory(rows, out_path: str) -> None:
    """Grouped bar chart, one subplot per model, baseline vs AC posthoc peak."""
    models = _models_in(rows)
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4.5))
    if len(models) == 1:
        axes = [axes]

    for ax, model in zip(axes, models):
        bss = _matched_bs(rows, model)
        if not bss:
            ax.set_title(f"{model}: no matched data")
            continue
        baseline_mb = [float(rows[(model, bs, "baseline")]["posthoc_peak_MB"]) for bs in bss]
        ac_mb       = [float(rows[(model, bs, "ac")]["posthoc_peak_MB"])       for bs in bss]
        ac_predicted = [float(rows[(model, bs, "ac")]["peak_post_ac_MB"])      for bs in bss]

        x = np.arange(len(bss))
        width = 0.28
        ax.bar(x - width, baseline_mb,  width, label="baseline (post-hoc)")
        ax.bar(x,         ac_mb,        width, label="AC (post-hoc)")
        ax.bar(x + width, ac_predicted, width, label="AC (simulator)", alpha=0.7)

        ax.set_title(f"{model}: peak fwd+bwd memory")
        ax.set_xlabel("batch size")
        ax.set_ylabel("peak memory (MB)")
        ax.set_xticks(x)
        ax.set_xticklabels([str(bs) for bs in bss])
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"wrote {out_path}")


def plot_latency(rows, out_path: str) -> None:
    """Line chart, baseline vs AC median latency, one subplot per model."""
    models = _models_in(rows)
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4.5))
    if len(models) == 1:
        axes = [axes]

    for ax, model in zip(axes, models):
        bss = _matched_bs(rows, model)
        if not bss:
            ax.set_title(f"{model}: no matched data")
            continue
        baseline_lat = [float(rows[(model, bs, "baseline")]["latency_median_ms"]) for bs in bss]
        ac_lat       = [float(rows[(model, bs, "ac")]["latency_median_ms"])       for bs in bss]

        ax.plot(bss, baseline_lat, marker="o", label="baseline")
        ax.plot(bss, ac_lat,       marker="s", label="AC")
        ax.set_title(f"{model}: median iteration latency")
        ax.set_xlabel("batch size")
        ax.set_ylabel("latency (ms)")
        ax.set_xscale("log", base=2)
        ax.set_xticks(bss)
        ax.set_xticklabels([str(bs) for bs in bss])
        ax.legend()
        ax.grid(linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"wrote {out_path}")


def print_savings_summary(rows) -> None:
    """Console summary: % memory saved and % latency overhead per cell."""
    models = _models_in(rows)
    print("\n" + "=" * 78)
    print(f"{'model':<12} {'bs':>4}  {'mem_saved%':>12} {'latency_overhead%':>18}  n_rec")
    print("=" * 78)
    for model in models:
        for bs in _matched_bs(rows, model):
            base = rows[(model, bs, "baseline")]
            ac   = rows[(model, bs, "ac")]
            base_mem = float(base["posthoc_peak_MB"])
            ac_mem   = float(ac["posthoc_peak_MB"])
            base_lat = float(base["latency_median_ms"])
            ac_lat   = float(ac["latency_median_ms"])
            mem_saved_pct = 100.0 * (base_mem - ac_mem) / base_mem if base_mem else 0.0
            lat_overhead_pct = 100.0 * (ac_lat - base_lat) / base_lat if base_lat else 0.0
            print(
                f"{model:<12} {bs:>4}  {mem_saved_pct:>11.1f}% "
                f"{lat_overhead_pct:>17.1f}%  {ac['n_recomputed']:>5}"
            )


def main() -> None:
    rows = _load(CSV_PATH)
    if not rows:
        print(f"No rows in {CSV_PATH} -- run benchmarks_ac_sweep.py first")
        return
    plot_peak_memory(rows, "ac_sweep_peak_memory.png")
    plot_latency(rows, "ac_sweep_latency.png")
    print_savings_summary(rows)


if __name__ == "__main__":
    main()
