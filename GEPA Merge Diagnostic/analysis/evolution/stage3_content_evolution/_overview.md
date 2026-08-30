# Stage 3 — Per-accept-event content evolution

Each accepted candidate is one accept event; the running-max val defines the Pareto-best frontier. We mark events where the running-max increases with **★** (new running-best) and where the cell's overall best_candidate is reached with **⭐**. For every accept event we report, per predictor, whether it was a pure passthrough, an inflation, a deflation, or a rewrite — and we extract the lines that were newly added (and dropped) by the operation.

Per-task timelines: see `stage3_content_evolution/{task}.md` for the full chronology of every accept event in every qwen Phase A cell.

## Overview: Pareto-best-updates by origin (per task, qwen Phase A, all 50 cells)

| Task | n cells | running-best updates total | reflect | merge | seed |
|------|--------:|--------------------------:|--------:|------:|-----:|
| hotpotqa | 10 | 50 | 31 | 9 | 10 |
| ifbench | 10 | 58 | 38 | 10 | 10 |
| hover | 10 | 56 | 28 | 18 | 10 |
| musique | 10 | 56 | 34 | 12 | 10 |
