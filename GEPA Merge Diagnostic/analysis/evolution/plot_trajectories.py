"""
Stage 1 Step 1.1 + 1.2: trajectory plots per cell + 4-panel main figure.

Reads analysis/evolution/candidates.csv, plots dual-axis trajectories.
"""
import csv
import json
import os
import pickle
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path("/Users/zhaochong/Desktop/NLP_Project/gepa_merge")
CSV_PATH = ROOT / "analysis/evolution/candidates.csv"
FIG_DIR = ROOT / "analysis/evolution/figures"
CELL_DIR = FIG_DIR / "cells"
CELL_DIR.mkdir(parents=True, exist_ok=True)


def load_rows():
    rows = list(csv.DictReader(open(CSV_PATH)))
    for r in rows:
        r["idx"] = int(r["idx"])
        r["val"] = float(r["val"]) if r["val"] not in (None, "") else None
        r["prompt_chars"] = int(r["prompt_chars"])
        r["mc_at_disc"] = (
            int(r["mc_at_disc"]) if r["mc_at_disc"] not in (None, "", "None") else None
        )
    return rows


def find_best_idx(task: str, cell: str, group: str = "phase_a_qwen") -> int | None:
    """Find best_candidate's idx in this cell by reading best_candidate.json."""
    cell_dirs_to_try = []
    if group == "phase_a_qwen":
        cell_dirs_to_try += [
            ROOT / f"P3_result/phase_a_main/{task}/{cell}",
            ROOT / f"P4_result/phase_a_main/{task}/{cell}",
            ROOT / f"runs/musique/qwen3_8b/{cell}",
            ROOT / f"runs/phase_a_main_qwen/{task}/{cell}",
        ]
    for d in cell_dirs_to_try:
        bc = d / "best_candidate.json"
        gs = d / "gepa_state.bin"
        if bc.exists() and gs.exists():
            try:
                target = json.load(open(bc)).get("best_candidate")
                state = pickle.load(open(gs, "rb"))
                for i, c in enumerate(state.get("program_candidates", [])):
                    if c == target:
                        return i
            except Exception:
                continue
    return None


def plot_cell(rows, task, cell, group, out_path, title=None):
    items = [r for r in rows if r["task"] == task and r["cell"] == cell and r["group"] == group]
    items.sort(key=lambda r: r["idx"])
    if not items:
        return False

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    xs = [r["idx"] for r in items]
    vals = [r["val"] for r in items]
    chars = [r["prompt_chars"] for r in items]

    # right axis: prompt chars (background)
    ax2 = ax1.twinx()
    ax2.fill_between(xs, chars, alpha=0.08, color="gray", label="prompt chars")
    ax2.plot(xs, chars, "--", color="gray", alpha=0.4, linewidth=1)
    ax2.set_ylabel("prompt total chars", color="gray")
    ax2.tick_params(axis="y", colors="gray")

    # left axis: val score, colored by origin
    seeds = [r for r in items if r["origin"] == "seed"]
    refs = [r for r in items if r["origin"] == "reflect"]
    mrgs = [r for r in items if r["origin"] == "merge"]

    # connecting line in light gray
    ax1.plot(xs, vals, "-", color="lightgray", alpha=0.6, linewidth=1, zorder=1)
    if seeds:
        ax1.scatter([r["idx"] for r in seeds], [r["val"] for r in seeds],
                    c="black", s=80, marker="s", zorder=3, label="seed")
    if refs:
        ax1.scatter([r["idx"] for r in refs], [r["val"] for r in refs],
                    c="#1f77b4", s=40, zorder=3, label="reflect")
    if mrgs:
        ax1.scatter([r["idx"] for r in mrgs], [r["val"] for r in mrgs],
                    c="#d62728", s=80, marker="D", zorder=4, label="merge")
        for r in mrgs:
            ax1.axvline(r["idx"], color="#d62728", alpha=0.15, linewidth=1, zorder=0)

    # mark best_candidate
    best_idx = find_best_idx(task, cell, group)
    if best_idx is not None:
        for r in items:
            if r["idx"] == best_idx:
                ax1.scatter([r["idx"]], [r["val"]], marker="*", s=300,
                            c="gold", edgecolor="black", linewidth=1, zorder=5,
                            label="best_candidate")
                break

    ax1.set_xlabel("candidate index")
    ax1.set_ylabel("val score")
    ax1.set_title(title or f"{task} / {cell}")
    ax1.legend(loc="lower right", fontsize=8, framealpha=0.9)
    ax1.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()
    return True


def main():
    rows = load_rows()
    pa_qwen = [r for r in rows if r["group"] == "phase_a_qwen"]
    cells = sorted({(r["task"], r["cell"]) for r in pa_qwen})
    print(f"Phase A qwen cells to plot: {len(cells)}")

    n_done = 0
    for task, cell in cells:
        out = CELL_DIR / f"{task}__{cell}.png"
        if plot_cell(rows, task, cell, "phase_a_qwen", out):
            n_done += 1
    print(f"Per-cell plots written: {n_done} → {CELL_DIR}")

    # Step 1.2: 2x2 main figure with 4 PA-best cells
    pa_best = [
        ("hotpotqa", "original_score_plateau_s0", "HotpotQA · original_score_plateau (test 56.33)"),
        ("ifbench", "combine_all_budget_proportional_s0", "IFBench · combine_all_budget_proportional (test 36.22)"),
        ("hover", "original_immediate_s0", "HoVer · original_immediate (test 50.67)"),
        ("musique", "summarize_before_immediate_s0", "MuSiQue · summarize_before_immediate (test 52.33)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    for ax, (task, cell, title) in zip(axes.flat, pa_best):
        items = [r for r in rows if r["task"] == task and r["cell"] == cell and r["group"] == "phase_a_qwen"]
        items.sort(key=lambda r: r["idx"])
        if not items:
            ax.set_title(f"{title}\n(no data)")
            continue

        xs = [r["idx"] for r in items]
        vals = [r["val"] for r in items]
        chars = [r["prompt_chars"] for r in items]

        ax2 = ax.twinx()
        ax2.fill_between(xs, chars, alpha=0.08, color="gray")
        ax2.plot(xs, chars, "--", color="gray", alpha=0.4, linewidth=1)
        ax2.set_ylabel("chars", color="gray", fontsize=9)
        ax2.tick_params(axis="y", colors="gray", labelsize=8)

        ax.plot(xs, vals, "-", color="lightgray", alpha=0.6, linewidth=1)
        seeds = [r for r in items if r["origin"] == "seed"]
        refs = [r for r in items if r["origin"] == "reflect"]
        mrgs = [r for r in items if r["origin"] == "merge"]
        if seeds:
            ax.scatter([r["idx"] for r in seeds], [r["val"] for r in seeds],
                       c="black", s=70, marker="s", zorder=3, label="seed")
        if refs:
            ax.scatter([r["idx"] for r in refs], [r["val"] for r in refs],
                       c="#1f77b4", s=30, zorder=3, label="reflect")
        if mrgs:
            ax.scatter([r["idx"] for r in mrgs], [r["val"] for r in mrgs],
                       c="#d62728", s=70, marker="D", zorder=4, label="merge")
            for r in mrgs:
                ax.axvline(r["idx"], color="#d62728", alpha=0.12, linewidth=1)

        best_idx = find_best_idx(task, cell, "phase_a_qwen")
        if best_idx is not None:
            for r in items:
                if r["idx"] == best_idx:
                    ax.scatter([r["idx"]], [r["val"]], marker="*", s=250,
                               c="gold", edgecolor="black", linewidth=1, zorder=5,
                               label="best")
                    break

        ax.set_title(title, fontsize=10)
        ax.set_xlabel("candidate index", fontsize=9)
        ax.set_ylabel("val score", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.2)

    # one shared legend
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4,
               bbox_to_anchor=(0.5, 1.02), fontsize=10, framealpha=0.9)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    main_out = FIG_DIR / "main_trajectory_2x2.png"
    plt.savefig(main_out, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"Main 2x2 figure: {main_out}")


if __name__ == "__main__":
    main()
