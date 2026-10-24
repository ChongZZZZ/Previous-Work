"""The message list sent with every request: append-only, from the first request to the last.

Every request re-sends the whole list, and the API caches the longest prefix it has seen
before (PHASE0_FINDINGS.md 2c). Cached input costs 20x less than fresh input, so a message,
once sent, is never changed, reordered or removed: it is stored exactly as sent, and later
requests only add to the end. Output is shaped when it enters (src/tools.py). A nudge after a
reply without a tool call is a new user message; budget notes (the wrap-up) are appended to the
last message not yet sent (see below). Phase 1 has no compaction or masking at all; whether Phase 2
needs it is decided from the prompt sizes this run logs.

Assistant messages are rebuilt from their content and tool calls only: the model's reasoning
(reasoning_content) is not sent back. The probe of 2026-10-10 found that the API ignores it
anyway (prompt tokens unchanged); config.REASONING_PASSBACK switches it on.

Harness notes (the wrap-up) are never sent as a new user message: the probe showed that a new
user turn makes the server re-render the assistant turns before it, so the cached prefix ends
at the previous user message and those turns are paid again (full5 run: 5 such drops, 7.5% of
the $). A note is appended to the last message instead, as long as that message has not been
sent yet (normally the last tool result), which keeps every request a prefix of the next.

Messages are written to the task's transcript (src/ledger.py) when they are sent, plus the
assistant message with its tool calls right after it arrives, so it is on disk before any of
its tools runs.
"""
from src import config

CHARS_PER_TOKEN = 3.5


class Conversation:
    def __init__(self, system_prompt, task_message, ledger=None, k=None, kind=""):
        """kind names the transcript file of a retry's conversation (<k>.<kind>.jsonl)."""
        self._ledger = ledger
        self._k = k
        self._kind = kind
        self.messages = []
        self._chars_since = 0          # added since the last response reported prompt_tokens
        self.last_prompt_tokens = None
        self._flushed = 0              # messages[:_flushed] are in the transcript (and frozen)
        self._append({"role": "system", "content": system_prompt})
        self._append({"role": "user", "content": task_message})

    def add_assistant(self, content, tool_calls=(), reasoning=None):
        """tool_calls: (id, name, raw arguments) for each call the model made. reasoning is
        stored only if config.REASONING_PASSBACK (it is logged on the side either way)."""
        message = {"role": "assistant", "content": content or ""}
        if reasoning and config.REASONING_PASSBACK:
            message["reasoning_content"] = reasoning
        if tool_calls:
            message["tool_calls"] = [
                {"id": call_id, "type": "function",
                 "function": {"name": name, "arguments": arguments or "{}"}}
                for call_id, name, arguments in tool_calls]
        self._append(message)

    def add_tool_result(self, call_id, text):
        self._append({"role": "tool", "tool_call_id": call_id, "content": text})

    def add_user(self, text):
        self._append({"role": "user", "content": text})

    def add_note(self, text):
        """A harness note for the model: appended to the last message if it is a tool result or a
        user message not yet sent; otherwise a new user message. Returns where it went."""
        last = self.messages[-1] if self.messages else None
        if last is not None and len(self.messages) > self._flushed and last["role"] in ("tool", "user"):
            self.messages[-1] = dict(last, content=(last.get("content") or "") + "\n\n" + text)
            self._chars_since += len(text) + 2
            return f"appended_to_{last['role']}"
        self.add_user(text)
        return "user_message"

    def retract_last(self):
        """Drop the last message when the request that carried it was never answered (the
        compaction notes, change 5): the next request is then a prefix of what was sent before
        it, so the cache is untouched. The transcript keeps a line saying what was retracted."""
        if not self.messages:
            return None
        message = self.messages.pop()
        self._chars_since = max(0, self._chars_since - _size(message))
        if self._flushed > len(self.messages):
            self._flushed = len(self.messages)
            if self._ledger is not None:
                self._ledger.transcript(self._k, {"retracted": message.get("role"),
                                                  "content": (message.get("content") or "")[:200]},
                                        kind=self._kind)
        return message

    def flush(self):
        """Write the messages not yet in the transcript; after this they are never changed."""
        for message in self.messages[self._flushed:]:
            if self._ledger is not None:
                self._ledger.transcript(self._k, message, kind=self._kind)
        self._flushed = len(self.messages)

    def record_prompt_tokens(self, prompt_tokens):
        if prompt_tokens:
            self.last_prompt_tokens = prompt_tokens
            self._chars_since = 0

    def estimated_tokens(self):
        """The next request's prompt size: the last reported one plus what was added since."""
        if self.last_prompt_tokens is None:
            return int(sum(map(_size, self.messages)) / CHARS_PER_TOKEN)
        return int(self.last_prompt_tokens + self._chars_since / CHARS_PER_TOKEN)

    def _append(self, message):
        self.messages.append(message)
        self._chars_since += _size(message)


def _size(message):
    size = len(message.get("content") or "")
    for call in message.get("tool_calls", ()):
        size += len(call["function"]["arguments"] or "")
    return size
