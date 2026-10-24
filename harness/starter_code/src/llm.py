"""One model call against the course API, with retries that respect the task's deadline.

The OpenAI SDK retries failed requests on its own, without telling the caller, so the client
is made with max_retries=0 and retrying happens here, with one api_retry line in the trace per
retry. Beyond that:
  * Every wait is bounded by the task's deadline. A request's timeout is
    min(REQUEST_TIMEOUT_S, time left - 30 s); a backoff that would end within WRAP_RESERVE_S of
    the deadline raises BudgetExhausted instead, so the task still has time to extract its patch.
  * A server's retry_after (in the error body, as this API sends it, or in the Retry-After
    header) is honoured in full, and never shortens our own exponential backoff with jitter.
  * A timed-out request is billed but returns no usage: it is charged an estimate in the ledger
    and retried once only.
  * Errors are told apart by status code, not by exception class: `openai` is not pinned in the
    agent image, and the leaderboard builds its own.
      - 408, 409, 429, 5xx, connection errors, timeouts, an empty `choices`: retried;
      - a 400 about the context length: ContextOverflow, after one retry with a small max_tokens;
      - any other 4xx: ApiError at once (a second try cannot succeed).
  * Every successful call is priced in the ledger and logged as api_request, with the
    iteration the solver passes in (one per model call, increasing per task).
  * A retryable error from any task is noted in `last_trouble`; the scheduler pauses opening
    new tasks while the API is in trouble, rather than spending them on failing calls.
"""
import collections
import os
import random
import re
import threading
import time

from src import config
from src.ledger import usage_field

Completion = collections.namedtuple(
    "Completion", "response message finish_reason row model_s attempts backoff_s")

RETRY_STATUS = {408, 409, 429}
_CONTEXT_PHRASES = re.compile(r"context length|context window|maximum context|context_length_exceeded",
                              re.IGNORECASE)


class LLMError(Exception):
    """A model call that did not produce a response; the message says why."""


class ContextOverflow(LLMError):
    """The prompt does not fit the model's context window."""


class BudgetExhausted(LLMError):
    """Waiting any longer would run past the task's deadline."""


class ApiError(LLMError):
    """An error a retry cannot fix, or retries ran out."""


def redact(text):
    key = os.environ.get("CS2680_API_KEY")
    return text.replace(key, "[REDACTED]") if key and len(key) >= 8 else text


def status_of(exc):
    status = getattr(exc, "status_code", None)
    return status if isinstance(status, int) else None


def is_timeout(exc):
    return "timeout" in type(exc).__name__.lower()


def is_connection_error(exc):
    # APIConnectionError and its subclass APITimeoutError have no status code.
    return status_of(exc) is None and any(
        cls.__name__ in ("APIConnectionError", "APITimeoutError") for cls in type(exc).__mro__)


def error_text(exc):
    """The error's message plus its body, for matching and for the trace."""
    body = getattr(exc, "body", None)
    return f"{exc} {body}" if body is not None else str(exc)


def describe(exc):
    """The error as recorded in api_retry and the ledger: type, status, message, key removed."""
    status = status_of(exc)
    label = f"{type(exc).__name__} ({status})" if status else type(exc).__name__
    return redact(f"{label}: {error_text(exc)}")[:500]


def retry_after_s(exc):
    """The server's requested wait in seconds, if it sent one.

    This API puts retry_after in the error body (PHASE0_FINDINGS.md section 2c). The SDK
    passes the body's inner "error" object as exc.body, so both shapes are checked, then the
    Retry-After header.
    """
    body = getattr(exc, "body", None)
    candidates = []
    if isinstance(body, dict):
        candidates.append(body.get("retry_after"))
        inner = body.get("error")
        if isinstance(inner, dict):
            candidates.append(inner.get("retry_after"))
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if headers is not None:
        try:
            candidates.append(headers.get("retry-after"))
            ms = headers.get("retry-after-ms")
            candidates.append(float(ms) / 1000 if ms is not None else None)
        except Exception:
            pass
    for value in candidates:
        try:
            seconds = float(value)
        except (TypeError, ValueError):
            continue
        if seconds > 0:
            return min(seconds, config.RETRY_AFTER_MAX_S)
    return None


class _EmptyResponse(Exception):
    """A response with no choices: treated like a retryable server error."""


class LLM:
    """Shared by all task threads (the OpenAI client is thread-safe)."""

    def __init__(self, ledger, client=None, sleep=time.sleep, clock=time.monotonic):
        if client is None:
            import openai
            client = openai.OpenAI(base_url=os.environ["CS2680_BASE_URL"],
                                   api_key=os.environ["CS2680_API_KEY"], max_retries=0)
        self._client = client
        self._ledger = ledger
        self._sleep = sleep
        self._clock = clock
        self._lock = threading.Lock()
        self.last_trouble = None   # clock() of the latest retryable error, from any task

    def in_trouble(self, window_s=None):
        window_s = config.API_TROUBLE_WINDOW_S if window_s is None else window_s
        with self._lock:
            last = self.last_trouble
        return last is not None and self._clock() - last < window_s

    def complete(self, *, k, iteration, logger, model, messages, tools, deadline,
                 max_tokens=None, extra_body=None, prompt_estimate=0):
        """One model call for task k's iteration. deadline is a clock() value.

        prompt_estimate: the prompt size in tokens (the previous call's prompt_tokens plus what
        was appended since), used only to charge a timed-out request in the ledger.
        Returns a Completion; raises ContextOverflow, BudgetExhausted or ApiError.
        """
        max_tokens = config.MAX_TOKENS if max_tokens is None else max_tokens
        extra_body = config.EXTRA_BODY if extra_body is None else extra_body
        attempts, timeouts, backoff_total = 0, 0, 0.0
        context_retried = False
        while True:
            timeout = min(config.REQUEST_TIMEOUT_S, deadline - self._clock() - 30)
            if timeout < config.MIN_REQUEST_S:
                raise BudgetExhausted(f"only {max(0, int(timeout + 30))} s left before the "
                                      "task deadline; no model call started")
            kwargs = {"model": model, "messages": messages, "timeout": timeout}
            if tools:
                kwargs["tools"] = tools
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if extra_body:
                kwargs["extra_body"] = extra_body
            attempts += 1
            started = self._clock()
            try:
                response = self._client.chat.completions.create(**kwargs)
                choices = getattr(response, "choices", None)
                if not choices:
                    # Billed if it carried usage; not an iteration of its own in the trace.
                    if getattr(response, "usage", None) is not None:
                        self._ledger.record_call(k, iteration, model, response.usage,
                                                 empty_response=True,
                                                 model_s=round(self._clock() - started, 2))
                    raise _EmptyResponse("the response has no choices")
            except Exception as exc:
                status = status_of(exc)
                if status in (400, 413) and _CONTEXT_PHRASES.search(error_text(exc)):
                    if max_tokens and max_tokens > config.CONTEXT_RETRY_MAX_TOKENS \
                            and not context_retried:
                        context_retried = True
                        max_tokens = config.CONTEXT_RETRY_MAX_TOKENS
                        self._log_retry(k, iteration, logger, exc, 0.0, attempts)
                        continue
                    raise ContextOverflow(describe(exc)) from None
                # A ValueError here is a 200 whose body is not valid JSON (the SDK's json()).
                retryable = (isinstance(exc, (_EmptyResponse, ValueError))
                             or is_connection_error(exc) or status in RETRY_STATUS
                             or (status is not None and status >= 500))
                if not retryable:
                    raise ApiError(describe(exc)) from None
                # A timeout we shortened ourselves near the deadline says nothing about the API.
                if not (is_timeout(exc) and timeout < config.REQUEST_TIMEOUT_S):
                    with self._lock:
                        self.last_trouble = self._clock()
                if is_timeout(exc):
                    timeouts += 1
                    self._ledger.charge_estimate(
                        k, iteration, model, prompt_estimate,
                        max_tokens or config.TIMEOUT_COMPLETION_ESTIMATE,
                        why=f"request timed out after {int(self._clock() - started)} s")
                    if timeouts > config.API_MAX_TIMEOUT_RETRIES:
                        raise ApiError(f"the request timed out {timeouts} times: "
                                       f"{describe(exc)}") from None
                if attempts >= config.API_MAX_ATTEMPTS:
                    raise ApiError(f"gave up after {attempts} attempts: {describe(exc)}") from None
                backoff = self._backoff_s(attempts, exc)
                if self._clock() + backoff > deadline - config.WRAP_RESERVE_S:
                    raise BudgetExhausted(f"the API asks to wait {backoff:.0f} s, past the task "
                                          f"deadline: {describe(exc)}") from None
                self._log_retry(k, iteration, logger, exc, backoff, attempts)
                self._sleep(backoff)
                backoff_total += backoff
                continue

            model_s = round(self._clock() - started, 2)
            choice = response.choices[0]
            message = getattr(choice, "message", None)
            finish_reason = getattr(choice, "finish_reason", None)
            tool_calls = getattr(message, "tool_calls", None) or []
            reasoning = getattr(message, "reasoning_content", None) or ""
            usage = getattr(response, "usage", None)
            row = self._ledger.record_call(
                k, iteration, model, usage, finish_reason=finish_reason,
                n_tool_calls=len(tool_calls), reasoning_chars=len(reasoning), model_s=model_s,
                attempts=attempts, backoff_s=round(backoff_total, 2))
            if logger is not None:
                logger.api_request(iteration, usage_field(usage, "prompt_tokens"),
                                   usage_field(usage, "completion_tokens"),
                                   usage_field(usage, "total_tokens"), model)
            return Completion(response, message, finish_reason, row, model_s, attempts,
                              round(backoff_total, 2))

    def _log_retry(self, k, iteration, logger, exc, backoff, attempts):
        error = describe(exc)
        if logger is not None:
            logger.api_retry(iteration, error, backoff)
        self._ledger.write("retry", k=k, iter=iteration, attempt=attempts, status=status_of(exc),
                           error=error, backoff_s=backoff)

    def _backoff_s(self, attempt, exc):
        """At least what the server asked for (retry_after), and at least our own exponential
        backoff with jitter, so a hint of 1 s cannot use up the attempts in seconds."""
        delay = min(config.BACKOFF_MAX_S, config.BACKOFF_BASE_S * 2 ** (attempt - 1))
        delay *= random.uniform(0.75, 1.25)
        hinted = retry_after_s(exc)
        return round(max(delay, hinted) if hinted is not None else delay, 2)
