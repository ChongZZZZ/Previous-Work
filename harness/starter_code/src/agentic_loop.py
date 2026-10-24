"""The agent: madsOpt.py (course code) calls Agent(dispatcher).run(), and that is all it needs.

run() is the scheduler. It keeps up to `cap` tasks open at once, one thread per task
(src/solver.py does the task), and opens the next task as soon as one is done, because time per
solved task counts from the first task opened to the last one done. Rules it keeps:

  * run() returns only when no task is open any more (or shortly after DispatcherShutdown).
    The host ends the whole run as soon as madsOpt exits (run_all.py serve() stops on `end`) and
    grades every task still open with whatever patch it has, usually none.
  * Only "too many live tasks (N)" lowers the cap, to N, the host's own limit (A3_MAX_LIVE; the
    agent cannot read it). Any other DispatcherError from next_task is a failure on the host
    side, after the task was already used up (run_all.py: next_k += 1 comes before the sandbox
    starts), so asking again is safe: it is retried with backoff and never lowers the cap.
  * No task is opened after the stop-opening point (time or $), nor while the API is in
    trouble (a retryable error in the last minute, from any task).
  * DispatcherShutdown from any call, or the host's `shutdown` file, stops everything.
  * An exception in the scheduler itself is logged and retried; after SCHED_MAX_ERRORS in a
    row, no new task is opened and the open ones are drained.
"""
import hashlib
import os
import platform
import re
import sys
import threading
import time
import traceback

from dispatcher import DispatcherError, DispatcherShutdown
from src import config, prompts
from src.ledger import Ledger
from src.llm import LLM
from src.solver import RunState, Solver, log
from src.tools import TOOL_SCHEMAS

_HOST_FULL = re.compile(r"too many live tasks \((\d+)\)")
SRC = os.path.dirname(os.path.abspath(__file__))


def harness_hash():
    """sha256 over src/*.py, so every run's numbers point at the exact code that made them."""
    digest = hashlib.sha256()
    for name in sorted(os.listdir(SRC)):
        if name.endswith(".py"):
            with open(os.path.join(SRC, name), "rb") as f:
                digest.update(name.encode() + b"\0" + f.read())
    return digest.hexdigest()[:16]


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class Agent:
    def __init__(self, dispatcher, llm=None, ledger=None, solver_factory=None,
                 clock=time.monotonic, sleep=time.sleep, shutdown_file=None):
        self.dispatcher = dispatcher
        self.ledger = ledger or Ledger()
        self.llm = llm or LLM(self.ledger)
        self.clock = clock
        self.sleep = sleep
        self.state = RunState(self.ledger, clock=clock)
        self.solver_factory = solver_factory or (
            lambda task: Solver(task, dispatcher, self.llm, self.ledger, self.state, clock=clock))
        if shutdown_file is None:
            try:
                from dispatcher import SEQ_DIR
                shutdown_file = os.path.join(SEQ_DIR, "shutdown")
            except ImportError:
                shutdown_file = ""
        self.shutdown_file = shutdown_file
        self.cap = config.INITIAL_CAP
        self.open = 0
        self.threads = []

    # -- the run ----------------------------------------------------------------------------

    def run(self):
        self._write_header()
        try:
            self._schedule()
        finally:
            self._join()
            self.ledger.write("run_end", usd=round(self.ledger.total_usd(), 6),
                              usd_blind=round(self.ledger.total_usd(blind=True), 6),
                              shutdown=self.state.shutdown, tasks=len(self.threads))
            log(f"run over: {len(self.threads)} tasks, ${self.ledger.total_usd():.4f}")

    def _schedule(self):
        exhausted = stop_open = False
        next_errors = scheduler_errors = 0
        retry_at = 0.0
        while True:
            try:
                if self.state.shutdown or (self.shutdown_file and os.path.exists(self.shutdown_file)):
                    self.state.set_shutdown()
                    return
                if not stop_open and self.state.stop_opening():
                    stop_open = True
                    self.ledger.write("sched", event="stop_opening", open=self.open,
                                      usd=round(self.ledger.guard_usd(), 4))
                if exhausted or stop_open:
                    self.state.opening_over = True       # retries may now use every slot
                    if self.open == 0:
                        return
                can_open = (not exhausted and not stop_open and self.open < self.cap
                            and self.clock() >= retry_at and not self.llm.in_trouble())
                opened = False
                if can_open:
                    t_call = self.clock()
                    try:
                        task = self.dispatcher.next_task()
                        self.ledger.write("disp", op="next_task", secs=round(self.clock() - t_call, 2),
                                          k=task.get("task") if task else None)
                    except DispatcherShutdown:
                        self.state.set_shutdown()
                        return
                    except DispatcherError as exc:
                        full = _HOST_FULL.search(str(exc))
                        if full:
                            self.cap = max(1, int(full.group(1)))
                            self.ledger.write("sched", event="cap", cap=self.cap, open=self.open)
                            if self.open == 0:   # the host counts a task we no longer work on
                                log(f"host full ({exc}) while no task of ours is open")
                        else:
                            next_errors += 1
                            backoff = min(config.NEXT_TASK_BACKOFF_MAX_S, 2 ** next_errors)
                            retry_at = self.clock() + backoff
                            self.ledger.write("sched", event="next_task_error", open=self.open,
                                              error=str(exc)[:300], backoff_s=backoff)
                            log(f"next_task failed ({exc}); retrying in {backoff} s")
                    else:
                        next_errors = 0
                        if task is None:
                            exhausted = self.state.opening_over = True
                            self.ledger.write("sched", event="exhausted", open=self.open)
                        else:
                            self.state.start_clock(t_call)
                            self._start(task)
                            opened = True
                scheduler_errors = 0
                if not opened:
                    with self.state.cond:
                        self.state.cond.wait(timeout=config.SCHED_TICK_S)
            except Exception as exc:  # never let one bad tick end the run
                scheduler_errors += 1
                self.ledger.write("sched", event="scheduler_error", error=f"{type(exc).__name__}: "
                                  f"{exc}", traceback=traceback.format_exc()[-2000:])
                log(f"scheduler error {scheduler_errors}: {type(exc).__name__}: {exc}")
                if scheduler_errors >= config.SCHED_MAX_ERRORS:
                    stop_open = True
                self.sleep(config.SCHED_TICK_S)

    def _start(self, task):
        with self.state.cond:
            self.open += 1
        self.ledger.write("sched", event="open", k=task.get("task"), open=self.open, cap=self.cap)
        thread = threading.Thread(target=self._work, args=(task,), daemon=True,
                                  name=f"task-{task.get('task')}")
        self.threads.append(thread)
        thread.start()

    def _work(self, task):
        try:
            self.solver_factory(task).run()
        except DispatcherShutdown:
            self.state.set_shutdown()
        except BaseException as exc:  # Solver.run never raises; this is the last line of defence
            self.ledger.write("sched", event="worker_error", k=task.get("task"),
                              error=f"{type(exc).__name__}: {exc}",
                              traceback=traceback.format_exc()[-2000:])
            # The host still counts the task as live; without done() its slot is lost for the
            # rest of the run. A retry's $ reservation must not outlive the task either.
            self.state.release_retry(task.get("task"))
            try:
                self.dispatcher.done(task.get("task"), f"error:{type(exc).__name__}", 0)
            except Exception:
                pass
        finally:
            with self.state.cond:
                self.open -= 1
                self.state.cond.notify_all()

    def _join(self):
        """Wait for every task thread; once the run is shut down, at most SHUTDOWN_JOIN_S more."""
        give_up = None
        for thread in self.threads:
            while thread.is_alive():
                if self.state.shutdown and give_up is None:
                    give_up = self.clock() + config.SHUTDOWN_JOIN_S
                if give_up is not None and self.clock() >= give_up:
                    return
                thread.join(timeout=config.SCHED_TICK_S if give_up is None
                            else min(config.SCHED_TICK_S, give_up - self.clock()))

    def _write_header(self):
        try:
            import openai
            openai_version = getattr(openai, "__version__", "?")
        except ImportError:
            openai_version = None
        settings = {name: getattr(config, name) for name in dir(config)
                    if name.isupper() and not name.startswith("_")}
        self.ledger.write("run", harness=harness_hash(), label=config.RUN_LABEL,
                          prompt_sha=_sha(prompts.SYSTEM_PROMPT), schemas_sha=_sha(repr(TOOL_SCHEMAS)),
                          python=platform.python_version(), openai=openai_version,
                          config=settings)
        try:
            import json
            with open(os.path.join(self.ledger.directory, "run_prompt.json"), "w",
                      encoding="utf-8") as f:
                json.dump({"system": prompts.SYSTEM_PROMPT, "tools": TOOL_SCHEMAS}, f, indent=1)
        except OSError:
            pass
        log(f"harness {harness_hash()}, model {config.MODEL}, caps: {config.TASK_MAX_CALLS} calls, "
            f"${config.TASK_MAX_USD}, {config.TASK_MAX_S} s per task; run limit {config.RUN_LIMIT_S} s")
