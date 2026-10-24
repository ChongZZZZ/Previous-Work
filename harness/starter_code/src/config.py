"""Harness settings: model tiers and prices, limits, and where our own logs go.

The course API settings are environment variables, not config: CS2680_API_KEY and
CS2680_MODEL_EXPERT / CS2680_MODEL_STANDARD / CS2680_MODEL_STARTER (exported on the host,
passed in by run_all.py) and CS2680_BASE_URL (set by run_all.py to the egress proxy, the agent
container's only way to the API). They are read with os.environ; the URL is never hard-coded.

Values marked "probe" are first guesses until the API probe (PHASE1_NOTES.md, run ladder
step 3) has measured them. Every value here is written into the ledger's `run` row, so each
run's numbers can be traced back to the settings that produced them.
"""
import os

# --- models and prices ---------------------------------------------------------------------

MODEL_EXPERT = os.environ.get("CS2680_MODEL_EXPERT", "expert")
MODEL_STANDARD = os.environ.get("CS2680_MODEL_STANDARD", "standard")
MODEL_STARTER = os.environ.get("CS2680_MODEL_STARTER", "starter")

# $ per 1M tokens: (fresh input, cached input, output). UNDERSTANDING.md section 4, from the
# assignment page. `prompt_tokens` includes the cached tokens (PHASE0_FINDINGS.md section 2c).
PRICES_PER_M = {
    MODEL_EXPERT: (2.00, 0.10, 10.00),
    MODEL_STANDARD: (0.08, 0.004, 0.28),
    MODEL_STARTER: (0.01, 0.0005, 0.04),
}
# A model id we have no price for is charged at the Expert price, so the guards err on the
# side of stopping early; the ledger flags such calls.
UNKNOWN_MODEL_PRICE = PRICES_PER_M[MODEL_EXPERT]

# The guards read the ledger's $ total times this factor. Which formula the leaderboard bills
# (cache-discounted, as the ledger computes it, or cache-blind from the trace's token counts)
# is checked on the first leaderboard submission; until then "ledger".
GUARD_FORMULA = "ledger"          # "ledger" | "blind"
LEDGER_SAFETY = 1.10


def _positive_int(value, default):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


# --- the run (src/agentic_loop.py) -------------------------------------------------------------

MODEL = MODEL_STANDARD            # the first attempt of every task (retries: RETRY_MODEL below)
# The whole run must end RUN_LIMIT_S after the first task is opened (run_all.py A3_RUN_LIMIT_S;
# the host does not pass that to the agent, so a short local run sets both, scripts/a3_run.sh).
RUN_LIMIT_S = _positive_int(os.environ.get("CS2680_A3_RUN_LIMIT_S"), 4 * 3600)
STOP_OPEN_FRAC = 0.8125           # no new task after 3h15m of 4h
WRAP_FRAC = 0.9375                # every task wraps up at 3h45m of 4h
# The run's budget: $10 per leaderboard submission; a local run can set less
# (CS2680_A3_BUDGET_USD, scripts/a3_run.sh --budget). No new task after 85% of it, as the guards
# count it (ledger x LEDGER_SAFETY); every task wraps up at 95%.
def _positive_float(value, default):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


RUN_BUDGET_USD = _positive_float(os.environ.get("CS2680_A3_BUDGET_USD"), 10.0)
STOP_OPEN_USD = 0.85 * RUN_BUDGET_USD
WRAP_USD = 0.95 * RUN_BUDGET_USD
INITIAL_CAP = 5                   # tasks open at once; lowered to the host's limit when refused
NEXT_TASK_BACKOFF_MAX_S = 60      # after a next_task error that is not "too many live tasks"
SCHED_TICK_S = 5                  # the scheduler re-checks the guards at least this often
SCHED_MAX_ERRORS = 5              # scheduler exceptions in a row before it stops opening tasks
SHUTDOWN_JOIN_S = 30              # after DispatcherShutdown, how long run() waits for the workers

# --- one task (src/solver.py) -----------------------------------------------------------------

# Model calls per task. run_all.py passes MADSOPT_MAX_ITERATIONS through to the agent; if the
# grader sets it, it is honoured.
TASK_MAX_CALLS = min(120, _positive_int(os.environ.get("MADSOPT_MAX_ITERATIONS"), 120))
TASK_MAX_USD = 0.40
TASK_MAX_S = 1800
WRAPUP_FRAC = 0.8                 # the wrap-up message: at 80% of the calls or $ cap ...
WRAPUP_TIME_LEFT_S = 360          # ... or with this little time left before the deadline
FINISH_RESERVE_CALLS = 2          # with this many calls left, one note asks for finish now (0: off)
NO_TOOL_LIMIT = 3                 # replies in a row without a tool call before the task ends
CONTEXT_WINDOW = 262_144          # measured for Standard (probe --extra, 2026-10-10): prompt +
                                  # max_tokens up to 261,698 accepted, 262,186 rejected
CONTEXT_WRAP_FRAC = 0.70          # of the window, counting prompt + MAX_TOKENS
CONTEXT_STOP_FRAC = 0.85
# If the grader sets MADSOPT_MAX_ITERATIONS, it also bounds the calls of all attempts together.
TASK_TOTAL_MAX_CALLS = _positive_int(os.environ.get("MADSOPT_MAX_ITERATIONS"), 0) or None

# --- retries after a failed evaluation (src/solver.py; PHASE2_NOTES.md, change 1) ---------------

# After an evaluation with failing hidden tests the task continues (continue_task) with a fresh
# conversation that is handed the verdict and the previous attempt's diff. The mode names the
# model of every retry; "off" is Phase 1's single attempt. CS2680_A3_RETRY sets it for a local
# run; the default here is what a leaderboard zip runs.
RETRY_MODES = {"off": None, "standard": MODEL_STANDARD, "expert": MODEL_EXPERT}
RETRY_MODE = (os.environ.get("CS2680_A3_RETRY") or "").strip().lower()
if RETRY_MODE not in RETRY_MODES:
    RETRY_MODE = "expert"
RETRY_MODEL = RETRY_MODES[RETRY_MODE]
RETRY_MAX_ATTEMPTS = 3            # attempts per task, the first one included
# Retries per task while tasks are still being opened. A retry holds the task's slot, and a task
# never opened is a sure failure: further retries wait until every task has been opened (or
# opening has stopped).
RETRY_WHILE_OPENING = 1
# Per retry, by the retry's model: model calls, and $ as the guards count it (ledger x
# LEDGER_SAFETY). An Expert call costs about $0.01-0.03 (25x Standard's input, 36x its output), so
# its $ cap is set to let the call cap bind in most retries, the $ cap being the backstop.
# Change 12 (2026-10-16, parked): the Expert retry's cap was tried at 50 calls and 25 min in
# `12-exp`; every retry used the room, 3 of 4 still ended at a cap and each cost 1.8x ($0.45
# against $0.22-0.27), so under the run's retry stop a run would hold half as many. Back to 30.
RETRY_MAX_CALLS = {MODEL_STANDARD: 60, MODEL_EXPERT: 30}
RETRY_MAX_USD = {MODEL_STANDARD: 0.15, MODEL_EXPERT: 0.60}
RETRY_MAX_S = 1200                # seconds per retry
RETRY_MIN_LEFT_S = 1200           # a retry starts only with this long left before the run's wrap-up
# ... and only if the run's $, plus what the retries already running may still spend, plus this
# retry's cap stays below a limit: 70% of the budget while tasks are still being opened (their
# first attempts need the money), 85% once every task has been opened.
RETRY_STOP_USD = 0.70 * RUN_BUDGET_USD
RETRY_LATE_STOP_USD = STOP_OPEN_USD
RETRY_DIFF_CHARS = 12_000         # of the previous attempt's diff, shown in the handoff
RETRY_MIN_CALLS = 15              # no retry with fewer calls left of the task's total (MADSOPT_MAX_ITERATIONS)
# The grounded handoff (change 2): after a failed verdict, one Standard call in the attempt's own
# (cached) conversation writes a reflection with the verdict in hand; the handoff carries it, the
# last commands the attempt ran with their exit codes, and where its temporary test files went.
RETRY_REFLECT = True              # off: the handoff carries the attempt's finish summary instead
REFLECT_MAX_S = 120               # the reflection call must end within this (and before the wrap-up)
REFLECT_MAX_CHARS = 1500          # of the reflection, in the handoff
HANDOFF_COMMANDS = 15             # the last bash commands of the attempt listed in the handoff ...
HANDOFF_COMMAND_CHARS = 160       # ... each cut to this many characters
STASH_TEST_FILES = True           # new test files are moved to WORK_DIR/scratch/attempt<n>/, not deleted

# --- the retry policy (src/solver.py; PHASE2_NOTES.md, change 8) ---------------------------------

# "independent": after a failed verdict, the failed attempt's changes are set aside (its tracked
# changes saved as a diff, its new files moved, under WORK_DIR/scratch/attempt1/) and attempt 2
# is a fresh first attempt by MODEL, planned and guarded like attempt 1 and told only the verdict;
# the RETRY_MODEL retry with the handoff then comes as attempt 3, for near-misses (the best verdict
# so far has F <= RETRY_NEAR_MISS or F/T <= RETRY_NEAR_MISS_FRAC) and, with RETRY_EXPERT_ALL_FAILED,
# for all-failed verdicts (F = T: a patch that did not build or run). Over nine leaderboard
# submissions the same tasks flipped between solved and not; an independent second draw at each
# task's own frequency is worth about 2.5 solves per submission, against 3 of 60 anchored
# retries converted so far. "handoff": every retry is the RETRY_MODEL retry with the handoff
# (change 1).
RETRY_POLICY = "handoff"          # "independent" | "handoff"
RETRY_NEAR_MISS = 2
RETRY_NEAR_MISS_FRAC = 0.25
RETRY_EXPERT_ALL_FAILED = True

# --- the pre-finish review (src/solver.py; PHASE2_NOTES.md, change 3) --------------------------

# When a Standard attempt calls finish and the harness would accept it, one Expert call in a fresh,
# small context reads the task and the diff and lists the gaps against the Requirements and the
# Interface; gaps go back to the model as the finish result, once per attempt.
FINISH_REVIEW = "expert"          # "expert" | "off"
REVIEW_MODEL = MODEL_EXPERT
REVIEW_MIN_CALLS_LEFT = 8         # no review when fewer calls are left in the attempt ...
REVIEW_MIN_TIME_LEFT_S = 180      # ... or less time: the fix round needs room
REVIEW_MAX_S = 120                # the review call must end within this
REVIEW_MAX_TOKENS = 1200          # its answer (Expert returns no reasoning, so this bounds the output)
REVIEW_DIFF_CHARS = 20_000        # of the diff shown to the reviewer
REVIEW_SHOWN_CHARS = 3000         # of the review shown back to the model

# --- the model policy (src/solver.py; PHASE2_NOTES.md, change 4) ------------------------------

# "first-large": the first attempt starts with a planning step by PLAN_MODEL in the same
# conversation (Lecture 8 research: BAAR's First-Large heuristic, Aider's architect and editor):
# PLAN_EXPLORE_CALLS replies that explore with bash and view (edits and finish are refused), then
# the plan written as plain text, which the attempt's own model (MODEL) carries out. With
# PLAN_REPLY (change 4a) the plan has a reply of its own after the exploring ones, whose tool calls
# are not run; without it (change 4) the plan is expected within the exploring replies, and the
# step ends after them either way. "standard": one model throughout, as in Phase 1. Retries are
# never planned. PLAN_IMPLEMENT below replaces this read-only step with an implementation turn.
MODEL_POLICY = "first-large"      # "first-large" | "standard"
PLAN_MODEL = MODEL_EXPERT
PLAN_EXPLORE_CALLS = 3            # exploring replies before the plan
PLAN_REPLY = True                 # then one dedicated plan reply (change 4a); False: change 4
# Change 4c: the plan reply is sent without the tool list, so the model can only answer in text
# (with the list, Expert kept reading instead of committing: 12 of 15 plan replies, and the extra
# rounds of 4b did not help); if the server refuses the tool-call history without the list, once
# more with it. The uncached Expert call costs about $0.02-0.04 per task.
PLAN_REPLY_TOOLS = False
# Change 4b (off): a plan reply shorter than PLAN_MIN_CHARS counts as one more exploring reply
# (its reads are run) and the plan is asked for again, at most PLAN_EXTRA_ROUNDS times.
PLAN_MIN_CHARS = 400              # also the line between a brief and a remark in the ledger
PLAN_EXTRA_ROUNDS = 0
PLAN_MAX_USD = 0.15               # the planning step's $ (as the guards count it) before the switch
# Change 11b: a plan reply that comes out as tool-call markup (the model wanted to read more and
# had no tools: 60-80% of the plan replies in every local run since 4c, counted as plans until
# 2026-10-15) is not a plan. It gets one more exploring reply with the tools, then the plan is
# asked for again; a second leak ends the step without a plan, and the hand-over says so.
PLAN_LEAK_ROUNDS = 1

# --- the check written by the planning model (src/solver.py; PHASE2_NOTES.md, change 11) ---------

# With PLAN_REPLY, one more planning reply follows the plan: the check reply, in which the
# planning model may create one new test file (removed from the patch at the end, as every
# temporary test is) or a file under WORK_DIR/scratch, and run it; its tool calls are run, edits of
# existing files stay refused. The hand-over then carries the check's path, the command and its
# last result (Agentless, MASAI: the reproduction test was the biggest single gain; Lecture 6:
# demand evidence). Money: one reply, and none when the planning step's $ cap is already spent.
PLAN_CHECK = True
PLAN_CHECK_REPLIES = 2            # replies for the check: a second one when the first created no
                                  # file (exploration) or did not run it; a check needs a file
PLAN_CHECK_RESULT_CHARS = 600     # of the check's last result carried into the hand-over
# At finish, once per attempt: the finish is sent back when the check has not been run since the
# last edit (CHECK_FINISH_ROUND), or when a path the task's Interface names does not exist
# (INTERFACE_PATHS_CHECK); the second finish is accepted whatever they say.
CHECK_FINISH_ROUND = True
INTERFACE_PATHS_CHECK = True

# --- Expert implements before Standard verifies (src/solver.py; change 14) ------------------

# In first-large mode Expert may edit from its first reply. The plan reply and leak rounds
# are bypassed; the check replies follow its implementation turn, within the same $ cap.
PLAN_IMPLEMENT = True
PLAN_IMPLEMENT_CALLS = 25        # implementation replies; check replies are additional
PLAN_IMPLEMENT_USD = 0.30        # the turn and check's $ cap, as the guards count it
PLAN_IMPLEMENT_TASK_USD = 0.55   # leaves room for Standard's verification after Expert

# --- compaction (src/solver.py; PHASE2_NOTES.md, change 5) ------------------------------------

# A conversation of a model in COMPACT_MODELS whose prompt has reached COMPACT_AT_TOKENS is
# compacted (the professor's tip of 2026-10-12: compact before the context length for a small
# model's accuracy; Lecture 4 context engineering: accuracy decays with length, keep the plan
# outside the window, re-inject the task after a compaction; TRACE's template): the model writes
# notes in the old conversation, then a fresh conversation restarts from the task message, the
# plan, the notes, the files viewed, the last commands with their exit codes, the last tool
# results and the diff. At most COMPACT_MAX times per attempt; never during the planning step.
COMPACT = True
COMPACT_AT_TOKENS = 40_000
COMPACT_MAX = 2
COMPACT_MODELS = (MODEL_STANDARD,)
COMPACT_MIN_CALLS_LEFT = 10       # no compaction with fewer calls left in the attempt ...
COMPACT_MIN_TIME_LEFT_S = 300     # ... or less time: the restart needs room to pay off
COMPACT_NOTES_MAX_S = 120         # the notes call must end within this
COMPACT_NOTES_CHARS = 4000        # of the notes carried over
COMPACT_NOTES_MIN_CHARS = 200     # shorter notes are no notes: no restart, the request is retracted
# The notes call is sent without the tool list, so the model can only answer in text (with the
# tools present, Standard answered the request with tool calls); if the server refuses the
# tool-call history without the list, once more with it.
COMPACT_RESULTS_CHARS = 4000      # of the last reply's tool results carried over verbatim
COMPACT_FILES = 30                # files viewed, listed in the restart (the most recent)
COMPACT_DIFF_CHARS = 12_000       # of the diff shown in the restart

# --- stall and exploration guards (src/solver.py; PHASE2_NOTES.md, change 7) ------------------

# Deterministic guards on the attempt's own trajectory (Lewis's harness guards, Lecture 4
# research 1; MAST: step repetition), each a run-time note appended to a tool result, so the
# context stays append-only and cached. A view or bash call identical to an earlier one in the
# conversation, with the same result, is noted on its STALL_REPEAT_NOTE-th occurrence and
# replaced by "same as call N" from its STALL_REPEAT_REPLACE-th (the result is already in the
# context; the counts reset at a compaction restart, where it is not). STALL_EXPLORE_CALLS model
# calls in an attempt without an applied edit get one note (the planning step's replies do not
# count; a retry's threshold is half its call cap when that is smaller). The same bash command
# failing with the same exit code STALL_SAME_FAILURE times gets one note.
STALL_GUARDS = True
STALL_REPEAT_NOTE = 2
STALL_REPEAT_REPLACE = 3
STALL_EXPLORE_CALLS = 30
# Change 10: the exploration guard also fires when this fraction of the attempt's time cap has
# passed without an applied edit (two leaderboard tasks died at their time cap after 32-36
# turns of about 50 s without an edit, before the call trigger could fire).
STALL_EXPLORE_TIME_FRAC = 0.35
STALL_SAME_FAILURE = 3
# "Ask Expert on a stall" (the professor's tip 2; escalation as a harness rule, never the model's
# choice): when the exploration or the same-failure guard fires in a Standard attempt, once per
# attempt, one call by STALL_EXPERT_MODEL in a fresh small context (the task, the plan, the diff,
# the last commands, the last tool results, the model's last reply) says what is wrong and where
# to go; its answer joins the tool result. Skipped near the attempt's caps and past its $ cap.
STALL_ASK_EXPERT = True
STALL_EXPERT_MODEL = MODEL_EXPERT
STALL_EXPERT_MAX_USD = 0.06       # the asks of one attempt ($ as billed): none past this
STALL_EXPERT_MIN_CALLS_LEFT = 10
STALL_EXPERT_MIN_TIME_LEFT_S = 180
STALL_EXPERT_MAX_S = 120          # the ask must end within this
STALL_EXPERT_MAX_TOKENS = 700     # its answer (Expert returns no reasoning)
STALL_EXPERT_DIFF_CHARS = 12_000  # of the diff shown
STALL_EXPERT_RESULTS = 3          # the last tool results shown ...
STALL_EXPERT_RESULT_CHARS = 1500  # ... each cut to this
STALL_EXPERT_REPLY_CHARS = 1500   # of the model's last reply text shown
STALL_EXPERT_SHOWN_CHARS = 2500   # of the answer shown to the model
# Re-attempt after an early empty end (change 7, item 5): a first attempt that ends with no patch
# before its caps (three text-only replies, an API error, a sandbox that stopped answering) is
# never evaluated, so no retry follows and the task is over. With EMPTY_REATTEMPT one fresh
# attempt by MODEL follows, the plan carried over, once per task, when the API is calm again,
# the sandbox answers, and time and calls remain.
EMPTY_REATTEMPT = True
EMPTY_REATTEMPT_STOPS = ("no_tool_calls", "api_error", "sandbox_dead")
EMPTY_REATTEMPT_MIN_CALLS = 40    # of the task's total, when the grader bounds it
EMPTY_REATTEMPT_WAIT_S = 120      # at most this long waiting for the API to calm down

# --- model calls (src/llm.py) ----------------------------------------------------------------

# The probe of 2026-10-10 (PHASE1_NOTES.md, "Probe results") decided these three:
MAX_TOKENS = None                 # not sent: Standard rejects a large max_tokens with a bare
                                  # "Invalid request"; not needed so far
EXTRA_BODY = None                 # reasoning_effort="low" is accepted but changed nothing measurable
REASONING_PASSBACK = False        # the API ignores reasoning sent back (prompt tokens unchanged)
REQUEST_TIMEOUT_S = 300           # one HTTP request, also bounded by the task deadline
MIN_REQUEST_S = 30                # a request with less time than this left is not started
API_MAX_ATTEMPTS = 6
API_MAX_TIMEOUT_RETRIES = 1       # a timed-out generation is billed anyway; retry it once only
BACKOFF_BASE_S = 2.0
BACKOFF_MAX_S = 60.0              # our own backoff; a server's retry_after is honoured in full
RETRY_AFTER_MAX_S = 900.0         # sanity bound on a server-sent retry_after
WRAP_RESERVE_S = 60               # no wait may end closer than this to the task deadline
API_TROUBLE_WINDOW_S = 60         # a retryable API error this recent pauses opening new tasks
CONTEXT_RETRY_MAX_TOKENS = 4096   # after a context-length error, one retry with this max_tokens
# A timed-out request is billed but returns no usage. It is charged its prompt as uncached input
# plus this many output tokens (max_tokens when that is sent): a generous guess for a long
# generation with reasoning.
TIMEOUT_COMPLETION_ESTIMATE = 20000

# --- the reply-length bound for Standard (src/solver.py; PHASE2_NOTES.md, change 9) ---------------

# The probe of 2026-10-14: Standard accepts max_tokens up to at least 32768, and the cap counts
# the reasoning (a reply cut at the cap comes back with finish_reason "length", no content and no
# tool call). In our Standard calls of 2026-10-13/14, replies over 8k completion tokens were 2.2%
# of calls but 34% of Standard model time (154 s each; one reply ran to 183k tokens in 20 minutes),
# and two attempts were lost whole to such replies. A cut-off reply gets the existing nudge
# ("keep your thinking shorter"); after REPLY_CAP_RAISE_AFTER cut-offs in an attempt the cap is
# raised once by REPLY_CAP_RAISE_FACTOR, so a task that needs long replies is not starved. The
# planning, review, notes and stall-ask calls keep their own limits.
REPLY_CAP = True
MAX_TOKENS_STANDARD = 12288       # every request by MODEL_STANDARD in an attempt
REPLY_CAP_RAISE_AFTER = 2
REPLY_CAP_RAISE_FACTOR = 1.5

# --- the sandbox and the tools (src/tools.py, src/workspace.py) ------------------------------------

WORK_DIR = "/work"                # outside the repo, allowed by the sandbox's /read and /write
OUT_DIR = WORK_DIR + "/out"       # full bash output when what the model sees is cut
HARNESS_EXEC_TIMEOUT_S = 60       # the harness's own git commands
SANDBOX_RW_RETRIES = 2            # /read and /write are retried (whole-file, so safe); /exec never
SANDBOX_DEAD_AFTER = 3            # this many sandbox errors in a row trigger a health check

# Every bash call starts with these exports: no pagers, colours or progress bars, and git works
# whoever owns the repository. GIT_CONFIG_* is ignored by git older than 2.31.
BASH_EXPORTS = (("PAGER", "cat"), ("GIT_PAGER", "cat"), ("TQDM_DISABLE", "1"),
                ("PIP_PROGRESS_BAR", "off"), ("NO_COLOR", "1"), ("TERM", "dumb"),
                ("GIT_CONFIG_COUNT", "1"), ("GIT_CONFIG_KEY_0", "safe.directory"),
                ("GIT_CONFIG_VALUE_0", "*"))
BASH_DEFAULT_TIMEOUT_S = 120
BASH_MAX_TIMEOUT_S = 600
BASH_MIN_TIMEOUT_S = 5            # with less time than this left, the command is not run
BASH_LINE_CHARS = 1000            # longer output lines are clipped
BASH_WHOLE = (100, 10_000)        # (lines, chars) shown whole; above either, head + tail
BASH_HEAD = (40, 4_000)
BASH_TAIL = (60, 6_000)
VIEW_DEFAULT_LINES = 200          # a range without `end`
VIEW_MAX = (400, 16_000)          # (lines, chars) per view call, all ranges together
VIEW_LINE_CHARS = 2_000           # longer lines are clipped (and cannot serve as an edit anchor)
EDIT_ECHO = (5, 4_000)            # (context lines, chars) shown around each applied edit

# --- the syntax check after an edit (src/tools.py; PHASE2_NOTES.md, change 6) ------------------

# After every applied str_replace or create, one fast command chosen by the file's extension
# parses the file in the sandbox (python ast, gofmt -e, node --check, bash -n), and one line
# joins the edit's echo: "syntax check (gofmt -e): ok", or "failed" with the checker's output.
# The edit stays applied either way (Lecture 4 research: SWE-agent's lint-gated edit, 18.0%
# against 15.0% without it; Lecture 7 research: syntax errors are a top SWE-bench Pro failure).
# Extensions without a fast per-file checker, and checkers missing from the image, add no line.
SYNTAX_CHECK = True
SYNTAX_CHECK_TIMEOUT_S = 30       # a check not finished by then adds no line, and that extension
                                  # is not checked again in the attempt
SYNTAX_CHECK_CHARS = 600          # of the checker's output shown after "failed"

# --- our own logs (src/ledger.py) ---------------------------------------------------------------

# Relative to the agent's working directory, /madsOpt/.tasks/trace: a host bind mount, so the
# files are on the host at once and survive a killed container. Never inside madsOpt_logs/,
# which the leaderboard parses. run_all.py deletes .tasks/ when the NEXT run starts, so
# scripts/a3_archive.sh copies this directory out after each run.
LEDGER_DIR = os.environ.get("CS2680_A3_LEDGER_DIR", "a3_logs")
LOG_TRANSCRIPTS = True
RUN_LABEL = os.environ.get("CS2680_A3_LABEL", "")
