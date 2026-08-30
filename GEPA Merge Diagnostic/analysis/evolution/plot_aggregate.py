"""
Stage 1 Step 1.3 + 1.4: aggregate normalized trajectory per task + merge-timing histogram.
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "analysis/evolution/candidates.csv"
FIG_DIR = ROOT / "analysis/evolution/figures"


def load_rows():
    rows = list(csv.DictReader(open(CSV_PATH)))
    for r in rows:
        r["idx"] = int(r["idx"])
        r["val"] = float(r["val"]) if r["val"] not in (None, "") else None
        r["prompt_chars"] = int(r["prompt_chars"])
    return rows


def normalize_per_cell(items):
    """Normalize idx to [0, 1] within a cell, return (x_norm, val, chars, origin)."""
    if not items:
        return []
    items = sorted(items, key=lambda r: r["idx"])
    max_idx = max(r["idx"] for r in items)
    if max_idx == 0:
        return []
    out = []
    for r in items:
        x_norm = r["idx"] / max_idx
        out.append((x_norm, r["val"], r["prompt_chars"], r["origin"]))
    return out


def aggregate_trajectory(rows, task, n_bins=10):
    """Group all cells of one task; bin by x_norm; compute mean and 25/75 quantile."""
    task_rows = [r for r in rows if r["task"] == task and r["group"] == "phase_a_qwen"]
    cells = sorted({(r["task"], r["cell"]) for r in task_rows})
    bins = [[] for _ in range(n_bins)]
    char_bins = [[] for _ in range(n_bins)]
    for (t, c) in cells:
        items = [r for r in task_rows if r["cell"] == c]
        normd = normalize_per_cell(items)
        for x_norm, val, chars, _ in normd:
            if val is None:
                continue
            bin_idx = min(n_bins - 1, int(x_norm * n_bins))
            bins[bin_idx].append(val)
            char_bins[bin_idx].append(chars)
    xs = [(i + 0.5) / n_bins for i in range(n_bins)]
    means = [np.mean(b) if b else None for b in bins]
    q25 = [np.percentile(b, 25) if b else None for b in bins]
    q75 = [np.percentile(b, 75) if b else None for b in bins]
    char_means = [np.mean(b) if b else None for b in char_bins]
    return xs, means, q25, q75, char_means


def merge_timing(rows, task):
    """For each merge event, return its position in [0,1]."""
    task_rows = [r for r in rows if r["task"] == task and r["group"] == "phase_a_qwen"]
    cells = defaultdict(list)
    for r in task_rows:
        cells[(r["task"], r["cell"])].append(r)
    positions = []
    for cell_key, items in cells.items():
        items_sorted = sorted(items, key=lambda r: r["idx"])
        max_idx = max(r["idx"] for r in items_sorted)
        if max_idx == 0:
            continue
        for r in items_sorted:
            if r["origin"] == "merge":
                positions.append(r["idx"] / max_idx)
    return positions


def main():
    rows = load_rows()
    tasks = ["hotpotqa", "ifbench", "hover", "musique"]

    # Step 1.3: aggregate trajectory per task
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    for ax, task in zip(axes.flat, tasks):
        xs, means, q25, q75, char_means = aggregate_trajectory(rows, task)
        # filter None
        xs_v = [x for x, m in zip(xs, means) if m is not None]
        means_v = [m for m in means if m is not None]
        q25_v = [q for q in q25 if q is not None]
        q75_v = [q for q in q75 if q is not None]
        char_means_v = [c for c in char_means if c is not None]

        ax.plot(xs_v, means_v, "-o", color="#1f77b4", label="mean val (across 10 cells)")
        ax.fill_between(xs_v, q25_v, q75_v, alpha=0.2, color="#1f77b4", label="25-75 percentile")

        # right axis: prompt chars
        ax2 = ax.twinx()
        ax2.plot(xs_v, char_means_v, "--", color="gray", alpha=0.6, label="mean prompt chars")
        ax2.set_ylabel("prompt chars (mean)", color="gray", fontsize=9)
        ax2.tick_params(axis="y", colors="gray", labelsize=8)

        ax.set_title(f"{task} (n=10 cells aggregated, 10 bins on normalized timeline)", fontsize=10)
        ax.set_xlabel("fraction through optimization (idx / max_idx)", fontsize=9)
        ax.set_ylabel("val score", fontsize=9)
        ax.set_xlim(0, 1)
        ax.grid(True, alpha=0.2)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    out1 = FIG_DIR / "aggregate_trajectory.png"
    plt.savefig(out1, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"Aggregate trajectory: {out1}")

    # Step 1.4: merge timing histogram per task
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.5), sharey=True)
    for ax, task in zip(axes, tasks):
        positions = merge_timing(rows, task)
        if not positions:
            ax.set_title(f"{task} (no merges)", fontsize=10)
            continue
        ax.hist(positions, bins=10, range=(0, 1), color="#d62728", alpha=0.7, edgecolor="black")
        median_pos = np.median(positions)
        ax.axvline(median_pos, color="black", linestyle="--", linewidth=1.5,
                   label=f"median={median_pos:.2f}")
        ax.set_title(f"{task} (n={len(positions)} merges)", fontsize=10)
        ax.set_xlabel("fraction through optimization", fontsize=9)
        if task == "hotpotqa":
            ax.set_ylabel("# merge events", fontsize=9)
        ax.set_xlim(0, 1)
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.2)

    fig.suptitle("Where in the trajectory do merges fire? (Phase A qwen)", fontsize=11, y=1.02)
    plt.tight_layout()
    out2 = FIG_DIR / "merge_timing.png"
    plt.savefig(out2, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"Merge timing histogram: {out2}")

    # Print summary stats for prose
    print("\n=== merge timing summary (per task) ===")
    for task in tasks:
        positions = merge_timing(rows, task)
        if positions:
            print(f"  {task}: n={len(positions)}, median={np.median(positions):.2f}, "
                  f"q25={np.percentile(positions, 25):.2f}, q75={np.percentile(positions, 75):.2f}, "
                  f"first_decile={np.percentile(positions, 10):.2f}, "
                  f"last_decile={np.percentile(positions, 90):.2f}")


if __name__ == "__main__":
    main()
