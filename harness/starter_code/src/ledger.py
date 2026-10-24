"""Our own record of what the run spends and where its time goes.

The course trace (dispatcher.logger(k)) has no field for cached tokens, so it cannot price a
call, and cached input costs 20x less than fresh input. The ledger reads `usage` from every
response and keeps:
  * the run's $ total and each task's $, which the guards read live;
  * one JSON line per event in <LEDGER_DIR>/ledger.jsonl, flushed as it is written;
  * each task's messages, exactly as sent, in <LEDGER_DIR>/transcripts/<k>.jsonl.

Every call is priced two ways: `usd` with the cache discount (what we expect to be billed)
and `usd_blind`, as if nothing were cached (what the trace's token counts alone would give).
Which one the leaderboard reports is checked on the first submission (config.GUARD_FORMULA).

Writing never raises: a full disk or a bad value must not fail a task. A line that cannot be
written is reported on stderr and dropped.
"""
import json
import os
import sys
import threading
import time

from src import config


def usage_field(obj, name):
    """A field of `usage` or of one of its parts: a pydantic object, a dict, or None."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _count(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def token_counts(usage):
    """(prompt, cached, completion) from a response's usage; missing values count as 0.

    cached = usage.prompt_tokens_details.cached_tokens, else the top-level cached_tokens
    (this API reports both, PHASE0_FINDINGS.md section 2c). It is part of prompt_tokens, so
    it is clamped to it.
    """
    prompt = _count(usage_field(usage, "prompt_tokens"))
    cached = usage_field(usage_field(usage, "prompt_tokens_details"), "cached_tokens")
    if cached is None:
        cached = usage_field(usage, "cached_tokens")
    return prompt, min(_count(cached), prompt), _count(usage_field(usage, "completion_tokens"))


def raw_usage(usage):
    """usage as plain JSON-able data, for the ledger."""
    if usage is None or isinstance(usage, dict):
        return usage
    dump = getattr(usage, "model_dump", None)
    if callable(dump):
        try:
            return dump()
        except Exception:
            pass
    try:
        return str(usage)
    except Exception:
        return None


class Ledger:
    def __init__(self, directory=None, prices=None, clock=time.time):
        self.directory = directory or config.LEDGER_DIR
        self.prices = dict(prices or config.PRICES_PER_M)
        self._clock = clock
        self._lock = threading.Lock()
        self._usd = 0.0
        self._usd_blind = 0.0
        self._task_usd = {}
        self._task_usd_blind = {}
        self._file = None
        self._transcripts = {}
        self._closed = False
        try:
            os.makedirs(self.directory, exist_ok=True)
            self._file = open(os.path.join(self.directory, "ledger.jsonl"), "a", buffering=1,
                              encoding="utf-8")
        except OSError as exc:
            self._warn(f"ledger file not available ({exc}); totals are still kept in memory")

    # -- prices -------------------------------------------------------------------------

    def cost(self, model, prompt, cached, completion):
        """(usd, usd_blind, priced): priced is False if the model has no known price."""
        rates = self.prices.get(model)
        priced = rates is not None
        p_in, p_cached, p_out = rates if priced else config.UNKNOWN_MODEL_PRICE
        usd = ((prompt - cached) * p_in + cached * p_cached + completion * p_out) / 1e6
        usd_blind = (prompt * p_in + completion * p_out) / 1e6
        return usd, usd_blind, priced

    # -- recording ----------------------------------------------------------------------

    def record_call(self, k, iteration, model, usage, **fields):
        """Price one completed model call, add it to the totals and write its `call` row.
        Returns the row (prompt, cached, completion, usd, ...)."""
        prompt, cached, completion = token_counts(usage)
        usd, usd_blind, priced = self.cost(model, prompt, cached, completion)
        self._add(k, usd, usd_blind)
        row = dict(k=k, iter=iteration, model=model, prompt=prompt, cached=cached,
                   completion=completion, usd=usd, usd_blind=usd_blind, **fields)
        if not priced:
            row["unpriced_model"] = True
        row["usage"] = raw_usage(usage)
        self.write("call", **row)
        return row

    def charge_estimate(self, k, iteration, model, prompt, completion, why):
        """Charge a request that is billed but returned no usage (a timed-out generation):
        its prompt as uncached input plus an assumed completion. Flagged `estimated`."""
        usd, _, _ = self.cost(model, prompt, 0, completion)
        self._add(k, usd, usd)
        self.write("call", k=k, iter=iteration, model=model, prompt=prompt, cached=0,
                   completion=completion, usd=usd, usd_blind=usd, estimated=True, why=why)
        return usd

    def write(self, kind, **fields):
        """One JSON line; never raises."""
        line = {"t": round(self._clock(), 3), "kind": kind, **fields}
        try:
            text = json.dumps(line, ensure_ascii=False, default=str)
        except Exception as exc:  # json.dumps calls str() on odd values
            text = json.dumps({"t": line["t"], "kind": kind, "unserializable": str(exc)})
        with self._lock:
            if self._file is None:
                return
            try:
                self._file.write(text + "\n")
            except (OSError, ValueError) as exc:
                self._warn(f"could not write a ledger line ({exc})")

    def transcript(self, k, message, kind=""):
        """Append one message of task k, exactly as sent to the model, to transcripts/<k>.jsonl;
        with a kind (e.g. "reasoning"), a side record to transcripts/<k>.<kind>.jsonl. Never raises."""
        if not config.LOG_TRANSCRIPTS:
            return
        try:
            text = json.dumps(message, ensure_ascii=False, default=str)
        except Exception as exc:  # json.dumps calls str() on odd values
            text = json.dumps({"unserializable": str(exc)})
        with self._lock:
            if self._closed:
                return
            try:
                f = self._transcripts.get((k, kind))
                if f is None:
                    folder = os.path.join(self.directory, "transcripts")
                    os.makedirs(folder, exist_ok=True)
                    name = f"{k}.{kind}.jsonl" if kind else f"{k}.jsonl"
                    f = self._transcripts[(k, kind)] = open(os.path.join(folder, name), "a",
                                                            buffering=1, encoding="utf-8")
                f.write(text + "\n")
            except (OSError, ValueError) as exc:
                self._warn(f"could not write transcript line for task {k} ({exc})")

    def close_transcript(self, k):
        with self._lock:
            files = [self._transcripts.pop(key) for key in list(self._transcripts) if key[0] == k]
        for f in files:
            try:
                f.close()
            except OSError:
                pass

    def close(self):
        with self._lock:
            files = list(self._transcripts.values()) + ([self._file] if self._file else [])
            self._closed = True
            self._transcripts.clear()
            self._file = None
        for f in files:
            try:
                f.close()
            except OSError:
                pass

    # -- totals ---------------------------------------------------------------------------

    def total_usd(self, blind=False):
        with self._lock:
            return self._usd_blind if blind else self._usd

    def task_usd(self, k, blind=False):
        with self._lock:
            return (self._task_usd_blind if blind else self._task_usd).get(k, 0.0)

    def guard_usd(self):
        """The run's $ as the global guards see it: the configured formula times the margin."""
        return self.total_usd(blind=config.GUARD_FORMULA == "blind") * config.LEDGER_SAFETY

    def guard_task_usd(self, k):
        return self.task_usd(k, blind=config.GUARD_FORMULA == "blind") * config.LEDGER_SAFETY

    def _add(self, k, usd, usd_blind):
        with self._lock:
            self._usd += usd
            self._usd_blind += usd_blind
            self._task_usd[k] = self._task_usd.get(k, 0.0) + usd
            self._task_usd_blind[k] = self._task_usd_blind.get(k, 0.0) + usd_blind

    @staticmethod
    def _warn(msg):
        print(f"[a3 ledger] {msg}", file=sys.stderr, flush=True)
