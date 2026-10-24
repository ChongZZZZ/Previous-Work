# Harness: Budget-Aware Coding Agent

A coding-agent harness built for Assignment 3 of Harvard CS2680, Modern AI Systems. It works on repository repair tasks using language models, tools, and feedback from tests, with limits on cost and execution time.

The central question was how to divide work between a stronger, more expensive model and a cheaper model. The harness lets the expert model explore and implement an initial solution, hands off to the standard model for verification and repair, and uses additional expert help when the remaining budget allows it.

## What the harness does

- Schedules up to five tasks concurrently in isolated Docker sandboxes.
- Provides tools for reading files, running commands, replacing text, and creating files.
- Tracks token usage, estimated cost, time, and per-task progress.
- Compacts long conversations while carrying forward requirements, changes, and selected evidence.
- Handles model API failures with bounded retries and tracks repeated failures during a task.
- Runs syntax checks after supported edits and submits patches for benchmark evaluation.

The [writeup](writeup.pdf) discusses the design, experiments, and tradeoffs. In particular, promising results on the small local task set did not always translate into better leaderboard performance.

## Code map

| File | Purpose |
| --- | --- |
| `starter_code/src/agentic_loop.py` | Concurrent task scheduling and shutdown handling |
| `starter_code/src/solver.py` | Model handoffs, verification, and repair logic |
| `starter_code/src/tools.py` | Tool schemas, execution, and edit validation |
| `starter_code/src/conversation.py` | Conversation and context management |
| `starter_code/src/llm.py` | Model calls, error handling, and retries |
| `starter_code/src/ledger.py` | Usage, cost, and event records |
| `starter_code/src/config.py` | Model policies, budgets, and execution limits |
| `starter_code/dispatcher/` | Course-provided task dispatcher and container infrastructure |
| `starter_code/evaluation_scripts/` | Course-provided local evaluation runner and benchmark setup |

## Running the course evaluation

This snapshot retains the original course runtime. It requires Python 3.11+, Docker with Linux/amd64 support, Git, curl, GNU `timeout`, and access to the CS2680 model API. The model names and pricing assumptions in `src/config.py` reflect the course environment.

From this folder:

```bash
cd starter_code

# Supply these values through your local environment or secret manager.
export CS2680_API_KEY="<your-course-api-key>"
export CS2680_MODEL_EXPERT="<expert-model-id>"
export CS2680_MODEL_STANDARD="<standard-model-id>"
export CS2680_MODEL_STARTER="<starter-model-id>"

bash evaluation_scripts/prepare_images.sh
python3 evaluation_scripts/run_all.py --limit 0  # infrastructure preflight
python3 evaluation_scripts/run_all.py --limit 1  # one task; uses the model API
```

The preparation script downloads the benchmark assets and builds the agent image. The runner sets `CS2680_BASE_URL` for the agent through its egress proxy. Before running, update `dispatcher/student_name.json` for your own course account. Previous run outputs must be moved aside before another run; the runner checks for them.

## Provenance

The student-developed harness is in `starter_code/src/`. The dispatcher, evaluation scripts, and `madsOpt.py` come from the Harvard CS2680 Assignment 3 starter infrastructure and are retained with their original comments. The benchmark is [SWE-bench Pro](https://github.com/scaleapi/SWE-bench_Pro-os).

Copied from the `assignment3/` directory of the coursework repository at commit `b5d59299734f3ec650a9486d290dd5e8a656b6f0`. The copied code and PDF are unchanged. Conversation archives, the duplicate submission ZIP, internal planning notes, and session-packaging helpers are excluded from this portfolio copy.
