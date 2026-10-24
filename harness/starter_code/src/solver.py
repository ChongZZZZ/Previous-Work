"""One task, from the moment it is opened to done() (PHASE1_NOTES.md, "Guards", "End of task";
PHASE2_NOTES.md, change 1: retries).

    attempt():     ask the model; run every tool call it made; append one result per call; stop
                   when finish() is accepted or a guard trips.
    end_attempt(): clean up -> extract_patch -> evaluate (not at the run's wrap-up).
    _retry():      if the hidden tests failed and the run has the time and the money,
                   continue_task and attempt again: config.RETRY_MODEL, a fresh conversation
                   handed the verdict and the diff, the edits still in place.
    finish():      done(k, the last attempt's stop reason, all iterations).

With config.MODEL_POLICY "first-large" (PHASE2_NOTES.md, changes 4 and 4a) the first attempt
starts with a planning step: config.PLAN_MODEL answers the first PLAN_EXPLORE_CALLS replies in the
same conversation and may only read (bash, view; edits and finish are refused); with PLAN_REPLY
the next reply is the plan reply, whose text is the plan and whose tool calls are not run; a
text-only reply at any point is the plan too. Then config.MODEL continues the conversation. The
step also ends at PLAN_MAX_USD, without a plan when the replies are used up, or when the planning
model is unavailable (MODEL then finishes the step).

With PLAN_IMPLEMENT (change 14), that step is Expert's implementation turn instead: edits
are allowed, the plan reply and leak round are bypassed, and a text-only reply or refused
finish signals completion. Its own call and $ caps also hand over unfinished work. After an
edit, the check replies follow within the $ cap; MODEL then verifies in the same conversation.

With config.COMPACT (change 5) a conversation of a model in COMPACT_MODELS whose prompt reached
COMPACT_AT_TOKENS is compacted after the reply's tool results: the model writes notes in the old
conversation (one call, no tool runs), then a fresh conversation restarts from the task message,
the handoff if any, and a section with the notes, the plan, the files viewed, the last commands,
the last tool results and the diff. At most COMPACT_MAX times per attempt; never while planning.

end_attempt() and finish() run on every path out of attempt(), a crash included, and each of
their steps runs even if the one before it failed: a correct edit made before a crash is still
graded, and the task is never left without done(). The final verdict is the last grading
(run_all.py finish_task) and a retry follows only a failed one, so a retry costs time and money,
never a solve.

Guards, checked before every model call and every tool call:
  * the run's: shutdown, the global wrap-up (time or $), both read from RunState;
  * the attempt's: model calls, $, the deadline (attempt start + TASK_MAX_S, RETRY_MAX_S for a
    retry, or the global wrap-up if sooner), and the context window; the task's calls over all
    attempts if the grader sets MADSOPT_MAX_ITERATIONS. At WRAPUP_FRAC of a cap (or with
    WRAPUP_TIME_LEFT_S left) one wrap-up message is appended, once per attempt.
A guard that trips mid-reply leaves the remaining calls of that reply unrun, but each still
gets a result, so every tool call id is answered.

Every model call is one iteration (logged as api_request by src/llm.py); every tool call and
result is logged under the iteration that asked for it; done() gets the number of iterations.
"""
import hashlib
import json
import posixpath
import re
import shlex
import sys
import threading
import time
import traceback

from dispatcher import DispatcherError, DispatcherShutdown
from src import config, prompts
from src.conversation import Conversation
from src.llm import ApiError, BudgetExhausted, ContextOverflow
from src.sandbox import Sandbox, SandboxError
from src.tools import SANDBOX_CUT_MARK, TOOL_SCHEMAS, SandboxTools
from src.workspace import GIT, Workspace, looks_like_test

STOP_REASONS = ("finished", "cap_calls", "cap_usd", "cap_time", "cap_context", "global_wrapup",
                "no_tool_calls", "api_error", "sandbox_dead", "no_sandbox", "shutdown")
PLAN_REFUSED_TOOLS = ("str_replace", "create", "finish")   # during the planning step (change 4)


def view_paths(arguments):
    """The paths a view call asked for (either form of its arguments), in order."""
    value = loggable_arguments(arguments)
    if not isinstance(value, dict):
        return []
    specs = value.get("ranges") if isinstance(value.get("ranges"), list) else [value]
    paths = []
    for spec in specs:
        if isinstance(spec, dict) and isinstance(spec.get("path"), str) and spec["path"]:
            paths.append(spec["path"])
    return paths
# Any repository path the task's Interface names: cleanup never deletes a file the task asks for.
# A path with a directory anywhere, or any file name given after a "Path:" label.
_INTERFACE_PATH = re.compile(r"(?<![\w.@-])((?:\.?/)?[\w.@-]+(?:/[\w.@-]+)+\.\w+)")
_INTERFACE_LABELLED = re.compile(r"\bPath:\s*`?([\w./@-]+\.\w+)`?", re.IGNORECASE)


def interface_paths(interface, workdir):
    """The repository-relative paths an Interface text names (./x and /workdir/x normalised)."""
    root = (workdir or "").rstrip("/") + "/"
    found = set()
    for path in _INTERFACE_PATH.findall(interface or "") + _INTERFACE_LABELLED.findall(interface or ""):
        if root != "/" and path.startswith(root):
            path = path[len(root):]
        while path.startswith("./"):
            path = path[2:]
        if path and not path.startswith("/"):
            found.add(path)
    return found


def log(msg):
    print(f"[a3] {msg}", file=sys.stderr, flush=True)


def same_diff(a, b):
    """Whether two of our own diffs describe the same tree. The host's extract (`git add -N .`)
    turns new files into intent-to-add entries, after which `git diff` lists them in path order
    instead of after the tracked changes, so the sections are compared as a set. A diff the
    sandbox cut (over its output limit) is never 'the same': the change may be in the cut part."""
    if not a or not b or SANDBOX_CUT_MARK in a or SANDBOX_CUT_MARK in b:
        return False

    def sections(text):           # the output's last newline belongs to whichever section is last
        return sorted(s.rstrip("\n") for s in ("\n" + text).split("\ndiff --git "))
    return sections(a) == sections(b)


def loggable_arguments(arguments):
    """Tool arguments as logged: the parsed JSON value, or the raw text if it is not JSON."""
    if not isinstance(arguments, str):
        return arguments
    try:
        return json.loads(arguments)
    except ValueError:
        return arguments


class RunState:
    """What the scheduler and every task share. Times are clock() values."""

    def __init__(self, ledger, clock=time.monotonic):
        self.ledger = ledger
        self.clock = clock
        self.cond = threading.Condition()
        self.t0 = None                 # when the first task was opened (the host's run clock)
        self.shutdown = False
        self.opening_over = False      # every task has been opened, or opening has stopped
        self.reserved = {}             # task -> (cap, guard $ at its start): retries running now

    def start_clock(self, t):
        if self.t0 is None:
            self.t0 = t

    def wrap_at(self):
        return None if self.t0 is None else self.t0 + config.RUN_LIMIT_S * config.WRAP_FRAC

    def stop_open_at(self):
        return None if self.t0 is None else self.t0 + config.RUN_LIMIT_S * config.STOP_OPEN_FRAC

    def global_wrap(self):
        """Why every task must wrap up now, or None."""
        if self.shutdown:
            return "shutdown"
        wrap_at = self.wrap_at()
        if wrap_at is not None and self.clock() >= wrap_at:
            return "global_wrapup"
        if self.ledger.guard_usd() >= config.WRAP_USD:
            return "global_wrapup"
        return None

    def stop_opening(self):
        at = self.stop_open_at()
        return (self.shutdown or (at is not None and self.clock() >= at)
                or self.ledger.guard_usd() >= config.STOP_OPEN_USD)

    def set_shutdown(self):
        with self.cond:
            self.shutdown = True
            self.cond.notify_all()

    def reserve_retry(self, k, cap, limit):
        """Reserve a retry's $ cap if the run's guard $, plus what the retries already running
        may still spend, plus the cap stays within limit. Check and reservation are one step, so
        tasks that end at the same moment cannot all pass on the same total."""
        with self.cond:
            committed = sum(max(0.0, cap_ - (self.ledger.guard_task_usd(key) - usd0))
                            for key, (cap_, usd0) in self.reserved.items() if key != k)
            if self.ledger.guard_usd() + committed + cap > limit:
                return False
            self.reserved[k] = (cap, self.ledger.guard_task_usd(k))
            return True

    def release_retry(self, k):
        with self.cond:
            self.reserved.pop(k, None)


class Solver:
    _sleep = staticmethod(time.sleep)      # change 7: the wait for a calm API (tests stub it)

    def __init__(self, task, dispatcher, llm, ledger, state, clock=time.monotonic):
        self.task = task
        self.k = task["task"]
        self.dispatcher = dispatcher
        self.llm = llm
        self.ledger = ledger
        self.state = state
        self.clock = clock
        self.logger = dispatcher.logger(self.k)
        self.started = clock()
        self.iterations = 0
        self.stop_reason = None
        self.summary = ""
        self.wrapped_up = False
        self.no_tool_streak = 0
        self.nudges = 0
        self.finish_rounds = 0
        self.max_prompt = 0
        self.last_cached = None
        self.sb = self.workspace = self.tools = self.convo = None
        self.times = {"tool_s": 0.0, "model_s": 0.0, "backoff_s": 0.0}
        self.end = {}                  # the current attempt's facts (task_end: the last one's)
        self.attempts = []             # one summary per attempt
        self.eval_wait_s = 0.0
        self.graded_diff = None        # our own diff of the tree the last grading saw
        self.reattempted = False       # change 7: one fresh attempt after an early empty end
        self.carried_plan = ""         # the first attempt's plan, for that fresh attempt
        self._begin(1)

    def _begin(self, n, handoff="", reattempt=False, fresh=False):
        """Start attempt n: its model, its own caps and clock, a clean set of per-attempt state.
        reattempt (change 7): a fresh attempt by MODEL with the first attempt's caps, after an
        early empty end. fresh (change 8): the independent second attempt, planned like attempt 1."""
        self.attempt_n = n
        self.reattempt = reattempt
        self.fresh = fresh
        self.planning = (n == 1 or fresh) and config.MODEL_POLICY == "first-large"
        if self.planning:
            self.model = config.PLAN_MODEL
        else:
            self.model = config.MODEL if n == 1 or reattempt or fresh else config.RETRY_MODEL
        # The planning step's facts (change 4): replies made, refused edits, its $ baseline.
        self.plan = ({"calls": 0, "refused": 0, "last_chars": 0, "model": self.model,
                      "plan_reply": False, "not_run": 0, "rounds": 0,
                      "check_reply": False, "check_files": [], "check_command": None,
                      "check_result": "", "check_exit": None, "pending_plan": None,
                      "leaks": 0, "leak_rounds": 0, "edits": 0,
                      "implement": config.PLAN_IMPLEMENT, "implemented": None,
                      "usd0": self.ledger.guard_task_usd(self.k)} if self.planning else None)
        self.attempt_started = self.clock()
        self.attempt_calls0 = self.iterations
        self.attempt_usd0 = self.ledger.guard_task_usd(self.k)
        self.attempt_raw_usd0 = self.ledger.task_usd(self.k)
        self.handoff = handoff
        self.stop_reason = None
        self.summary = ""
        self.wrapped_up = False
        self.finish_noted = False
        self.no_tool_streak = 0
        self.commands = []             # (command, exit, elapsed, timed out, timeout) of this attempt's bash calls
        self.reviewed = False          # the pre-finish review happens once per attempt
        self.last_cached = None        # a new conversation (or model) starts its cache afresh
        self.compactions = 0           # change 5: attempts at compaction in this attempt ...
        self.restarts = 0              # ... and the conversations actually restarted
        self.viewed = []               # paths viewed in this attempt, oldest first
        self.viewed_at_compaction = set()
        self.re_reads = 0              # views after a compaction of a path viewed before it
        # Change 7: the stall guards' state (reset with the attempt; `seen` also at a restart)
        self.seen = {}                 # (tool, arguments) -> [first call, result digest, count]
        self.failures = {}             # (command, exit) -> times it failed that way
        self.edits = 0                 # edits applied in this attempt
        self.explore_noted = False
        self.stall_asked = False
        self.pending_stall = None      # a guard that fired in this reply, for the Expert ask
        self.stall = {"repeats": 0, "replaced": 0, "explore": 0, "same_failure": 0,
                      "asks": 0, "ask_usd": 0.0}
        self.cut_offs = 0              # change 9: replies cut at the reply-length cap in this attempt
        # Change 11: whether the planning model's check has run since the last edit, the
        # runs, and the finish round (once per attempt); the check itself is kept across the
        # attempts (its file stays in the tree) and dropped with a fresh attempt's set-aside.
        self.check_ran = True
        self.check_runs = 0
        self.finish_gated = False
        if fresh or n == 1:
            self.check = None
        self.end = {}

    # -- the attempt's limits ------------------------------------------------------------

    def caps(self):
        """(model calls, $, seconds) of the current attempt; the calls also bounded by what is left
        of the task's total if the grader sets one."""
        if self.attempt_n == 1 or self.reattempt or self.fresh:
            calls, usd, secs = config.TASK_MAX_CALLS, config.TASK_MAX_USD, config.TASK_MAX_S
            if self.plan is not None and config.PLAN_IMPLEMENT:
                usd = config.PLAN_IMPLEMENT_TASK_USD
        else:
            calls, usd, secs = self._retry_calls(), self._retry_usd(), config.RETRY_MAX_S
        if config.TASK_TOTAL_MAX_CALLS:
            calls = min(calls, config.TASK_TOTAL_MAX_CALLS - self.attempt_calls0)
        return calls, usd, secs

    @staticmethod
    def _retry_usd():
        return config.RETRY_MAX_USD.get(config.RETRY_MODEL, min(config.RETRY_MAX_USD.values()))

    @staticmethod
    def _retry_calls():
        return config.RETRY_MAX_CALLS.get(config.RETRY_MODEL, min(config.RETRY_MAX_CALLS.values()))

    def _stash_dir(self):
        return f"{config.WORK_DIR}/scratch/attempt{self.attempt_n}"

    def deadline(self):
        deadline = self.attempt_started + self.caps()[2]
        wrap_at = self.state.wrap_at()
        return deadline if wrap_at is None else min(deadline, wrap_at)

    def _time_up(self):
        """The stop reason when the deadline is near: the run's wrap-up if that is the binding
        deadline, else the attempt's own time cap."""
        wrap_at = self.state.wrap_at()
        binding_is_run = wrap_at is not None and wrap_at <= self.attempt_started + self.caps()[2]
        return "global_wrapup" if binding_is_run else "cap_time"

    def guard(self):
        """The reason the task must stop now, or None. Appends the wrap-up message once."""
        reason = self.state.global_wrap()
        if reason:
            return reason
        left = self.deadline() - self.clock()
        max_calls, max_usd, _ = self.caps()
        calls = self.iterations - self.attempt_calls0
        if calls >= max_calls or (config.TASK_TOTAL_MAX_CALLS
                                  and self.iterations >= config.TASK_TOTAL_MAX_CALLS):
            return "cap_calls"
        usd = self.ledger.guard_task_usd(self.k) - self.attempt_usd0
        if usd >= max_usd:
            return "cap_usd"
        if left < config.WRAP_RESERVE_S + config.MIN_REQUEST_S:
            return self._time_up()
        context = (self.convo.last_prompt_tokens or 0) + (config.MAX_TOKENS or 0)
        if context >= config.CONTEXT_STOP_FRAC * config.CONTEXT_WINDOW:
            return "cap_context"
        if not self.wrapped_up:
            why = None
            if calls >= config.WRAPUP_FRAC * max_calls:
                why = f"you have used {calls} of {max_calls} model calls ({max_calls - calls} left)"
            elif usd >= config.WRAPUP_FRAC * max_usd:
                what = "task" if self.attempt_n == 1 else "attempt"
                why = f"this {what} has cost ${usd:.2f} of its ${max_usd:.2f}"
            elif left < config.WRAPUP_TIME_LEFT_S:
                why = f"about {max(1, int(left // 60))} minutes are left for this task"
            elif context >= config.CONTEXT_WRAP_FRAC * config.CONTEXT_WINDOW:
                why = "the conversation is close to the model's context limit"
            if why:
                self.wrapped_up = True
                channel = self.convo.add_note(prompts.wrap_up(why))
                self.ledger.write("event", k=self.k, iter=self.iterations, what="wrapup", why=why,
                                  channel=channel)
        # With the last FINISH_RESERVE_CALLS calls left, one note asks for finish now, so that the
        # finish review runs and the calls are not spent exploring past the cap.
        if (config.FINISH_RESERVE_CALLS and not self.finish_noted and calls > 0
                and calls >= max_calls - config.FINISH_RESERVE_CALLS):
            self.finish_noted = True
            what = "task" if self.attempt_n == 1 else "attempt"
            channel = self.convo.add_note(prompts.finish_now(max_calls - calls, what))
            self.ledger.write("event", k=self.k, iter=self.iterations, what="finish_now",
                              left=max_calls - calls, channel=channel)
        return None

    # -- the whole task --------------------------------------------------------------------

    def run(self):
        """Never raises; always ends with done() (or run_end written here on shutdown)."""
        self.ledger.write("task_start", k=self.k, workdir=self.task.get("workdir"),
                          sandbox=bool(self.task.get("sandbox_url")),
                          deadline_s=round(self.deadline() - self.clock(), 1))
        try:
            self.sb = Sandbox(self.task.get("sandbox_url") or "", self.task.get("workdir") or "/app")
        except SandboxError as exc:
            self.stop_reason = "no_sandbox"
            self.end["error"] = str(exc)
        while True:
            if self.sb is not None:
                try:
                    self.attempt()
                except DispatcherShutdown:
                    self.state.set_shutdown()
                    self.stop_reason = "shutdown"
                except Exception as exc:  # a bug must not lose the task's patch
                    self.stop_reason = f"error:{type(exc).__name__}"
                    self.end["traceback"] = traceback.format_exc()[-4000:]
                    log(f"task {self.k}: {type(exc).__name__}: {exc}")
            try:
                self.end_attempt()
            except Exception as exc:  # a bug here must not skip done()
                self.end["end_attempt_error"] = f"{type(exc).__name__}: {exc}"[:300]
                self.end["traceback"] = traceback.format_exc()[-4000:]
                log(f"task {self.k}: end_attempt {type(exc).__name__}: {exc}")
                break
            try:
                if not self._retry() and not self._reattempt():
                    break
            except Exception as exc:  # never let a retry bug skip done()
                self.end["retry_error"] = f"{type(exc).__name__}: {exc}"[:300]
                break
        self.finish()
        return self.stop_reason

    def attempt(self):
        if self.workspace is None:
            # Once per task: every attempt's cleanup compares with the repository as opened.
            self.workspace = Workspace(self.sb)
            try:
                self.end["snapshot_exit"] = self.workspace.snapshot()
            except SandboxError as exc:
                self.end["snapshot_error"] = str(exc)[:300]
        # The earlier attempts' edits are still in the tree: the finish review must not report
        # them as changed by a command, nor ask again about files already confirmed.
        edited = set(self.tools.edited) if self.tools is not None else set()
        confirmed = set(self.tools._confirmed) if self.tools is not None else set()
        out_n = self.tools._out_n if self.tools is not None else 0   # saved logs keep numbering
        self.tools = SandboxTools(self.sb, self.workspace, deadline=self.deadline(),
                                  clock=self.clock)
        self.tools.edited |= edited
        self.tools._confirmed |= confirmed
        self.tools._out_n = out_n
        self.tools.interface_paths = interface_paths(self.task.get("interface"), self.task.get("workdir"))
        opening = prompts.task_message(self.task)
        if self.planning:
            opening += (prompts.plan_step_implement(config.PLAN_IMPLEMENT_CALLS)
                        if config.PLAN_IMPLEMENT else
                        prompts.plan_step(config.PLAN_EXPLORE_CALLS, config.PLAN_REPLY))
        self.convo = Conversation(prompts.SYSTEM_PROMPT, opening + self.handoff,
                                  ledger=self.ledger, k=self.k,
                                  kind="" if self.attempt_n == 1 else f"a{self.attempt_n}")
        while self.stop_reason is None:
            self.stop_reason = self.guard() or self.step()

    def step(self):
        """One model call and its tool calls. Returns a stop reason, or None to go on."""
        iteration = self.iterations + 1
        self.tools.deadline = self.deadline()
        self.convo.flush()                             # what is sent is now in the transcript
        # Change 4c: the plan reply goes without the tool list, so it can only be text; after a
        # refusal (some servers want the list with a tool-call history) once more with it.
        plan_reply = bool(self.planning and self.plan["plan_reply"]
                          and not self.plan.get("check_reply"))     # change 11: the check reply has tools
        without_tools = (plan_reply and not config.PLAN_REPLY_TOOLS
                         and "tools_retry" not in self.plan)
        try:
            cap = self._reply_cap()
            c = self.llm.complete(
                k=self.k, iteration=iteration, logger=self.logger, model=self.model,
                messages=self.convo.messages, tools=None if without_tools else TOOL_SCHEMAS,
                deadline=self.deadline(), max_tokens=cap,
                prompt_estimate=self.convo.estimated_tokens())
        except ContextOverflow as exc:
            self.end["error"] = str(exc)[:500]
            return "cap_context"
        except BudgetExhausted as exc:
            self.end["error"] = str(exc)[:500]
            return self.state.global_wrap() or self._time_up()
        except ApiError as exc:
            if without_tools:
                self.plan["tools_retry"] = str(exc)[:300]
                self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_tools_retry",
                                  error=str(exc)[:300])
                return None
            if self.planning and self.model == config.PLAN_MODEL and "fallback" not in self.plan:
                # The planning model is unavailable: the attempt's own model finishes the
                # planning step instead of the task losing its attempt.
                self.plan["fallback"] = str(exc)[:300]
                self.plan["model"] = self.model = config.MODEL
                self.last_cached = None
                self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_fallback",
                                  error=str(exc)[:300])
                log(f"task {self.k}: planning model unavailable ({str(exc)[:80]}); "
                    f"{config.MODEL} finishes the planning step")
                return None
            self.end["error"] = str(exc)[:500]
            return "api_error"
        self.iterations = iteration
        if self.planning:
            self.plan["calls"] += 1
            if plan_reply:
                self.plan["reply_tools"] = not without_tools
        cached = c.row.get("cached") or 0
        if self.last_cached is not None and cached < self.last_cached - 1024:
            # The cache went backwards: a prefix the API had cached was not reused (a server-side
            # re-render, or a change before the end of the list). A cached count that merely lags
            # behind a growing prompt is not a drop.
            self.ledger.write("event", k=self.k, iter=iteration, what="cache_drop",
                              previous_cached=self.last_cached, cached=cached,
                              prompt=c.row.get("prompt"))
        self.last_cached = cached
        self.times["model_s"] += c.model_s
        self.times["backoff_s"] += c.backoff_s
        self.convo.record_prompt_tokens(c.row.get("prompt"))
        self.max_prompt = max(self.max_prompt, c.row.get("prompt") or 0)
        message = c.message
        content = (getattr(message, "content", None) or "") if message is not None else ""
        calls = list(getattr(message, "tool_calls", None) or []) if message is not None else []
        reasoning = getattr(message, "reasoning_content", None) if message is not None else None
        if reasoning:
            self.ledger.transcript(self.k, {"iter": self.iterations, "reasoning": reasoning},
                                   kind="reasoning")

        parsed = []
        for i, call in enumerate(calls):
            function = getattr(call, "function", None)
            name = (getattr(function, "name", None) or "(missing name)") if function else \
                f"({getattr(call, 'type', 'unknown')} call)"
            arguments = getattr(function, "arguments", None) if function else None
            parsed.append((getattr(call, "id", None) or f"call_{self.iterations}_{i}", name,
                           arguments))

        if self.planning:
            self.plan["last_chars"] = len(content)
            check_reply = bool(self.plan.get("check_reply"))   # change 11: after the plan reply
            leaked = (self.plan["plan_reply"] and not check_reply and not calls
                      and prompts.looks_like_tool_markup(content))
            if leaked and self.plan["leak_rounds"] < config.PLAN_LEAK_ROUNDS:
                # Change 11b: the plan reply came out as tool-call markup (the model wanted to read
                # more and had no tools). Not a plan: one more exploring reply with the tools, then
                # the plan is asked for again.
                self.plan["leaks"] += 1
                self.plan["leak_rounds"] += 1
                self.plan["rounds"] += 1
                self.plan["plan_reply"] = False
                self.plan["after_leak"] = True
                self.convo.add_assistant(content, reasoning=reasoning)
                channel = self.convo.add_note(prompts.PLAN_LEAK_NOTE)
                self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_leak",
                                  channel=channel, chars=len(content), round=self.plan["leak_rounds"])
                self.no_tool_streak = 0
                return None
            if self.plan["plan_reply"] and not check_reply and not leaked \
                    and len(content.strip()) < config.PLAN_MIN_CHARS \
                    and self.plan["rounds"] < config.PLAN_EXTRA_ROUNDS:
                # Change 4b: not a plan. It counts as one more exploring reply (its reads run
                # below, edits refused as before) and the plan is asked for again.
                self.plan["rounds"] += 1
                self.plan["plan_reply"] = False
                self.plan["again_chars"] = len(content.strip())
                if not calls:
                    self.convo.add_assistant(content or "(empty reply)", reasoning=reasoning)
                    self.plan["plan_reply"] = True
                    channel = self.convo.add_note(prompts.plan_again(len(content.strip())))
                    self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_now",
                                      channel=channel, again=len(content.strip()),
                                      round=self.plan["rounds"])
                    self.no_tool_streak = 0
                    return None
            elif self.plan["plan_reply"] and not check_reply:
                # Change 4a: the plan reply. Its text is the plan; its tool calls are not run,
                # but each still gets a result, so every call id is answered.
                self.convo.add_assistant(content or "(empty reply)", parsed, reasoning=reasoning)
                self.convo.flush()
                for call_id, name, arguments in parsed:
                    self.logger.tool_call(self.iterations, name, loggable_arguments(arguments))
                    self.logger.tool_result(self.iterations, name, prompts.PLAN_REPLY_NOT_RUN, True)
                    self.ledger.write("tool", k=self.k, iter=self.iterations, name=name,
                                      is_error=True, not_run="plan_reply", refused_plan=True,
                                      secs=0.0, shown_chars=len(prompts.PLAN_REPLY_NOT_RUN))
                    self.convo.add_tool_result(call_id, prompts.PLAN_REPLY_NOT_RUN)
                self.plan["not_run"] += len(parsed)
                self.no_tool_streak = 0
                if leaked:
                    self.plan["leaks"] += 1                    # 11b: a second leak; no plan
                self._plan_taken(content, c.finish_reason == "length",
                                 is_plan=bool(content.strip()) and not leaked, leaked=leaked)
                return None
            if check_reply and not calls:
                # Change 11: the check reply wrote nothing; the plan stands, without a check.
                self.convo.add_assistant(content or "(empty reply)", reasoning=reasoning)
                self.no_tool_streak = 0
                self.plan["check_rounds"] += 1
                self._end_check_reply()
                return None
            if not calls and content.strip():
                # The plan: a text-only reply during the planning step (cut off or not). It is
                # not nudged; the attempt's own model takes over from here.
                self.convo.add_assistant(content, reasoning=reasoning)
                self.no_tool_streak = 0
                if config.PLAN_IMPLEMENT:
                    self._implement_done("implemented")
                else:
                    self._plan_taken(content, c.finish_reason == "length", is_plan=True)
                return None
        if c.finish_reason == "length" or not calls:
            # A reply cut off at the output limit may carry half a tool call: never run or
            # store it. Either way the model is told to continue with a tool call.
            placeholder = "(reply cut off)" if c.finish_reason == "length" else "(empty reply)"
            self.convo.add_assistant(content or placeholder, reasoning=reasoning)
            if self.planning and config.PLAN_IMPLEMENT and not self.plan.get("check_reply"):
                if self.ledger.guard_task_usd(self.k) - self.plan["usd0"] >= self._plan_usd_cap():
                    self._implement_done("usd")
                    return None
                if self.plan["calls"] >= config.PLAN_IMPLEMENT_CALLS:
                    self._implement_done("calls")
                    return None
            self.no_tool_streak += 1
            if c.finish_reason == "length" and cap:
                self.cut_offs += 1                     # change 9: cut at the reply-length cap
            if self.no_tool_streak >= config.NO_TOOL_LIMIT:
                return "no_tool_calls"
            self.nudges += 1
            self.convo.add_user(prompts.NUDGE_CUT_OFF if c.finish_reason == "length"
                                else prompts.NUDGE)
            self.ledger.write("event", k=self.k, iter=self.iterations,
                              what=f"nudge_{c.finish_reason or 'no_tool'}",
                              finish_reason=c.finish_reason, content_chars=len(content),
                              cap=cap, cut_offs=self.cut_offs,
                              completion=c.row.get("completion"),
                              tool_markup_in_reasoning=bool(reasoning and re.search(
                                  r"<tool_call|</?function|</parameter>", reasoning)))
            return None
        self.no_tool_streak = 0

        self.convo.add_assistant(content, parsed, reasoning=reasoning)
        self.convo.flush()                             # on disk before any of its tools runs

        results, stop, finished = {}, None, False
        # finish runs after the other calls of the reply, so its review sees their effect.
        for i in sorted(range(len(parsed)), key=lambda i: parsed[i][1] == "finish"):
            _, name, arguments = parsed[i]
            self.logger.tool_call(self.iterations, name, loggable_arguments(arguments))
            if stop is None:
                stop = self.state.global_wrap() or self._out_of_time()
            if stop is not None:
                text, is_error, meta = prompts.NOT_RUN, True, {"not_run": stop}
            elif self.planning and (refusal := self._plan_refusal(name, arguments)) is not None:
                text, is_error = refusal, True
                meta = {"error_kind": "refusal", "refused_plan": True}
                self.plan["refused"] += 1
            else:
                self.tools.deadline = self.deadline()
                r = self.tools.execute(name, arguments)
                text, is_error, meta = r.text, r.is_error, r.meta
                self.times["tool_s"] += meta.get("secs", 0.0)
                if name in ("str_replace", "create") and not is_error:
                    self.edits += 1
                    if self.planning and not self.plan.get("check_reply"):
                        self.plan["edits"] += 1
                    if self.check is not None:
                        self.check_ran = False             # change 11: the check must run again
                if self.planning and self.plan.get("check_reply"):
                    # Change 11: the check reply's facts, for the hand-over
                    if name == "create" and not is_error:
                        self.plan["check_files"].append(self._path_of(arguments))
                    elif name == "bash" and "exit" in meta:
                        command = self._command_of(arguments)
                        if self._names_a_file(command, self.plan["check_files"]):
                            self.plan["check_command"] = command
                            self.plan["check_result"] = text
                            self.plan["check_exit"] = meta.get("exit")
                elif self.check is not None and name == "bash" and "exit" in meta:
                    command = self._command_of(arguments)
                    if self._runs_the_check(command):
                        self.check_ran = True
                        self.check_runs += 1
                        self.check["last_exit"] = meta.get("exit")
                if config.STALL_GUARDS and not self.planning:
                    text, meta = self._guard_result(name, arguments, text, is_error, meta)
                if name == "view" and not is_error:
                    for path in view_paths(arguments):
                        if path in self.viewed_at_compaction:
                            self.re_reads += 1
                            self.viewed_at_compaction.discard(path)
                        if path in self.viewed:
                            self.viewed.remove(path)
                        self.viewed.append(path)
                if name == "bash" and ("exit" in meta or meta.get("timed_out")):
                    value = loggable_arguments(arguments)
                    command = str(value.get("command", "")) if isinstance(value, dict) else ""
                    self.commands.append((command, meta.get("exit"), meta.get("elapsed"),
                                          bool(meta.get("timed_out")), meta.get("timeout")))
                    del self.commands[:-config.HANDOFF_COMMANDS]
                if r.stop:
                    stop = r.stop
                if r.finished:
                    self.summary = self._summary_of(arguments)
                    gate = self._finish_gate()                 # change 11, once per attempt
                    gaps = gate or self._review_before_finish()
                    if gaps:
                        text, is_error, meta = gaps, False, dict(meta, review_gaps=gate is None,
                                                                 finish_gate=gate is not None)
                    else:
                        finished = True
                if name == "finish":
                    self.finish_rounds += 1
            self.logger.tool_result(self.iterations, name, text, is_error)
            self.ledger.write("tool", k=self.k, iter=self.iterations, name=name,
                              is_error=is_error, **meta)
            results[i] = text
        for i, (call_id, _, _) in enumerate(parsed):
            self.convo.add_tool_result(call_id, results[i])
        if finished:
            return "finished"
        if config.STALL_GUARDS and not self.planning and stop is None:
            self._stall_after_reply()
        if self.planning and stop is None:
            if self.plan.get("check_reply"):
                # Change 11: the check reply's tools have run. A check is a created file and a
                # run of it; while either is missing, one more reply (with the note saying which),
                # unless the replies or the planning step's $ cap are spent.
                self.plan["check_rounds"] += 1
                spent = self.ledger.guard_task_usd(self.k) - self.plan["usd0"] >= self._plan_usd_cap()
                created = bool(self.plan["check_files"])
                complete = created and self.plan["check_command"] is not None
                if complete or spent or self.plan["check_rounds"] >= config.PLAN_CHECK_REPLIES:
                    self._end_check_reply()
                else:
                    note = prompts.plan_check_again(created, f"{config.WORK_DIR}/scratch")
                    channel = self.convo.add_note(note)
                    self.ledger.write("event", k=self.k, iter=self.iterations,
                                      what="plan_check_again", channel=channel, created=created)
            elif config.PLAN_IMPLEMENT:
                if self.plan.get("finish_signal"):
                    self._implement_done("implemented")
                elif self.ledger.guard_task_usd(self.k) - self.plan["usd0"] >= self._plan_usd_cap():
                    self._implement_done("usd")
                elif self.plan["calls"] >= config.PLAN_IMPLEMENT_CALLS:
                    self._implement_done("calls")
            elif self.ledger.guard_task_usd(self.k) - self.plan["usd0"] >= config.PLAN_MAX_USD:
                self._end_planning("usd")
            elif self.plan["calls"] >= config.PLAN_EXPLORE_CALLS:
                if config.PLAN_REPLY and not self.plan["plan_reply"]:
                    # Change 4a: the exploring replies are used; the next reply is the plan
                    # (4b: asked again after a reply that was not a plan).
                    self.plan["plan_reply"] = True
                    again = self.plan.pop("again_chars", None)
                    after_leak = self.plan.pop("after_leak", False)       # change 11b
                    note = (prompts.PLAN_AFTER_LEAK if after_leak
                            else prompts.PLAN_NOW if again is None else prompts.plan_again(again))
                    channel = self.convo.add_note(note)
                    self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_now",
                                      channel=channel, again=again, round=self.plan["rounds"],
                                      after_leak=after_leak)
                else:
                    self._end_planning("calls")
        if stop is None and self._should_compact():
            self._compact()
        return stop

    def _reply_cap(self):
        """Change 9: the reply-length bound for the attempt's Standard calls (max_tokens), raised
        once after REPLY_CAP_RAISE_AFTER cut-offs; None for other models or when off."""
        if not config.REPLY_CAP or self.model != config.MODEL_STANDARD:
            return None
        cap = config.MAX_TOKENS_STANDARD
        if self.cut_offs >= config.REPLY_CAP_RAISE_AFTER:
            cap = int(cap * config.REPLY_CAP_RAISE_FACTOR)
        return cap

    def _out_of_time(self):
        return self._time_up() if self.deadline() - self.clock() < config.WRAP_RESERVE_S else None

    @staticmethod
    def _summary_of(arguments):
        value = loggable_arguments(arguments)
        return str(value.get("summary", ""))[:500] if isinstance(value, dict) else ""

    def _end_planning(self, why, chars=0, cut=False, note=True, text="", check=None):
        """Change 4: the planning step is over and config.MODEL continues the same conversation.
        why: "plan" (a text plan was written), "calls", "usd", or "stop:<reason>" when the attempt
        ended first. After a plan the hand-over is a user message (the plan is the last message);
        otherwise the note joins the last unsent tool result, so the request stays a prefix."""
        self.planning = False
        self.model = config.MODEL
        self.last_cached = None                    # the new model starts its cache afresh
        usd = round(self.ledger.guard_task_usd(self.k) - self.plan["usd0"], 5)
        channel = None
        if config.PLAN_IMPLEMENT:
            if why in ("calls", "usd") and not self.plan["edits"]:
                why = "none"
            text = prompts.implement_record(why)
            if check:
                text += prompts.plan_check_section(check["path"], check["command"],
                                                  self.plan["check_result"])
            if note:
                channel = self.convo.add_note(prompts.implement_handover(
                    why, check, self.plan["check_result"]))
        elif note and why == "plan" and check:
            channel = self.convo.add_note(prompts.plan_handover_check(
                check["path"], check["command"], self.plan["check_result"]))
        elif note and why == "plan":
            channel = self.convo.add_note(prompts.PLAN_HANDOVER)
        elif note and check:
            channel = self.convo.add_note(prompts.plan_over_check(
                why, config.PLAN_EXPLORE_CALLS, check["path"], check["command"], self.plan["check_result"]))
        elif note:
            channel = self.convo.add_note(prompts.plan_over(why, config.PLAN_EXPLORE_CALLS))
        self.plan.update(why=why, usd=usd, chars=chars, cut=cut, text=text)
        self.ledger.write("event", k=self.k, iter=self.iterations, what="plan", why=why,
                          calls=self.plan["calls"], usd=usd, chars=chars, cut=cut,
                          brief=chars >= config.PLAN_MIN_CHARS, rounds=self.plan["rounds"],
                          reply_tools=self.plan.get("reply_tools"),
                          tools_retry=self.plan.get("tools_retry"),
                          last_chars=self.plan["last_chars"], refused=self.plan["refused"],
                          plan_reply=self.plan["plan_reply"], not_run=self.plan["not_run"],
                          check=bool(check), check_files=len(self.plan["check_files"]),
                          check_rounds=self.plan.get("check_rounds"), leaks=self.plan["leaks"],
                          implement=self.plan["implement"], implemented=self.plan["implemented"],
                          edits=self.plan["edits"],
                          check_command=(self.plan["check_command"] or "")[:160] or None,
                          check_exit=self.plan["check_exit"], check_skipped=self.plan.get("check_skipped"),
                          model=self.plan["model"], fallback=self.plan.get("fallback"),
                          channel=channel)
        log(f"task {self.k}: planning step over ({why}) after {self.plan['calls']} calls, "
            f"${usd:.4f}; {config.MODEL} continues")

    # -- compaction (change 5) ---------------------------------------------------------------

    def _should_compact(self):
        if not config.COMPACT or self.planning or self.convo is None:
            return False
        if self.model not in config.COMPACT_MODELS or self.compactions >= config.COMPACT_MAX:
            return False
        if (self.convo.last_prompt_tokens or 0) < config.COMPACT_AT_TOKENS:
            return False
        max_calls, _, _ = self.caps()
        if max_calls - (self.iterations - self.attempt_calls0) < config.COMPACT_MIN_CALLS_LEFT:
            return False
        if self.deadline() - self.clock() < config.COMPACT_MIN_TIME_LEFT_S:
            return False
        return not self.state.global_wrap()

    def _compact(self):
        """Notes-and-restart compaction: the model writes notes in the old conversation; a fresh
        conversation then restarts from the task message (and the handoff), the notes, the plan,
        the files viewed, the last commands, the last reply's tool results and the diff (the
        professor's tip; Lecture 4 context engineering; TRACE's template). Without notes (the
        call failed) the old conversation goes on; the attempt at compaction still counts."""
        self.compactions += 1
        n = self.compactions
        at_iter, prompt_tokens = self.iterations, self.convo.last_prompt_tokens
        results = []
        for m in reversed(self.convo.messages):
            if m.get("role") != "tool":
                break
            results.append(m.get("content") or "")
        results.reverse()
        results_text = "\n\n".join(results)
        notes, facts = self._compact_notes()
        event = dict(k=self.k, iter=self.iterations, what="compaction", n=n, at_iter=at_iter,
                     prompt_tokens=prompt_tokens, notes_chars=len(notes), **facts)
        if not notes:
            self.ledger.write("event", restarted=False, **event)
            log(f"task {self.k}: compaction {n} skipped, no notes ({facts.get('notes_error', '?')[:80]})")
            return
        diff = ""
        try:
            diff = self._own_patch()
        except Exception as exc:
            facts["diff_error"] = f"{type(exc).__name__}: {exc}"[:300]
        plan_text = (self.plan or {}).get("text") or ""
        restart = (prompts.task_message(self.task) + self.handoff
                   + prompts.compact_message(notes, plan_text, self.viewed[-config.COMPACT_FILES:],
                                             self.commands, results_text, diff, config.OUT_DIR,
                                             f"{config.WORK_DIR}/scratch"))
        old_kind = self._kind()
        self.restarts += 1
        self.convo.flush()
        self.ledger.transcript(self.k, {"compacted": self.restarts, "iter": self.iterations},
                               kind=old_kind)
        self.convo = Conversation(prompts.SYSTEM_PROMPT, restart, ledger=self.ledger, k=self.k,
                                  kind=self._kind())
        self.last_cached = None                    # a new conversation: not a cache drop
        self.wrapped_up = self.finish_noted = False   # the guard re-sends them when still due
        self.viewed_at_compaction = set(self.viewed)
        self.seen = {}                             # change 7: the earlier results are gone
        self.ledger.write("event", restarted=True, restart=self.restarts, files=len(self.viewed),
                          commands=len(self.commands), results_chars=len(results_text),
                          diff_chars=len(diff), restart_chars=len(restart),
                          diff_error=facts.get("diff_error"), **event)
        log(f"task {self.k}: compaction {n} at call {at_iter} ({prompt_tokens} prompt tokens): "
            f"{len(notes)} chars of notes, {len(self.viewed)} files, diff {len(diff)} chars")

    def _compact_notes(self):
        """One call in the old conversation for the notes, sent without the tool list so the
        model can only answer in text (with the list, Standard answered with tool calls: 5-exp,
        2026-10-13); if the server refuses the tool-call history without the list, once more
        with it. On failure, short notes or tool-call markup, the request
        (and the reply) is retracted so the old conversation goes on unchanged."""
        usd0 = self.ledger.task_usd(self.k)
        self.convo.add_user(prompts.COMPACT_NOTES)
        self.convo.flush()
        iteration = self.iterations + 1
        deadline = min(self.clock() + config.COMPACT_NOTES_MAX_S, self.deadline())
        facts = {}

        def ask(tools):
            return self.llm.complete(
                k=self.k, iteration=iteration, logger=self.logger, model=self.model,
                messages=self.convo.messages, tools=tools, deadline=deadline,
                prompt_estimate=self.convo.estimated_tokens())
        try:
            try:
                c = ask(None)
            except ApiError as exc:
                facts["notes_retry"] = str(exc)[:300]
                c = ask(TOOL_SCHEMAS)
        except (ContextOverflow, BudgetExhausted, ApiError) as exc:
            self.convo.retract_last()
            return "", dict(facts, notes_error=str(exc)[:300])
        self.iterations = iteration
        self.times["model_s"] += c.model_s
        self.times["backoff_s"] += c.backoff_s
        message = c.message
        content = (getattr(message, "content", None) or "") if message is not None else ""
        calls = list(getattr(message, "tool_calls", None) or []) if message is not None else []
        reasoning = getattr(message, "reasoning_content", None) if message is not None else None
        if reasoning:
            self.ledger.transcript(self.k, {"iter": iteration, "reasoning": reasoning},
                                   kind="reasoning")
        text = " ".join(content.split())
        facts.update(notes_usd=round(self.ledger.task_usd(self.k) - usd0, 5),
                     notes_tool_calls=len(calls), notes_finish=c.finish_reason)
        markup = prompts.looks_like_tool_markup(text)
        if len(text) < config.COMPACT_NOTES_MIN_CHARS or markup:
            # No usable notes: the reply is not kept and the request is retracted, so the next
            # request is a prefix of this one (the cache holds) and the model's state is as before.
            self.ledger.transcript(self.k, {"iter": iteration, "discarded_notes": content[:500]},
                                   kind=self._kind())
            self.convo.retract_last()
            if len(text) < config.COMPACT_NOTES_MIN_CHARS:
                facts["notes_short"] = len(text)
            if markup:
                facts["notes_leak"] = True
            return "", facts
        self.convo.add_assistant(content, reasoning=reasoning)   # a tool call here is never run
        self.convo.flush()
        return text, facts

    def _kind(self):
        """The transcript kind of the current conversation (attempt and compaction suffixes)."""
        kind = "" if self.attempt_n == 1 else f"a{self.attempt_n}"
        return kind + (f"c{self.restarts}" if self.restarts else "")

    # -- end of task ---------------------------------------------------------------------------

    def _disp(self, op, call, *args):
        """One dispatcher call, timed in a `disp` ledger row; exceptions pass through."""
        t = self.clock()
        try:
            result = call(*args)
        except BaseException as exc:
            self.ledger.write("disp", k=self.k, op=op, secs=round(self.clock() - t, 2),
                              error=f"{type(exc).__name__}: {exc}"[:300])
            raise
        self.ledger.write("disp", k=self.k, op=op, secs=round(self.clock() - t, 2),
                          result=result if isinstance(result, (int, dict)) else None)
        return result

    def end_attempt(self):
        """cleanup -> extract -> evaluate; every step runs even if one before failed. Writes the
        attempt's `attempt` row."""
        reason = self.stop_reason = self.stop_reason or "error:unknown"
        self.state.release_retry(self.k)               # this attempt spends no more
        if self.planning:                              # the attempt ended during its planning step
            self._end_planning(f"stop:{reason}", note=False)
        end = self.end
        t = self.clock()
        if self.convo is not None:
            self.convo.flush()                         # the last results, never sent
        if self.sb is not None:
            try:
                keep = interface_paths(self.task.get("interface"), self.task.get("workdir"))
                workspace = self.workspace or Workspace(self.sb)
                end["cleanup"] = workspace.cleanup(
                    keep=keep, stash_dir=self._stash_dir() if config.STASH_TEST_FILES else None)
                end["stashed"] = list(workspace.last_stashed)
            except Exception as exc:
                end["cleanup_error"] = f"{type(exc).__name__}: {exc}"[:300]
        diff = None
        if self.sb is not None and not self.state.shutdown:
            try:
                diff = self._own_patch()
            except Exception as exc:
                end["diff_error"] = f"{type(exc).__name__}: {exc}"[:300]
        patch_bytes = 0
        no_calls = self.iterations == self.attempt_calls0
        if diff is not None and SANDBOX_CUT_MARK in diff:
            end["diff_cut"] = True              # too long to compare: always graded
        if self.attempt_n > 1 and (no_calls or same_diff(diff, self.graded_diff)):
            # A retry that left the tree as it was graded: continue_task removed the submitted
            # patch, so done() keeps that grading (run_all.py finish_task); grading the same
            # patch again would only hold this slot and a grading slot.
            end["unchanged"] = True
        elif self.sb is not None and not self.state.shutdown:
            patch_bytes = self._extract()
        elif self.sb is not None:
            patch_bytes = self._submit_own_patch()
        end["patch_bytes"] = patch_bytes
        # At the run's wrap-up, done() grades the patch itself; a separate evaluate() would only
        # queue behind other gradings (run_all.py: A3_MAX_GRADING) before done() is reached.
        wrapping = reason in ("global_wrapup", "shutdown") or self.state.global_wrap()
        if patch_bytes and not wrapping:
            t_eval = self.clock()
            try:
                ev = self._disp("evaluate", self.dispatcher.evaluate, self.k)
                end.update(F=ev.get("tests_failed"), T=ev.get("tests_total"), evaluated=True)
                self.graded_diff = diff
            except DispatcherShutdown:
                self.state.set_shutdown()
            except DispatcherError as exc:
                end["evaluate_error"] = str(exc)[:300]
            end["eval_wait_s"] = round(self.clock() - t_eval, 1)
            self.eval_wait_s += end["eval_wait_s"]
        end["finalize_s"] = round(self.clock() - t, 1)
        row = dict(n=self.attempt_n, model=self.model, stop=reason,
                   calls=self.iterations - self.attempt_calls0,
                   usd=round(self.ledger.task_usd(self.k) - self.attempt_raw_usd0, 5),
                   wall_s=round(self.clock() - self.attempt_started, 1),
                   F=end.get("F"), T=end.get("T"), patch_bytes=patch_bytes)
        if self.plan is not None:
            row.update(plan_calls=self.plan["calls"], plan_usd=self.plan.get("usd"),
                       plan_why=self.plan.get("why"), plan_model=self.plan["model"])
        row.update(compactions=self.restarts, compaction_attempts=self.compactions,
                   re_reads=self.re_reads, reattempt=self.reattempt, fresh=self.fresh,
                   cut_offs=self.cut_offs, cap_raised=self.cut_offs >= config.REPLY_CAP_RAISE_AFTER,
                   check_runs=self.check_runs, finish_gated=self.finish_gated,
                   **{f"stall_{key}": value for key, value in self.stall.items()})
        self.attempts.append(row)
        self.ledger.write("attempt", k=self.k, **row, summary=self.summary,
                          **{key: value for key, value in end.items()
                             if key not in row and key not in ("k", "summary")})

    # -- the check written by the planning model (change 11) ---------------------------------

    @staticmethod
    def _path_of(arguments):
        value = loggable_arguments(arguments)
        return str(value.get("path", "")) if isinstance(value, dict) else ""

    def _plan_refusal(self, name, arguments):
        """The refusal text for a tool call during the planning step, or None when it may run:
        bash and view always; in the check reply (change 11) also create, for a new test file or
        a file under WORK_DIR/scratch (the implementation mode) or WORK_DIR (the old mode)."""
        if name not in PLAN_REFUSED_TOOLS:
            return None
        if not self.plan.get("check_reply"):
            if config.PLAN_IMPLEMENT:
                if name == "finish":
                    self.plan["finish_signal"] = True
                    return prompts.implement_finish_refused(f"{config.WORK_DIR}/scratch")
                return None
            return prompts.PLAN_REFUSED
        if name == "create":
            path = self._path_of(arguments)
            if path.strip() and self.tools._in_roots(path):
                rel = self.tools._repo_path(path)
                scratch = posixpath.normpath(f"{config.WORK_DIR}/scratch") + "/"
                full = posixpath.normpath(posixpath.join(self.tools.workdir, path))
                outside_check = rel is None and (not config.PLAN_IMPLEMENT
                                                or full.startswith(scratch))
                if outside_check or (rel is not None and looks_like_test(rel)):
                    return None
        if config.PLAN_IMPLEMENT:
            return prompts.implement_check_refused(f"{config.WORK_DIR}/scratch")
        return prompts.plan_check_refused(f"{config.WORK_DIR}/scratch")

    def _end_check_reply(self):
        """Change 11: the check reply's tool calls have run; the plan kept from the reply before
        ends the planning step, with the check's facts in the hand-over when a check was written."""
        self.plan["check_reply"] = False
        plan_text, cut = self.plan["pending_plan"]
        why = "plan" if plan_text.strip() else ("leak" if self.plan["leaks"] else "no_plan")
        if config.PLAN_IMPLEMENT:
            why = self.plan["implemented"]
        files, command = self.plan["check_files"], self.plan["check_command"]
        if files:
            path, result = files[-1], self.plan["check_result"]
            self.check = {"path": path, "command": command, "files": list(files),
                          "exit": self.plan["check_exit"]}
            text = plan_text + prompts.plan_check_section(path, command, result)
            self._end_planning(why, chars=len(plan_text), cut=cut, text=text, check=self.check)
        else:
            if not self.plan.get("check_skipped"):
                self.plan["check_skipped"] = "no_file"
            self._end_planning(why, chars=len(plan_text), cut=cut, text=plan_text)

    @staticmethod
    def _plan_usd_cap():
        return config.PLAN_IMPLEMENT_USD if config.PLAN_IMPLEMENT else config.PLAN_MAX_USD

    def _implement_done(self, why):
        """End Expert's implementation turn; check replies are additional, within its $ cap."""
        self.plan["implemented"] = why
        under_cap = self.ledger.guard_task_usd(self.k) - self.plan["usd0"] < self._plan_usd_cap()
        if config.PLAN_CHECK and self.plan["edits"] and under_cap:
            self.plan["pending_plan"] = (prompts.implement_record(why), False)
            self.plan["check_reply"] = True
            self.plan["check_rounds"] = 0
            # A refused finish already carries the check request in its unsent tool result.
            channel = "appended_to_tool"
            if not self.plan.get("finish_signal"):
                channel = self.convo.add_note(prompts.plan_check_now_after(f"{config.WORK_DIR}/scratch"))
            self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_check_now",
                              channel=channel, implement=True)
        else:
            if config.PLAN_CHECK:
                self.plan["check_skipped"] = "usd" if not under_cap else "no_edit"
            self._end_planning(why)

    def _plan_taken(self, content, cut, is_plan, leaked=False):
        """The plan reply is in (a plan, a leak, or nothing): change 11's check reply follows when
        it is on and the planning step's $ cap is not spent; otherwise the step ends here."""
        under_cap = self.ledger.guard_task_usd(self.k) - self.plan["usd0"] < config.PLAN_MAX_USD
        if config.PLAN_CHECK and under_cap:
            self.plan["pending_plan"] = (content if is_plan else "", cut)
            self.plan["check_reply"] = True
            self.plan["check_rounds"] = 0
            note = prompts.plan_check_now(f"{config.WORK_DIR}/scratch", plan=is_plan)
            channel = self.convo.add_note(note)
            self.ledger.write("event", k=self.k, iter=self.iterations, what="plan_check_now",
                              channel=channel, plan=is_plan)
        elif is_plan:
            if config.PLAN_CHECK:
                self.plan["check_skipped"] = "usd"
            self._end_planning("plan", chars=len(content), cut=cut, text=content)
        else:
            self._end_planning("leak" if leaked else "no_plan")

    @staticmethod
    def _names_a_file(command, files):
        """Whether a bash command names one of the files (by path or by file name)."""
        names = {f for f in files if f} | {f.rsplit("/", 1)[-1] for f in files if f}
        return any(name and name in command for name in names)

    def _runs_the_check(self, command):
        """Whether a bash command of the model is the check: the check's command, or one that
        names one of its files (by path or by name)."""
        if self.check["command"] and command.strip() == self.check["command"].strip():
            return True
        return self._names_a_file(command, self.check["files"])

    def _finish_gate(self):
        """Change 11: once per attempt, the finish is sent back when the check has not been run
        since the last edit, or when a path the task's Interface names does not exist. Returns
        the text to send back, or None."""
        if self.finish_gated:
            return None
        notes, kinds, missing = [], [], []
        if config.CHECK_FINISH_ROUND and self.check is not None and not self.check_ran:
            notes.append(prompts.finish_check_not_run(self.check["path"], self.check["command"]))
            kinds.append("check_not_run")
        if config.INTERFACE_PATHS_CHECK and self.tools.interface_paths:
            missing = self._missing_interface_paths()
            if missing:
                notes.append(prompts.finish_interface_missing(", ".join(missing)))
                kinds.append("interface_missing")
        if not notes:
            return None
        self.finish_gated = True
        self.ledger.write("event", k=self.k, iter=self.iterations, what="finish_gate", kinds=kinds,
                          missing=missing or None, check_runs=self.check_runs)
        return "\n\n".join(notes)

    def _missing_interface_paths(self):
        """The paths the Interface names that do not exist in the tree (one command)."""
        paths = sorted(p for p in self.tools.interface_paths if p)
        if not paths:
            return []
        script = 'for p in "$@"; do [ -e "./$p" ] || printf "%s\\n" "$p"; done'
        try:
            _, out = self.tools._run(f"sh -c {shlex.quote(script)} sh "
                                     + " ".join(shlex.quote(p) for p in paths))
        except SandboxError:
            return []
        return [p for p in (line.strip() for line in out.split("\n")) if p in paths]

    # -- stall guards (change 7) ---------------------------------------------------------------

    @staticmethod
    def _command_of(arguments):
        value = loggable_arguments(arguments)
        return str(value.get("command", "")) if isinstance(value, dict) else ""

    def _guard_result(self, name, arguments, text, is_error, meta):
        """The repeated-call and same-failure guards on one tool result (change 7): the text the
        model gets and the ledger fields, possibly changed. A failing bash command is counted by
        (command, exit); a view or a successful bash call by its arguments and its result's
        digest (the bash header line, with the timing, left out)."""
        if meta.get("not_run"):
            return text, meta
        if name == "bash" and (meta.get("timed_out") or meta.get("exit") not in (None, 0)):
            code = "timeout" if meta.get("timed_out") else meta.get("exit")
            key = (self._command_of(arguments), code)
            count = self.failures[key] = self.failures.get(key, 0) + 1
            if count == config.STALL_SAME_FAILURE:
                self.stall["same_failure"] += 1
                self.pending_stall = self.pending_stall or ("same_failure", key)
                return (text + "\n\n" + prompts.stall_same_failure(count, code),
                        dict(meta, same_failure=count))
            return text, meta
        if name not in prompts.STALL_WHAT or is_error:
            return text, meta
        key = (name, json.dumps(loggable_arguments(arguments), sort_keys=True, default=str))
        body = text.split("\n", 1)[1] if name == "bash" and "\n" in text else text
        digest = hashlib.sha256(body.encode("utf-8", "replace")).hexdigest()
        seen = self.seen.get(key)
        if seen is None or seen[1] != digest:
            self.seen[key] = [self.iterations, digest, 1]
            return text, meta
        seen[2] += 1
        if seen[2] >= config.STALL_REPEAT_REPLACE:
            self.stall["replaced"] += 1
            return prompts.stall_replaced(seen[0], name), dict(meta, repeat=seen[2], replaced=True)
        if seen[2] >= config.STALL_REPEAT_NOTE:
            self.stall["repeats"] += 1
            return text + "\n\n" + prompts.stall_repeat(seen[0], name), dict(meta, repeat=seen[2])
        return text, meta

    def _stall_after_reply(self):
        """After a reply's tools ran (change 7): the exploration guard, then the Expert ask for a
        guard that fired in this reply. The notes join the last tool result, not yet sent."""
        if not self.explore_noted and not self.edits:
            max_calls, _, max_s = self.caps()
            made = self.iterations - self.attempt_calls0 - ((self.plan or {}).get("calls") or 0)
            threshold = min(config.STALL_EXPLORE_CALLS, max(1, max_calls // 2))
            elapsed = self.clock() - self.attempt_started
            # Change 10: the guard also fires on time, for slow attempts (about 50 s per turn)
            # that would reach their time cap before the call trigger.
            by_time = elapsed >= config.STALL_EXPLORE_TIME_FRAC * max_s
            if made >= threshold or by_time:
                self.explore_noted = True
                self.stall["explore"] += 1
                left = max_calls - (self.iterations - self.attempt_calls0)
                trigger = "calls" if made >= threshold else "time"
                if trigger == "calls":
                    note = prompts.stall_explore(made, left)
                else:
                    note = prompts.stall_explore_time(int(elapsed // 60), int((max_s - elapsed) // 60), left)
                channel = self.convo.add_note(note)
                self.ledger.write("event", k=self.k, iter=self.iterations, what="stall",
                                  guard="explore", trigger=trigger, calls=made,
                                  elapsed_s=round(elapsed, 1), left=left, channel=channel)
                self.pending_stall = self.pending_stall or ("explore", made)
        pending, self.pending_stall = self.pending_stall, None
        if pending is not None:
            note = self._ask_expert_on_stall(*pending)
            if note:
                self.convo.add_note(note)

    def _ask_expert_on_stall(self, why, detail):
        """One call by STALL_EXPERT_MODEL in a fresh small context when a guard fired (change 7;
        the professor's tip 2), once per Standard attempt. Returns the note to append, or None."""
        if not config.STALL_ASK_EXPERT or self.model == config.STALL_EXPERT_MODEL:
            return None
        max_calls, _, _ = self.caps()
        calls_left = max_calls - (self.iterations - self.attempt_calls0)
        skip = None
        if self.stall_asked:
            skip = "asked"
        elif calls_left < config.STALL_EXPERT_MIN_CALLS_LEFT:
            skip = "calls"
        elif self.deadline() - self.clock() < config.STALL_EXPERT_MIN_TIME_LEFT_S:
            skip = "time"
        elif self.state.global_wrap():
            skip = "wrapping"
        elif self.stall["ask_usd"] >= config.STALL_EXPERT_MAX_USD:
            skip = "usd"
        if skip:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="stall_ask", why=why,
                              outcome=f"skipped:{skip}", calls_left=calls_left)
            return None
        self.stall_asked = True
        diff, diff_error = "", None
        try:
            diff = self._own_patch()
        except Exception as exc:
            diff_error = f"{type(exc).__name__}: {exc}"[:300]
        results = [m.get("content") or "" for m in self.convo.messages if m.get("role") == "tool"]
        last_reply = next((m.get("content") or "" for m in reversed(self.convo.messages)
                           if m.get("role") == "assistant"), "")
        if why == "explore":
            why_text = f"They have made {detail} model calls in this attempt without editing any file."
        else:
            command, code = detail
            how = "timed out" if code == "timeout" else f"exited with {code}"
            why_text = (f"The same command has {how} {config.STALL_SAME_FAILURE} times: "
                        f"`{' '.join(str(command).split())[:300]}`")
        plan_text = (self.plan or {}).get("text") or self.carried_plan
        messages = [{"role": "system", "content": prompts.STALL_SYSTEM},
                    {"role": "user", "content": prompts.stall_message(
                        self.task, plan_text, diff, self.commands, results, last_reply, why_text)}]
        iteration = self.iterations + 1
        usd0 = self.ledger.task_usd(self.k)
        deadline = min(self.clock() + config.STALL_EXPERT_MAX_S, self.deadline())
        try:
            c = self.llm.complete(
                k=self.k, iteration=iteration, logger=self.logger, model=config.STALL_EXPERT_MODEL,
                messages=messages, tools=None, deadline=deadline,
                max_tokens=config.STALL_EXPERT_MAX_TOKENS,
                prompt_estimate=int(sum(len(m["content"]) for m in messages) / 3.5))
        except (ContextOverflow, BudgetExhausted, ApiError) as exc:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="stall_ask", why=why,
                              outcome="error", error=str(exc)[:300], diff_error=diff_error)
            return None
        self.iterations = iteration
        self.times["model_s"] += c.model_s
        self.times["backoff_s"] += c.backoff_s
        message = c.message
        content = (getattr(message, "content", None) or "") if message is not None else ""
        usd = round(self.ledger.task_usd(self.k) - usd0, 5)
        self.stall["asks"] += 1
        self.stall["ask_usd"] += usd
        self.ledger.transcript(self.k, {"iter": iteration, "why": why,
                                        "request": messages[1]["content"], "answer": content,
                                        "finish_reason": c.finish_reason}, kind="stall")
        shown = content.strip()
        if len(shown) > config.STALL_EXPERT_SHOWN_CHARS:
            shown = shown[:config.STALL_EXPERT_SHOWN_CHARS].rstrip() + " [cut]"
        self.ledger.write("event", k=self.k, iter=iteration, what="stall_ask", why=why,
                          outcome="answered" if shown else "empty", chars=len(content), usd=usd,
                          finish_reason=c.finish_reason, calls_left=calls_left - 1,
                          diff_chars=len(diff), diff_error=diff_error)
        log(f"task {self.k}: stall ({why}) at call {self.iterations - 1}: "
            f"{config.STALL_EXPERT_MODEL} asked, {len(content)} chars, ${usd:.4f}")
        if not shown:
            return None
        return prompts.STALL_EXPERT_NOTE.format(answer=shown)

    def _reattempt(self):
        """Change 7, item 5: after a first attempt that ended early with no patch (so it was never
        evaluated and no retry follows), one fresh attempt by MODEL with the plan carried over,
        when the API is calm, the sandbox answers, and time and calls remain. Returns True when
        the fresh attempt is set up."""
        if not config.EMPTY_REATTEMPT or self.reattempted or self.attempt_n != 1:
            return False
        if self.end.get("patch_bytes") or self.stop_reason not in config.EMPTY_REATTEMPT_STOPS:
            return False
        if self.state.shutdown or self.sb is None:
            return False
        why = None
        wrap_at = self.state.wrap_at()
        if self.state.global_wrap():
            why = "wrapping"
        elif wrap_at is not None and wrap_at - self.clock() < config.RETRY_MIN_LEFT_S:
            why = "time"
        elif config.TASK_TOTAL_MAX_CALLS and \
                config.TASK_TOTAL_MAX_CALLS - self.iterations < config.EMPTY_REATTEMPT_MIN_CALLS:
            why = "calls"
        elif self.stop_reason == "api_error" and not self._api_calm():
            why = "api"
        elif self.stop_reason == "sandbox_dead" and \
                not (self.tools is not None and self.tools._sandbox_alive()):
            why = "sandbox"
        if why:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="reattempt",
                              restarted=False, why=why, stop=self.stop_reason)
            return False
        self.reattempted = True
        plan_text = (self.plan or {}).get("text") or ""
        calls = config.TASK_MAX_CALLS
        if config.TASK_TOTAL_MAX_CALLS:
            calls = min(calls, config.TASK_TOTAL_MAX_CALLS - self.iterations)
        handoff = prompts.reattempt_message(self.stop_reason, plan_text, calls,
                                            config.TASK_MAX_S // 60)
        self.ledger.write("event", k=self.k, iter=self.iterations, what="reattempt",
                          restarted=True, stop=self.stop_reason, attempt=self.attempt_n + 1,
                          plan_chars=len(plan_text))
        log(f"task {self.k}: attempt 1 ended {self.stop_reason} with no patch; a fresh attempt "
            f"{self.attempt_n + 1} with {config.MODEL}")
        self.carried_plan = plan_text
        self._begin(self.attempt_n + 1, handoff, reattempt=True)
        return True

    def _api_calm(self):
        """Wait, in short steps, until the API has had no retryable error for a while."""
        waited = 0.0
        while self.llm.in_trouble():
            if waited >= config.EMPTY_REATTEMPT_WAIT_S:
                return False
            self._sleep(10)
            waited += 10
        return True

    # -- retries -----------------------------------------------------------------------------

    def _no_retry(self):
        """Why no retry follows the attempt that just ended, or None if one may start."""
        failed = self.end.get("F")
        if config.RETRY_MODEL is None:
            return "off"
        if self.end.get("unchanged"):
            return "unchanged"
        if not self.end.get("evaluated"):
            return "not_evaluated"
        if not isinstance(failed, int) or failed <= 0:
            return "passed" if failed == 0 else "no_verdict"
        if self.attempt_n >= config.RETRY_MAX_ATTEMPTS:
            return "attempts"
        if self.attempt_n > config.RETRY_WHILE_OPENING and not self.state.opening_over:
            return "tasks_unopened"
        if config.RETRY_POLICY == "independent" and self.attempt_n >= 2 and not self._near_miss():
            return "not_near_miss"                     # change 8: the RETRY_MODEL retry earns its place
        # A broken sandbox or a harness bug would most likely fail the retry too; so would the
        # API while it is still in trouble (a retryable error in the last minute, from any task).
        if self.stop_reason in ("no_sandbox", "sandbox_dead", "shutdown") \
                or self.stop_reason.startswith("error:") \
                or (self.stop_reason == "api_error" and self.llm.in_trouble()):
            return f"stop:{self.stop_reason}"
        if self.state.global_wrap():
            return "wrapping"
        wrap_at = self.state.wrap_at()
        if wrap_at is not None and wrap_at - self.clock() < config.RETRY_MIN_LEFT_S:
            return "time"
        # While tasks are still unopened, a retry must be over before opening stops: its time
        # cap, a grading as long as this task's last one, and the dispatcher calls around it.
        stop_open_at = self.state.stop_open_at()
        next_secs = config.TASK_MAX_S if self._fresh_next() else config.RETRY_MAX_S
        needed = next_secs + (self.end.get("eval_wait_s") or 0) + 60
        if (not self.state.opening_over and stop_open_at is not None
                and stop_open_at - self.clock() < needed):
            return "opening_time"
        if config.TASK_TOTAL_MAX_CALLS \
                and config.TASK_TOTAL_MAX_CALLS - self.iterations < config.RETRY_MIN_CALLS:
            return "calls"
        limit = config.RETRY_LATE_STOP_USD if self.state.opening_over else config.RETRY_STOP_USD
        cap = config.TASK_MAX_USD if self._fresh_next() else self._retry_usd()
        if not self.state.reserve_retry(self.k, cap, limit):
            return "money"
        return None                                    # the retry's $ is now reserved

    def _retry(self):
        """After a failed evaluation, when allowed: continue_task, then set up the next attempt
        with the handoff. Returns False when the task ends here."""
        why = self._no_retry()
        if why is not None:
            if why not in ("off", "not_evaluated", "passed"):
                self.ledger.write("event", k=self.k, iter=self.iterations, what="no_retry",
                                  why=why, attempt=self.attempt_n)
            return False
        failed, total, summary = self.end.get("F"), self.end.get("T"), self.summary
        diff = self.graded_diff or ""      # after cleanup: the tree that was extracted and graded
        try:
            self._disp("continue", self.dispatcher.continue_task, self.k)
        except DispatcherShutdown:
            self.state.release_retry(self.k)
            self.state.set_shutdown()
            return False
        except DispatcherError as exc:
            self.state.release_retry(self.k)
            self.end["continue_error"] = str(exc)[:300]
            return False
        if self._fresh_next():
            return self._fresh_retry(failed, total)
        reflection, reflect = self._reflect(failed, total)
        calls = self._retry_calls()
        # Change 8: an earlier attempt that scored better than the last one left its change as a
        # diff under its stash directory; the retry is told where.
        saved = ""
        better = [a for a in self.attempts[:-1] if isinstance(a.get("F"), int) and a.get("T")
                  and isinstance(failed, int) and total and a["F"] / a["T"] < failed / total]
        if better and config.RETRY_POLICY == "independent":
            best = min(better, key=lambda a: a["F"] / a["T"])
            saved = prompts.saved_note(best["n"], best["F"], best["T"],
                                      f"{config.WORK_DIR}/scratch/attempt{best['n']}/tree.diff")
        if config.TASK_TOTAL_MAX_CALLS:
            calls = min(calls, config.TASK_TOTAL_MAX_CALLS - self.iterations)
        handoff = prompts.retry_message(failed, total, summary, diff, calls,
                                        config.RETRY_MAX_S // 60,
                                        history=[(a["n"], a["F"], a["T"]) for a in self.attempts],
                                        reflection=reflection, commands=self.commands,
                                        stashed=self.end.get("stashed") or (),
                                        stash_dir=self._stash_dir(), saved=saved)
        stop_open_at = self.state.stop_open_at()
        self.ledger.write("event", k=self.k, iter=self.iterations, what="retry",
                          attempt=self.attempt_n + 1, model=config.RETRY_MODEL, F=failed, T=total,
                          diff_chars=len(diff), diff_error=self.end.get("diff_error"),
                          opening_over=self.state.opening_over,
                          stop_open_in_s=None if stop_open_at is None
                          else round(stop_open_at - self.clock(), 1),
                          run_usd=round(self.ledger.guard_usd(), 4), commands=len(self.commands),
                          stashed=len(self.end.get("stashed") or ()), cap_usd=self._retry_usd(),
                          saved=bool(saved), **reflect)
        log(f"task {self.k}: {failed}/{total} hidden tests failing; attempt {self.attempt_n + 1} "
            f"with {config.RETRY_MODEL}")
        self._begin(self.attempt_n + 1, handoff)
        return True

    def _near_miss(self):
        """Change 8: whether the best verdict so far earns the RETRY_MODEL retry: a near-miss, or
        every test failing when RETRY_EXPERT_ALL_FAILED."""
        graded = [(a["F"], a.get("T")) for a in self.attempts
                  if isinstance(a.get("F"), int) and a.get("T")]
        if not graded:
            return False
        failed, total = min(graded, key=lambda ft: (ft[0] / ft[1], ft[0]))
        if failed <= config.RETRY_NEAR_MISS or failed / total <= config.RETRY_NEAR_MISS_FRAC:
            return True
        return bool(config.RETRY_EXPERT_ALL_FAILED and failed == total)

    def _fresh_next(self):
        """Whether the next attempt is the independent fresh attempt (change 8)."""
        return config.RETRY_POLICY == "independent" and self.attempt_n == 1

    def _fresh_retry(self, failed, total):
        """Change 8: set the failed attempt's changes aside and start attempt 2 as a fresh first
        attempt: planned and guarded like attempt 1, told only the verdict."""
        notes, moved, reset_error = [], [], None
        try:
            workspace = self.workspace or Workspace(self.sb)
            notes, moved = workspace.set_aside(self._stash_dir())
        except Exception as exc:
            reset_error = f"{type(exc).__name__}: {exc}"[:300]
        calls = config.TASK_MAX_CALLS
        if config.TASK_TOTAL_MAX_CALLS:
            calls = min(calls, config.TASK_TOTAL_MAX_CALLS - self.iterations)
        handoff = prompts.fresh_message(failed, total, calls, config.TASK_MAX_S // 60)
        self.ledger.write("event", k=self.k, iter=self.iterations, what="retry",
                          attempt=self.attempt_n + 1, model=config.MODEL, fresh=True, F=failed,
                          T=total, cap_usd=config.TASK_MAX_USD, moved=len(moved),
                          reset_notes=notes or None, reset_error=reset_error,
                          opening_over=self.state.opening_over,
                          run_usd=round(self.ledger.guard_usd(), 4))
        log(f"task {self.k}: {failed}/{total} hidden tests failing; a fresh attempt "
            f"{self.attempt_n + 1} with {config.MODEL} ({len(moved)} files set aside"
            f"{'; reset error' if reset_error else ''})")
        self._begin(self.attempt_n + 1, handoff, fresh=True)
        return True

    def _reflect(self, failed, total):
        """One model call in the attempt's own conversation once the verdict is known (Lecture 4
        research, Reflexion): what the failing tests most likely cover, what was not checked, what
        to change next. Standard, so the context is read at the cached rate (or cheaply); any
        failure leaves the handoff without it. Returns (text, facts for the retry event)."""
        if not config.RETRY_REFLECT or self.convo is None:
            return "", {}
        usd0 = self.ledger.task_usd(self.k)
        self.convo.add_user(prompts.reflect_message(failed, total))
        self.convo.flush()
        iteration = self.iterations + 1
        deadline = self.clock() + config.REFLECT_MAX_S
        wrap_at = self.state.wrap_at()
        if wrap_at is not None:
            deadline = min(deadline, wrap_at)
        try:
            c = self.llm.complete(
                k=self.k, iteration=iteration, logger=self.logger, model=config.MODEL,
                messages=self.convo.messages, tools=TOOL_SCHEMAS, deadline=deadline,
                prompt_estimate=self.convo.estimated_tokens())
        except (ContextOverflow, BudgetExhausted, ApiError) as exc:
            return "", {"reflect_error": str(exc)[:300]}
        self.iterations = iteration
        self.times["model_s"] += c.model_s
        self.times["backoff_s"] += c.backoff_s
        message = c.message
        content = (getattr(message, "content", None) or "") if message is not None else ""
        calls = list(getattr(message, "tool_calls", None) or []) if message is not None else []
        reasoning = getattr(message, "reasoning_content", None) if message is not None else None
        if reasoning:
            self.ledger.transcript(self.k, {"iter": iteration, "reasoning": reasoning},
                                   kind="reasoning")
        self.convo.add_assistant(content, reasoning=reasoning)   # a tool call here is never run
        self.convo.flush()
        text = " ".join(content.split())
        if len(text) > config.REFLECT_MAX_CHARS:
            text = text[:config.REFLECT_MAX_CHARS].rstrip() + " [cut]"
        return text, {"reflect_chars": len(text), "reflect_tool_calls": len(calls),
                      "reflect_usd": round(self.ledger.task_usd(self.k) - usd0, 5),
                      "reflect_finish": c.finish_reason}

    def _review_before_finish(self):
        """Change 3: one call by REVIEW_MODEL in a fresh, small context, when a Standard attempt
        finishes and the harness would accept it: the task, the diff, the summary and the last
        commands, judged against the Requirements and the Interface. Returns the finish result
        to send back when the review lists gaps (once per attempt), else None."""
        if config.FINISH_REVIEW != "expert" or self.reviewed or self.model == config.REVIEW_MODEL:
            return None
        max_calls, _, _ = self.caps()
        calls_left = max_calls - (self.iterations - self.attempt_calls0)
        time_left = self.deadline() - self.clock()
        why = None
        if calls_left < config.REVIEW_MIN_CALLS_LEFT:
            why = "calls"
        elif time_left < config.REVIEW_MIN_TIME_LEFT_S:
            why = "time"
        elif self.state.global_wrap():
            why = "wrapping"
        if why:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="review",
                              outcome=f"skipped:{why}", calls_left=calls_left)
            return None
        self.reviewed = True
        try:
            diff = self._own_patch()
        except Exception as exc:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="review",
                              outcome="no_diff", error=f"{type(exc).__name__}: {exc}"[:300])
            return None
        if not diff.strip():
            return None
        messages = [{"role": "system", "content": prompts.REVIEW_SYSTEM},
                    {"role": "user", "content": prompts.review_message(
                        self.task, diff, self.summary, self.commands)}]
        iteration = self.iterations + 1
        usd0 = self.ledger.task_usd(self.k)
        deadline = min(self.clock() + config.REVIEW_MAX_S, self.deadline())
        try:
            c = self.llm.complete(
                k=self.k, iteration=iteration, logger=self.logger, model=config.REVIEW_MODEL,
                messages=messages, tools=None, deadline=deadline,
                max_tokens=config.REVIEW_MAX_TOKENS,
                prompt_estimate=int(sum(len(m["content"]) for m in messages) / 3.5))
        except (ContextOverflow, BudgetExhausted, ApiError) as exc:
            self.ledger.write("event", k=self.k, iter=self.iterations, what="review",
                              outcome="error", error=str(exc)[:300])
            return None
        self.iterations = iteration
        self.times["model_s"] += c.model_s
        self.times["backoff_s"] += c.backoff_s
        message = c.message
        content = (getattr(message, "content", None) or "") if message is not None else ""
        self.ledger.transcript(self.k, {"iter": iteration, "request": messages[1]["content"],
                                        "review": content, "finish_reason": c.finish_reason},
                               kind="review")
        outcome, shown = prompts.review_verdict(content)
        self.ledger.write("event", k=self.k, iter=iteration, what="review", outcome=outcome,
                          chars=len(content), usd=round(self.ledger.task_usd(self.k) - usd0, 5),
                          finish_reason=c.finish_reason, calls_left=calls_left - 1)
        if outcome != "gaps":
            return None
        return prompts.REVIEW_GAPS.format(review=shown)

    # -- the task's end ----------------------------------------------------------------------

    def finish(self):
        """done(k) with the last attempt's stop reason, then the task_end row."""
        reason = self.stop_reason
        self.state.release_retry(self.k)
        self._done(reason)
        end = self.end
        # The verdict may be an earlier attempt's (the last one changed nothing): report that
        # attempt's patch and F/T, and which attempt was graded.
        graded = next((a for a in reversed(self.attempts) if a.get("F") is not None), None)
        if end.get("unchanged") and graded is not None:
            end.update(patch_bytes=graded.get("patch_bytes"), F=graded.get("F"), T=graded.get("T"))
        end["graded_attempt"] = graded.get("n") if graded is not None else None
        # done()'s answer is lost after a shutdown: then this attempt's own grading, if any.
        final = end.get("final_F") if end.get("final_F") is not None else end.get("F")
        end.update(stop_reason=reason, iterations=self.iterations, attempt=self.attempt_n,
                   attempts=self.attempts, solved_on=self.attempt_n if final == 0 else None,
                   usd=self.ledger.task_usd(self.k), usd_blind=self.ledger.task_usd(self.k, True),
                   wall_s=round(self.clock() - self.started, 1),
                   eval_wait_s=round(self.eval_wait_s, 1), max_prompt=self.max_prompt,
                   nudges=self.nudges, finish_rounds=self.finish_rounds, summary=self.summary,
                   **{key: round(value, 1) for key, value in self.times.items()})
        self.ledger.write("task_end", k=self.k, **end)
        self.ledger.close_transcript(self.k)
        log(f"task {self.k}: {reason} after {self.iterations} calls in {self.attempt_n} "
            f"attempt(s), ${self.ledger.task_usd(self.k):.4f}, patch {end.get('patch_bytes')} "
            f"bytes, F/T {end.get('F')}/{end.get('T')}")

    def _extract(self):
        try:
            size = self._disp("extract", self.dispatcher.extract_patch, self.k)
        except DispatcherShutdown:
            self.state.set_shutdown()
            return self._submit_own_patch()
        except DispatcherError as exc:
            self.end["extract_error"] = str(exc)[:300]
            size = 0
        if size:
            return size
        # 0 bytes although the tree has changes: the host's `git add -N . && git diff` failed
        # (cleanup already removed a stale index.lock). Build the patch here and submit it.
        try:
            changed = self.workspace.changed_paths() if self.workspace else []
            if not changed:
                return 0
            text = self._own_patch()
            if text:
                self.end["extract_fallback"] = True
                return self._disp("submit", self.dispatcher.submit_patch, self.k, text)
        except DispatcherShutdown:
            self.state.set_shutdown()
        except Exception as exc:
            self.end["extract_fallback_error"] = f"{type(exc).__name__}: {exc}"[:300]
        return 0

    def _submit_own_patch(self):
        """After a shutdown no dispatcher request is answered, but submit_patch writes the patch
        file directly, and the host grades the patch of every task still open at the end
        (run_all.py serve). Best effort."""
        try:
            if self.workspace and self.workspace.changed_paths():
                text = self._own_patch()
                if text:
                    self.end["submitted_after_shutdown"] = True
                    return self._disp("submit", self.dispatcher.submit_patch, self.k, text)
        except Exception as exc:
            self.end["extract_fallback_error"] = f"{type(exc).__name__}: {exc}"[:300]
        return 0

    def _own_patch(self):
        """`git diff` of tracked files plus each new file diffed against /dev/null."""
        r = self.sb.exec(f"{GIT} diff; {GIT} ls-files --others --exclude-standard -z | "
                         f"xargs -0 -r -n1 {GIT} diff --no-index -- /dev/null; true",
                         timeout_s=config.HARNESS_EXEC_TIMEOUT_S)
        return r.get("output", "") if r.get("exit_code") == 0 else ""

    def _done(self, reason):
        if self.state.shutdown:
            self._run_end_ourselves(reason)
            return
        t_done = self.clock()
        for attempt in range(3):
            try:
                resp = self._disp("done", self.dispatcher.done, self.k, reason, self.iterations)
                self.end.update(final_F=resp.get("tests_failed"), final_T=resp.get("tests_total"))
                break
            except DispatcherShutdown:
                self.state.set_shutdown()
                self._run_end_ourselves(reason)
                break
            except DispatcherError as exc:
                self.end["done_error"] = str(exc)[:300]
                if "is not live" in str(exc) or attempt == 2:
                    self._run_end_ourselves(reason)
                    break
                time.sleep(2 * (attempt + 1))
        self.end["done_wait_s"] = round(self.clock() - t_done, 1)

    def _run_end_ourselves(self, reason):
        """dispatcher.done() logs run_end only after a good reply (dispatcher.py:113-118)."""
        try:
            self.logger.run_end(reason, int(self.iterations))
        except Exception:
            pass
