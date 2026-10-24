"""The tools the model can call, run in the task's sandbox: bash, view, str_replace, create
and finish (PHASE1_NOTES.md, "Tools").

SandboxTools.execute(name, raw_arguments) returns a ToolResult and never raises:
  * text is exactly what the model is sent and what the trace records;
  * is_error means the call itself failed (bad arguments, refused, not applied, sandbox
    unreachable). A command that ran and exited non-zero is an ordinary result;
  * finished is True only when finish() ends the task;
  * stop names a reason the task must end now (cap_time, sandbox_dead), else None;
  * meta holds numbers for the ledger (seconds, sizes, truncation, refusals).

TOOL_SCHEMAS is a constant: it is sent with every request, right after the system prompt, so
its bytes must never change within a run (prompt caching).

Output is shaped when it enters the context and never rewritten later (the context is
append-only): bash output is cleaned, and above BASH_WHOLE cut to a head and a tail, with the
full cleaned text saved under /work/out/ so nothing is lost. File contents in view are never
compressed, only paged, because edit anchors are copied from them. After an applied edit, one
fast parser chosen by the file's extension checks the file and its verdict joins the echo
(PHASE2_NOTES.md, change 6).
"""
import collections
import difflib
import json
import os
import re
import shlex
import time

from src import config
from src.sandbox import SandboxError, SandboxPathError
from src.workspace import Workspace, looks_like_test, test_reason

ToolResult = collections.namedtuple("ToolResult", "text is_error finished stop meta")


def _tool(name, description, properties, required):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required}}}


TOOL_SCHEMAS = [
    _tool("bash",
          "Run a bash command at the repository root and return its exit code and output "
          "(stdout and stderr together). Each call is a fresh non-interactive shell without "
          "stdin; only files carry over between calls. There is no network. Long output is cut "
          "to its start and end, and saved in full under /work/out/. A command is stopped after "
          "`timeout` seconds. Git commands that change the repository state (add, commit, stash, "
          "reset, checkout, restore, clean, ...) are refused, because changes they move out of "
          "the working tree are missing from the patch. A background job must redirect its "
          "output to a file under /work; it is not stopped for you.",
          {"command": {"type": "string", "description": "The command to run."},
           "timeout": {"type": "integer", "description":
                       f"Seconds before the command and everything it started are stopped "
                       f"(default {config.BASH_DEFAULT_TIMEOUT_S}, "
                       f"maximum {config.BASH_MAX_TIMEOUT_S})."}},
          ["command"]),
    _tool("view",
          "Show lines of text files, with line numbers. Pass several ranges to read several "
          "files or regions in one call. Paths are relative to the repository root, or absolute "
          f"(installed packages too). A range without `end` shows {config.VIEW_DEFAULT_LINES} "
          f"lines; one call shows at most {config.VIEW_MAX[0]} lines and "
          f"{config.VIEW_MAX[1]:,} characters in total.",
          {"ranges": {"type": "array", "description": "The files and line ranges to show.",
                      "items": {"type": "object", "properties": {
                          "path": {"type": "string"},
                          "start": {"type": "integer", "description": "First line, from 1 (default 1)."},
                          "end": {"type": "integer", "description":
                                  "Last line, inclusive; -1 for as far as the limit allows."}},
                          "required": ["path"]}}},
          ["ranges"]),
    _tool("str_replace",
          "Edit an existing file by replacing exact text. Each edit's `old` must occur exactly "
          "once in the file, with the same whitespace and indentation: copy it from view output "
          "without the line-number prefix, with enough surrounding lines to be unique. All edits "
          "of one call are matched against the file as it was before the call, must not "
          "overlap, and are applied together or not at all. Existing test files cannot be edited.",
          {"path": {"type": "string", "description": "The file to edit."},
           "edits": {"type": "array", "description": "The replacements to make.",
                     "items": {"type": "object", "properties": {
                         "old": {"type": "string", "description": "The exact text to replace."},
                         "new": {"type": "string", "description": "The text to put in its place."}},
                         "required": ["old", "new"]}}},
          ["path", "edits"]),
    _tool("create",
          "Create a new file with the given content. The file must not exist yet (edit existing "
          "files with str_replace). A new file inside the repository becomes part of your patch "
          "(a new test file is removed from it at the end), so put scratch files under "
          "/work/scratch.",
          {"path": {"type": "string", "description": "The file to create."},
           "content": {"type": "string", "description": "The full content of the file."}},
          ["path", "content"]),
    _tool("finish",
          "Finish the task once the fix is complete and verified, with a short summary of what "
          "you changed and how you checked it. If your patch would be empty, adds files the task's "
          "Interface does not name, or changes existing test files, you are first shown what it "
          "contains; then call finish again.",
          {"summary": {"type": "string", "description": "What you changed and how you checked it."}},
          ["summary"]),
]
TOOL_NAMES = [tool["function"]["name"] for tool in TOOL_SCHEMAS]
_PARAMETERS = {tool["function"]["name"]: tool["function"]["parameters"] for tool in TOOL_SCHEMAS}


class ToolError(Exception):
    """A call that cannot be carried out; its message is what the model is sent."""

    def __init__(self, message, **meta):
        super().__init__(message)
        self.meta = meta


# --- arguments ------------------------------------------------------------------------

def parse_arguments(raw):
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise ToolError(f"error: the arguments are not valid JSON ({exc}). Send them again as "
                        "one JSON object.") from None
    if not isinstance(value, dict):
        raise ToolError("error: the arguments must be a JSON object.")
    return value


def _lenient(name, args):
    """Accept the usual near-misses instead of spending a turn on them."""
    args = dict(args)
    if name == "view" and "ranges" not in args and "path" in args:
        args["ranges"] = [{key: args.pop(key) for key in ("path", "start", "end") if key in args}]
    if name == "str_replace" and "edits" not in args:
        old = args.pop("old", args.pop("old_string", None))
        new = args.pop("new", args.pop("new_string", None))
        if old is not None or new is not None:
            args["edits"] = [{"old": old, "new": new}]
    for key in ("ranges", "edits"):
        if isinstance(args.get(key), str):          # an array sent as a JSON string
            try:
                args[key] = json.loads(args[key])
            except ValueError as exc:
                raise ToolError(f"error: {key} must be a JSON array, but a string was received, and "
                                f"that string is not valid JSON ({exc}). Send the array itself, not "
                                "a string holding it.", error_kind="schema") from None
    if name == "str_replace" and isinstance(args.get("edits"), list):
        args["edits"] = [{"old": e.get("old", e.get("old_string")),
                          "new": e.get("new", e.get("new_string"))} if isinstance(e, dict) else e
                         for e in args["edits"]]
    return args


def _check(value, spec, where):
    kind = spec["type"]
    if kind == "integer":
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            value = int(value)
        elif isinstance(value, float) and value.is_integer():
            value = int(value)
        if not isinstance(value, int) or isinstance(value, bool):
            raise ToolError(f"error: {where} must be an integer.")
        return value
    if kind == "string":
        if not isinstance(value, str):
            raise ToolError(f"error: {where} must be a string.")
        return value
    if kind == "array":
        if not isinstance(value, list) or not value:
            raise ToolError(f"error: {where} must be a non-empty array.")
        return [_check(item, spec["items"], f"{where}[{i}]") for i, item in enumerate(value)]
    if kind == "object":
        if not isinstance(value, dict):
            raise ToolError(f"error: {where} must be an object.")
        clean = {}
        for key, prop in spec["properties"].items():
            if value.get(key) is not None:
                clean[key] = _check(value[key], prop, f"{where}.{key}" if where else key)
        missing = [key for key in spec.get("required", []) if key not in clean]
        if missing:
            prefix = f"{where}: " if where else ""
            raise ToolError(f"error: {prefix}missing required argument(s): {', '.join(missing)}.")
        return clean
    return value


def validate(name, args):
    return _check(_lenient(name, args), _PARAMETERS[name], "")


# --- refusing git commands that would take changes out of the patch --------------------------

_GIT_STATE_COMMANDS = ["add", "commit", "stash", "reset", "checkout", "restore", "clean", "rm",
                       "mv", "switch", "rebase", "merge", "cherry-pick", "revert", "am", "pull",
                       "update-index", "read-tree"]
# `git` where a command starts (not inside a longer word), then any global options, then one of
# the subcommands above.
_GIT_STATE = re.compile(
    r"(?:^|[\s;&|()`])git"
    r"(?:\s+(?:-C|-c|--git-dir|--work-tree)(?:\s+|=)\S+|\s+-{1,2}[\w-]+)*"
    r"\s+(" + "|".join(map(re.escape, _GIT_STATE_COMMANDS)) + r")(?=$|[\s;&|)`])")
_GIT_APPLY_INDEX = re.compile(r"(?:^|[\s;&|()`])git\s+apply\b[^;&|\n]*\s--(?:index|cached)\b")
# Commands that list git's objects one by one, reachable or not: objects that HEAD's history does
# not reach are not part of the task (an integrity guard, as the course notes recommend).
_GIT_OBJECT_DUMP = re.compile(
    r"(?:^|[\s;&|()`])git(?:\s+(?:-C|-c|--git-dir|--work-tree)(?:\s+|=)\S+|\s+-{1,2}[\w-]+)*"
    r"\s+(fsck|verify-pack|show-index|unpack-objects|lost-found"
    r"|cat-file\b[^;&|\n]*--batch-all-objects)")


def refused_git_command(command):
    """(rule, git subcommand) if command would change the repository state or dump objects."""
    match = _GIT_STATE.search(command)
    if match:
        return "git_state", match.group(1)
    if _GIT_APPLY_INDEX.search(command):
        return "git_state", "apply --index"
    match = _GIT_OBJECT_DUMP.search(command)
    if match:
        return "git_objects", match.group(1).split()[0]
    return None


# --- shaping command output ---------------------------------------------------------------

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]")
SANDBOX_CUT_MARK = "[... sandbox cut "

# The real exit status, and the exit status of every stage of the last pipeline, come from an EXIT
# trap: a function defined on the command's first line, before the command, so nothing follows the
# command text (an open heredoc or a trailing backslash parses as in plain bash) and line numbers do
# not move. The function reads $? and PIPESTATUS before anything resets them and writes them to a
# private file (A3_STATUS_FILE, under /work), never to the command's own output, so `exec > file`
# cannot carry it into a file. The outer shell appends the file's content as one status line after
# bash exits, and the harness removes that line. A command that sets its own EXIT trap or replaces
# the shell with exec leaves no status, and is reported by its plain exit status. PIPESTATUS is not
# updated by if/while/for/case, `!` or background jobs, so it is only used when the last pipeline has
# two or more stages and its last stage matches $?.
STATUS_MARK = "__A3_STATUS__"
STATUS_FN = ('__a3_status() { { __a3_rc=$? __a3_ps=("${PIPESTATUS[@]}"); set +x +v; } 2>/dev/null; '
             'printf -v __a3_s " %s" "${__a3_ps[@]}"; '
             'printf "%s |%s\\n" "$__a3_rc" "$__a3_s" > "$A3_STATUS_FILE" 2>/dev/null; }')
TIMEOUT_KILLED = {124, 137}       # coreutils `timeout`: 124 on its signal, 137 with -s KILL / -k
SIGKILL = 137
EARLY_STOP = {141, 120}           # an early stage stopped because a later one (head) stopped
                                  # reading: SIGPIPE, or Python's exit on a broken pipe
# `timeout [its own options] DURATION COMMAND` as a command word (also after a path or inside $(...)
# and quotes); the duration must be followed by a space, so `-k timeout 2>&1` or `grep timeout -A 3`
# are not read as a timeout.
_INNER_TIMEOUT = re.compile(
    r"(?:^|[\s;&|(`/\"'$])timeout\s+"
    r"(?:(?:(?:-k|--kill-after|-s|--signal)(?:=|\s+)\S+|--preserve-status|--foreground|-v|--verbose)\s+)*"
    r"(\d+(?:\.\d+)?)([smhd]?)(?=\s)")
_COMMENT = re.compile(r"(?:^|(?<=\s))#[^\n]*", re.MULTILINE)


def split_status(raw):
    """(output without the status line, exit status or None, [pipeline statuses])."""
    at = raw.rfind("\n" + STATUS_MARK + " ")
    if at < 0:
        return raw, None, []
    end = raw.find("\n", at + 1)
    line = raw[at + 1 + len(STATUS_MARK):end if end >= 0 else len(raw)]
    head, _, tail = line.partition("|")
    try:
        rc = int(head.strip())
        stages = [int(f) for f in tail.split()]
    except ValueError:
        return raw, None, []
    out = raw[:at]
    body = out.rstrip("\n")
    last_nl = body.rfind("\n")
    if body[last_nl + 1:].lstrip("+ ") == "__a3_status":     # set -x / set -v tracing the trap
        out = body[:last_nl + 1]
    return out + (raw[end + 1:] if end >= 0 else ""), rc, stages


def inner_timeouts(command):
    """Seconds of every coreutils `timeout DURATION` in the command (comments skipped; s, m, h, d
    suffixes)."""
    scale = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}
    code = _COMMENT.sub(" ", command) + " "
    return [float(n) * scale[u] for n, u in _INNER_TIMEOUT.findall(code)]


def clean_lines(text, line_chars=None):
    """Output as lines: ANSI codes removed, carriage-return redraws (progress bars) reduced to
    what was left on screen, and lines longer than line_chars clipped (0: never)."""
    line_chars = config.BASH_LINE_CHARS if line_chars is None else line_chars
    lines = []
    for line in _ANSI.sub("", text).split("\n"):
        if line.endswith("\r"):
            line = line[:-1]
        if "\r" in line:
            line = line.rsplit("\r", 1)[-1]
        if line_chars and len(line) > line_chars:
            line = f"{line[:line_chars]}…[+{len(line) - line_chars} chars]"
        lines.append(line)
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _size(lines):
    return sum(len(line) + 1 for line in lines)


def shape_lines(lines, saved_path):
    """(text shown, truncated): the whole output, or a head and a tail with a marker between."""
    whole_lines, whole_chars = config.BASH_WHOLE
    if len(lines) <= whole_lines and _size(lines) <= whole_chars:
        return "\n".join(lines), False
    head_lines, head_chars = config.BASH_HEAD
    tail_lines, tail_chars = config.BASH_TAIL
    head, size = [], 0
    for line in lines[:head_lines]:
        if head and size + len(line) + 1 > head_chars:
            break
        head.append(line)
        size += len(line) + 1
    tail, size = [], 0
    for line in reversed(lines[len(head):]):
        if len(tail) >= tail_lines or (tail and size + len(line) + 1 > tail_chars):
            break
        tail.append(line)
        size += len(line) + 1
    tail.reverse()
    first, last = len(head) + 1, len(lines) - len(tail)
    omitted = _size(lines[len(head):len(lines) - len(tail)])
    where = (f"full output: {saved_path}; grep -n or view it, or narrow the command"
             if saved_path else "the full output could not be saved; narrow the command")
    marker = f"[... lines {first}-{last} omitted ({omitted:,} chars); {where}]"
    return "\n".join(head + [marker] + tail), True


# --- paths ------------------------------------------------------------------------------

def _inside(path, root):
    return path == root or path.startswith(root.rstrip("/") + "/")


def _match_lines(text, needle):
    found, at = [], text.find(needle)
    while at != -1:
        found.append(text.count("\n", 0, at) + 1)
        at = text.find(needle, at + len(needle))
    return found


def _no_match(text, old):
    squash = " ".join(old.split())
    if squash and squash in " ".join(text.split()):
        return ("it matches only when whitespace is ignored: copy the exact indentation and "
                "spacing from view output (without the line-number prefix)")
    lines = [line.strip() for line in text.split("\n")]
    first = next((line.strip() for line in old.split("\n") if line.strip()), "")
    close = difflib.get_close_matches(first, lines, n=3, cutoff=0.6) if first else []
    if close:
        return "not found; the most similar lines are:\n" + "\n".join(
            f"    {lines.index(c) + 1}: {c[:200]}" for c in close)
    return "not found; view the file again to see its current content"


def _unencodable(text):
    """A message if text cannot be written as UTF-8 (a lone surrogate from an over-escaped
    JSON string), else None."""
    try:
        text.encode("utf-8")
        return None
    except UnicodeEncodeError as exc:
        line = text.count("\n", 0, exc.start) + 1
        return (f"the text contains {text[exc.start]!r} at line {line}, half of a surrogate pair, "
                "which cannot be stored in a file. Write the character itself, or an escape "
                "sequence in the file's own language.")


def _numbered(lines, first, last, line_chars=None):
    line_chars = line_chars or config.VIEW_LINE_CHARS
    rows = []
    for n in range(max(1, first), min(len(lines), last) + 1):
        line = lines[n - 1].rstrip("\r")
        if len(line) > line_chars:
            line = (f"{line[:line_chars]} [line truncated: +{len(line) - line_chars} chars; "
                    "not usable as a str_replace anchor]")
        rows.append(f"{n:6d}\t{line}")
    return rows


# --- the syntax check after an edit (change 6) ---------------------------------------------

# One fast, per-file parser by file extension, run in the sandbox after an applied edit
# (Lecture 4 research: SWE-agent's lint-gated edit; Lecture 7 research: syntax errors are a top
# SWE-bench Pro failure). Each entry: the label shown in the echo, the programs that can run it
# (the first one `command -v` finds is used), and the check as a shell command with $1 = the
# program and $2 = the file. A check parses the file and nothing else: no package build, no
# formatting, no file written into the tree. The table is generic by extension and knows
# nothing about any repository.
_PY_AST = """\
import ast, sys
p = sys.argv[1]
try:
    ast.parse(open(p, 'rb').read(), p)
except SyntaxError as e:
    print('%s: %s (line %s)' % (type(e).__name__, e.msg, e.lineno))
    if e.text:
        print('    ' + e.text.rstrip('\\n'))
        if e.offset:
            print('    ' + ' ' * (e.offset - 1) + '^')
    sys.exit(1)
except Exception as e:
    print('%s: %s' % (type(e).__name__, e))
    sys.exit(1)
"""
_PYTHON = ("python3", "python")
_NODE_CHECK = ("node --check", ("node",), '"$1" --check "$2" 2>&1')
SYNTAX_CHECKERS = {
    ".py": ("python3 ast", _PYTHON, f'"$1" -c {shlex.quote(_PY_AST)} "$2" 2>&1'),
    ".go": ("gofmt -e", ("gofmt",), '"$1" -e "$2" 2>&1 >/dev/null'),
    ".js": _NODE_CHECK, ".mjs": _NODE_CHECK, ".cjs": _NODE_CHECK,
    ".sh": ("bash -n", ("bash",), '"$1" -n "$2" 2>&1'),
    ".bash": ("bash -n", ("bash",), '"$1" -n "$2" 2>&1'),
}
# No .json entry: JSON files with comments or trailing commas (tsconfig-style) are common and
# would fail a strict parser; no .ts, .tsx or .jsx either (no fast per-file checker).
NO_TOOL_MARK = "__A3_NO_TOOL__"
# ES module syntax in a file node reads as CommonJS: checked once more as a module.
_ESM_ERROR = re.compile(r"Cannot use import statement outside a module|Unexpected token 'export'"
                        r"|Cannot use 'import\.meta' outside a module")
# What a parser alone cannot judge (JSX, TypeScript in a .js file, module syntax on an old node).
_INCONCLUSIVE = re.compile(r"Unexpected token '<'|Cannot use import statement outside a module"
                           r"|Unexpected token 'export'|Cannot use 'import\.meta'")
# Lines of a checker's output that carry no information about the file.
_CHECK_NOISE = re.compile(r"^(\s+at |Node\.js v\d|\(node:\d+\) \w*Warning|\(Use `node --trace-warnings)")


# --- the tools --------------------------------------------------------------------------

class SandboxTools:
    def __init__(self, sb, workspace=None, deadline=None, clock=time.monotonic, sleep=time.sleep):
        self.sb = sb
        self.workdir = sb.workdir.rstrip("/") or "/"
        self.workspace = workspace or Workspace(sb)
        self.deadline = deadline      # clock() value; the solver moves it at a global wrap-up
        self._clock = clock
        self._sleep = sleep
        self._out_n = 0
        self._sandbox_errors = 0
        self._refused = set()          # (tool, arguments) of calls already refused by a rule
        self._status_n = 0             # numbers the private status file of each bash call
        self._confirmed = set()        # review flags the model has already been asked about
        self._finish_asks = 0
        self.edited = set()            # repository paths changed through str_replace or create
        self._syntax_timeouts = set()  # extensions whose syntax check timed out in this attempt
        self.interface_paths = set()   # repository paths the task's Interface names (set by the solver)
        self._handlers = {"bash": self._bash, "view": self._view,
                          "str_replace": self._str_replace, "create": self._create,
                          "finish": self._finish}

    def execute(self, name, raw_arguments):
        started = self._clock()
        meta, stop, finished, call_key = {}, None, False, None
        try:
            handler = self._handlers.get(name)
            if handler is None:
                raise ToolError(f"error: there is no tool called {name!r}. The tools are: "
                                f"{', '.join(TOOL_NAMES)}.")
            try:
                args = validate(name, parse_arguments(raw_arguments))
            except ToolError as exc:
                exc.meta.setdefault("error_kind", "schema")
                raise
            call_key = (name, json.dumps(args, sort_keys=True, default=str))
            text, is_error, finished, stop, meta = handler(**args)
            self._sandbox_errors = 0
        except ToolError as exc:
            text, is_error, meta = str(exc), True, dict(exc.meta)
            meta.setdefault("error_kind", "refusal" if meta.get("refused_rule") else "other")
            if meta.get("refused_rule") and call_key is not None:
                if call_key in self._refused:
                    text = ("error: refused again by the same rule; this call cannot succeed in "
                            "this form.\n" + text)
                    meta["repeat_refusal"] = True
                self._refused.add(call_key)
        except SandboxError as exc:
            self._sandbox_errors += 1
            text, is_error = (f"error: the sandbox did not answer ({exc}). If this was a command, "
                              "it may or may not have run: check the state before repeating it."), True
            meta = {"sandbox_error": str(exc)[:300], "error_kind": "sandbox"}
            if self._sandbox_errors >= config.SANDBOX_DEAD_AFTER and not self._sandbox_alive():
                stop = "sandbox_dead"
        except Exception as exc:  # a bug must not lose this call's result
            text, is_error = f"error: the {name} tool failed: {type(exc).__name__}: {exc}", True
            meta = {"error_kind": "harness_bug"}
        meta = dict(meta or {}, secs=round(self._clock() - started, 2), shown_chars=len(text))
        if is_error:
            meta.setdefault("error_kind", "other")
        return ToolResult(text, is_error, finished, stop, meta)

    # -- sandbox access with retries -----------------------------------------------------

    def _sandbox_alive(self):
        for attempt in range(2):
            try:
                if self.sb.health().get("root"):
                    return True
            except Exception:  # health() raises raw urllib errors, not SandboxError
                pass
            if attempt == 0:
                self._sleep(5)
        return False

    def _read(self, path):
        for attempt in range(config.SANDBOX_RW_RETRIES + 1):
            try:
                return self.sb.read_text(path)
            except SandboxError:
                if attempt == config.SANDBOX_RW_RETRIES:
                    raise
                self._sleep(1 + attempt)

    def _write(self, path, content):
        for attempt in range(config.SANDBOX_RW_RETRIES + 1):
            try:
                return self.sb.write_text(path, content)
            except SandboxError:
                if attempt == config.SANDBOX_RW_RETRIES:
                    raise
                self._sleep(1 + attempt)

    def _run(self, command, timeout_s=None):
        r = self.sb.exec(command, timeout_s=timeout_s or config.HARNESS_EXEC_TIMEOUT_S)
        return r.get("exit_code"), r.get("output", "")

    def _repo_path(self, path):
        """The path relative to the repository root, or None if it is outside the repository."""
        full = os.path.normpath(path if os.path.isabs(path) else os.path.join(self.workdir, path))
        if not _inside(full, self.workdir):
            return None
        return os.path.relpath(full, self.workdir)

    def _in_roots(self, path):
        full = os.path.normpath(path if os.path.isabs(path) else os.path.join(self.workdir, path))
        return _inside(full, self.workdir) or _inside(full, config.WORK_DIR)

    def _writable(self, path, new_file=False):
        """The repository-relative path (None under /work), or a ToolError saying why not.
        new_file: a new test file may be created; cleanup removes new test files from the patch
        at the end (patch hygiene, as for any reproduction test)."""
        if not path.strip():
            raise ToolError("error: path is empty.")
        if not self._in_roots(path):
            raise ToolError(f"error: {path} is outside the repository ({self.workdir}) and "
                            f"{config.WORK_DIR}; files can only be written there.", error_kind="path")
        rel = self._repo_path(path)
        if rel is not None and (rel == ".git" or rel.startswith(".git/")):
            raise ToolError("error: files under .git cannot be changed.")
        if rel is not None and looks_like_test(rel) and not new_file:
            raise ToolError(
                f"error: {rel} is a test file ({test_reason(rel)}), and existing test files may not "
                "be changed; a test "
                "file changed any other way is put back at the end. The fix has to be in the "
                f"source code; put your own checks under {config.WORK_DIR}/scratch.",
                refused_rule="test_file")
        return rel

    # -- bash ---------------------------------------------------------------------------

    def _bash(self, command, timeout=None):
        refused = refused_git_command(command)
        if refused and refused[0] == "git_state":
            raise ToolError(
                f"error: refused to run `git {refused[1]}`: it changes the repository state, and "
                "changes that are staged, committed or stashed are missing from the patch. Leave "
                "your changes as unstaged edits. To see the original version of a file use "
                "`git diff` or `git show HEAD:<path>`.", refused_rule="git_state")
        if refused:
            raise ToolError(
                f"error: refused to run `git {refused[1]}`: listing git's stored objects is not "
                "part of this task. Work from the code at HEAD; `git log`, `git show` and "
                "`git diff` on HEAD's history are fine.", refused_rule="git_objects")
        requested = config.BASH_DEFAULT_TIMEOUT_S if timeout is None else \
            max(1, min(timeout, config.BASH_MAX_TIMEOUT_S))
        effective = requested
        if self.deadline is not None:
            left = int(self.deadline - self._clock() - config.WRAP_RESERVE_S)
            if left < config.BASH_MIN_TIMEOUT_S:
                return ("[not run: the task is out of time]", True, False, "cap_time",
                        {"timeout": max(0, left), "not_run": "cap_time", "error_kind": "not_run"})
            effective = min(requested, left)
        meta = {"timeout": effective}
        exports = " ".join(f"{key}={shlex.quote(value)}" for key, value in config.BASH_EXPORTS)
        self._status_n += 1
        status_file = f"{config.WORK_DIR}/.a3/status_{self._status_n}"
        script = f"{STATUS_FN}; trap __a3_status EXIT; {command}"
        q = shlex.quote(status_file)
        wrapper = (f"export {exports} A3_STATUS_FILE={q}; mkdir -p {shlex.quote(config.WORK_DIR + '/.a3')}; "
                   f"rm -f {q}; bash -c {shlex.quote(script)}; __a3_rc=$?; "
                   f"if [ -s {q} ]; then printf '\\n{STATUS_MARK} '; cat {q}; rm -f {q}; fi; "
                   "exit $__a3_rc")
        started = self._clock()
        r = self.sb.exec(wrapper, timeout_s=effective)
        elapsed = self._clock() - started
        raw, status, stages = split_status(r.get("output", "") or "")
        exit_code, timed_out = r.get("exit_code"), bool(r.get("timed_out"))
        full = clean_lines(raw, line_chars=0)
        lines = clean_lines(raw)
        saved = None
        whole_lines, whole_chars = config.BASH_WHOLE
        if len(lines) > whole_lines or _size(lines) > whole_chars:
            self._out_n += 1
            saved = f"{config.OUT_DIR}/{self._out_n}.log"
            try:
                self._write(saved, "\n".join(full) + "\n")   # same line numbers, nothing clipped
            except (SandboxError, SandboxPathError):
                saved = None
        body, truncated = shape_lines(lines, saved)
        if timed_out:
            header = (f"timed out after {effective} s (the command and everything it started "
                      "were stopped); narrow it (one package, one test) or pass a larger timeout "
                      f"(max {config.BASH_MAX_TIMEOUT_S})")
        else:
            header = (f"exit={exit_code} | {elapsed:.1f} s | {len(lines)} lines, "
                      f"{_size(lines):,} chars")
        notes = []
        # Stage statuses are trusted only for a real pipeline that ended the command.
        pipeline = stages if len(stages) >= 2 and stages[-1] == exit_code else []
        hidden = [s for s in pipeline[:-1] if s != 0 and s not in EARLY_STOP]
        if hidden:
            notes.append(f"note: the stages of the last pipeline exited with "
                         f"{' '.join(map(str, pipeline))}; the exit shown is the last stage's. A "
                         "non-zero earlier stage can mean an error, or for example no match (grep) or "
                         "files that differ (diff).")
        limits = [limit for limit in inner_timeouts(command) if limit > 0]   # 0 = no timeout
        codes = set(pipeline) | {exit_code}
        reached = [limit for limit in limits if elapsed >= limit - 1.0]
        killed_inner = not timed_out and bool(reached) and bool(TIMEOUT_KILLED & codes)
        ran_to_limit = bool(not timed_out and not killed_inner and any(
            limit - 1.0 <= elapsed <= limit + max(2.0, 0.1 * limit) for limit in limits))
        if killed_inner:
            notes.append("note: a `timeout` in the command stopped it (status 124 or 137), so it did "
                         "not finish and its output is incomplete.")
        elif ran_to_limit:
            limit = min(limits, key=lambda value: abs(elapsed - value))
            notes.append(f"note: the command ran for {elapsed:.0f} s, as long as the `timeout "
                         f"{limit:g}` in it allows: that timeout probably stopped part of it, so its "
                         "output may be incomplete even though the exit status hides it.")
        elif not timed_out and SIGKILL in codes:
            notes.append("note: status 137 means a process was killed with SIGKILL"
                         + (" before any `timeout` in the command was reached" if limits else "")
                         + " (for example when memory ran out).")
        if r.get("pipe_held"):
            notes.append("note: a background process still held the output when the command ended, "
                         "so later output was not collected; redirect a background job's output to "
                         "a file under /work.")
        if effective < requested:
            notes.append(f"note: the timeout was cut to {effective} s because the task is near its "
                         "time limit; wrap up.")
        if SANDBOX_CUT_MARK in raw:
            notes.append("note: the output was over 1 MB; its middle was dropped before it reached "
                         "the harness, so the saved log is cut too.")
        clean_success = (exit_code == 0 and not timed_out and not hidden and not killed_inner
                         and not ran_to_limit)
        if not lines:
            body = "Command ran successfully and printed nothing." if clean_success else "(no output)"
        meta.update(raw_chars=len(raw), truncated=truncated, saved_path=saved, exit=exit_code,
                    timed_out=timed_out, timeout_clipped=effective < requested,
                    elapsed=round(elapsed, 2), pipestatus=stages or None, trap_status=status,
                    inner_timeout="killed" if killed_inner else "suspected" if ran_to_limit else None)
        return ("\n".join([header] + notes + [body]), False, False, None, meta)

    # -- view ---------------------------------------------------------------------------

    def _view(self, ranges):
        max_lines, max_chars = config.VIEW_MAX
        parts, errors, lines_left, chars_left = [], 0, max_lines, max_chars
        shown, cut, continues = 0, 0, 0
        for spec in ranges:
            path = spec["path"]
            if lines_left <= 0 or chars_left <= 0:
                parts.append(f"[{path}: not shown, the output limit of one view call was reached; "
                             "view it in another call]")
                continue
            start = max(1, spec.get("start") or 1)
            end = spec.get("end")
            if end is not None and end < start:     # e.g. end=-1, "to the end of the file"
                end = start + max_lines - 1
            wanted = start + config.VIEW_DEFAULT_LINES - 1 if end is None else end
            last = min(wanted, start + lines_left - 1)
            try:
                lines, total = self._read_range(path, start, last)
            except ToolError as exc:
                parts.append(str(exc))
                errors += 1
                continue
            if total == 0:
                parts.append(f"{path}: empty file")
                continue
            if start > total:
                parts.append(f"error: start {start} is past the end of {path} ({total} lines).")
                errors += 1
                continue
            rows = []
            for row in _numbered(lines, start, min(last, total)):
                if (rows or chars_left < max_chars) and len(row) + 1 > chars_left:
                    break
                rows.append(row)
                chars_left -= len(row) + 1
            if not rows:
                parts.append(f"[{path}: not shown, the output limit of one view call was "
                             "reached; view it in another call]")
                chars_left = 0
                continue
            lines_left -= len(rows)
            shown_last = start + len(rows) - 1
            shown += len(rows)
            cut += shown_last < min(wanted, total)      # the budget, not the request, ended it
            continues += shown_last < total
            text = f"{path} (lines {start}-{shown_last} of {total})\n" + "\n".join(rows)
            if shown_last < total:
                text += (f'\n[file continues; next: view {{"path": "{path}", '
                         f'"start": {shown_last + 1}}}]')
            parts.append(text)
        return ("\n\n".join(parts), errors == len(ranges), False, None,
                {"ranges": len(ranges), "errors": errors, "lines_shown": shown,
                 "cut_by_harness": cut, "continues": continues})

    def _read_range(self, path, start, last):
        """(all lines of the file, or a list with the lines up to `last`; total lines).
        Files in the repository or /work are read with /read; other absolute paths (installed
        packages, the Go module cache) with a read-only command, since /read is confined."""
        if not path.strip():
            raise ToolError("error: path is empty.")
        if self._in_roots(path):
            try:
                text = self._read(path)
            except SandboxPathError as exc:
                raise ToolError(self._missing(path, exc)) from None
            if "\0" in text[:8000]:
                raise ToolError(f"error: {path} looks like a binary file.")
            lines = text.split("\n")
            if lines and lines[-1] == "":
                lines.pop()
            return lines, len(lines)
        q = shlex.quote(path)
        script = (f"if [ -d {q} ]; then echo __A3_DIR__; elif [ ! -f {q} ]; then echo __A3_NONE__; "
                  f"elif [ \"$(head -c 8000 {q} | wc -c)\" -ne "
                  f"\"$(head -c 8000 {q} | tr -d '\\000' | wc -c)\" ]; then echo __A3_BIN__; "
                  f"else awk 'END {{print NR}}' {q} 2>/dev/null; echo __A3_SEP__; "
                  f"sed -n '{start},{last}p' {q} 2>/dev/null | cut -c1-{config.VIEW_LINE_CHARS + 100}; fi")
        code, out = self._run(f"sh -c {shlex.quote(script)}")
        first = out.split("\n", 1)[0].strip()
        if first == "__A3_DIR__":
            raise ToolError(f"error: {path} is a directory; list it with bash (ls {path}).")
        if first == "__A3_NONE__":
            raise ToolError(f"error: {path} does not exist.")
        if first == "__A3_BIN__":
            raise ToolError(f"error: {path} looks like a binary file.")
        if "__A3_SEP__\n" not in out:
            raise ToolError(f"error: could not read {path}: {out[-300:]}")
        count, body = out.split("__A3_SEP__\n", 1)
        got = body.split("\n")
        if got and got[-1] == "":
            got.pop()
        digits = re.findall(r"\d+", count)
        total = max(int(digits[-1]) if digits else 0, start + len(got) - 1 if got else 0)
        return [""] * (start - 1) + got, total

    def _missing(self, path, exc):
        message = str(exc)
        if "file not found" in message:
            code, _ = self._run(f"test -d {shlex.quote(path)}")
            if code == 0:
                return f"error: {path} is a directory; list it with bash (ls {path})."
            return f"error: {path} does not exist."
        return f"error: {message}"

    # -- str_replace --------------------------------------------------------------------

    def _str_replace(self, path, edits):
        self._writable(path)
        try:
            text = self._read(path)
        except SandboxPathError as exc:
            raise ToolError(self._missing(path, exc) + " To create a new file, use create.",
                            error_kind="missing") from None
        if "\ufffd" in text and not self._fffd_is_literal(path, text):
            raise ToolError(f"error: {path} is not valid UTF-8 text, so it cannot be edited "
                            "safely here; edit it with bash (e.g. perl -pi -e ...).",
                            refused_rule="not_utf8")
        crlf = "\r\n" in text
        spans, problems = [], []
        for i, edit in enumerate(edits):
            old, new = edit["old"], edit["new"]
            if old == "":
                problems.append(f"edit {i}: `old` is empty; give the exact text to replace (to "
                                "create a new file, use create).")
                continue
            if old == new:
                problems.append(f"edit {i}: `old` and `new` are the same, so nothing would change.")
                continue
            if crlf:
                # The file has Windows line endings; the model writes plain \n.
                if old not in text and "\r\n" not in old:
                    old = old.replace("\n", "\r\n")
                new = re.sub(r"(?<!\r)\n", "\r\n", new)
            count = text.count(old)
            if count == 0:
                problems.append(f"edit {i}: {_no_match(text, old)}")
            elif count > 1:
                where = ", ".join(map(str, _match_lines(text, old)[:10]))
                problems.append(f"edit {i}: `old` occurs {count} times (at lines {where}); include "
                                "more of the surrounding lines so that it matches exactly once.")
            else:
                at = text.index(old)
                spans.append((at, at + len(old), new, i))
        spans.sort()
        for (a0, a1, _, ai), (b0, _, _, bi) in zip(spans, spans[1:]):
            if b0 < a1:
                problems.append(f"edits {ai} and {bi} overlap; merge them into one edit.")
        if problems:
            good = sorted(i for _, _, _, i in spans)
            raise ToolError(
                f"error: no edit was applied to {path} (the edits of one call apply together or "
                "not at all).\n" + "\n".join(problems) +
                (f"\nEdits that would have applied: {', '.join(map(str, good))}." if good else ""),
                edit_errors=len(problems), error_kind="match")
        pieces, regions, cursor, shift = [], [], 0, 0
        for begin, end, new, _ in spans:
            pieces.append(text[cursor:begin])
            pieces.append(new)
            regions.append((begin + shift, begin + shift + len(new)))
            shift += len(new) - (end - begin)
            cursor = end
        pieces.append(text[cursor:])
        updated = "".join(pieces)
        bad = _unencodable(updated)
        if bad:
            raise ToolError(f"error: no edit was applied to {path}: {bad}")
        self._write(path, updated)
        rel = self._repo_path(path)
        if rel is not None:
            self.edited.add(rel)
        text = (f"edited {path} ({len(spans)} edit{'s' if len(spans) != 1 else ''}).\n"
                + self._echo(updated, regions))
        line, check = self._syntax_check(path)
        if line:
            text += "\n" + line
        return text, False, False, None, dict({"edits": len(spans)}, **check)

    def _fffd_is_literal(self, path, text):
        """Whether every U+FFFD in the decoded text is really in the file (bytes EF BF BD), so
        nothing was lost when the server decoded it."""
        script = f"LC_ALL=C grep -o -a $'\\xef\\xbf\\xbd' {shlex.quote(path)} | wc -l"
        try:
            _, out = self._run(f"bash -c {shlex.quote(script)}")
        except SandboxError:
            return False
        digits = re.findall(r"\d+", out)
        return bool(digits) and int(digits[-1]) == text.count("\ufffd")

    @staticmethod
    def _echo(text, regions):
        context, max_chars = config.EDIT_ECHO
        lines = text.split("\n")
        if len(lines) > 1 and lines[-1] == "":
            lines.pop()
        windows = []
        for begin, end in regions:
            first = text.count("\n", 0, begin) + 1
            last = first + text.count("\n", begin, end)
            windows.append([max(1, first - context), min(len(lines), last + context)])
        merged = []
        for window in windows:
            if merged and window[0] <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], window[1])
            else:
                merged.append(window)
        out, size = [], 0
        for first, last in merged:
            block = "\n".join(_numbered(lines, first, last))
            if out and size + len(block) > max_chars:
                out.append("[... more changed regions not shown; view the file to see them]")
                break
            if len(block) > max_chars:
                block = block[:max_chars] + "\n[... cut; view the file to see the rest]"
            out.append(block)
            size += len(block)
        return "\n...\n".join(out)

    # -- the syntax check after an edit (change 6) -----------------------------------------

    def _run_check(self, script, timeout_s):
        """The checker's {output, exit_code, timed_out}; separate so that tests can stub it."""
        return self.sb.exec(script, timeout_s=timeout_s)

    def _syntax_check(self, path):
        """(the line for the echo, or None; the ledger's fields) after a file was written: one
        fast parser chosen by the file's extension, run in the sandbox. Never raises: the edit is
        already applied, and a check that cannot run adds no line."""
        if not config.SYNTAX_CHECK:
            return None, {}
        ext = os.path.splitext(path)[1].lower()
        checker = SYNTAX_CHECKERS.get(ext)
        if checker is None:
            return None, {}
        label, programs, check = checker
        rel = self._repo_path(path)
        meta = {"syntax_tool": label, "syntax_path": path if rel is None else rel}
        if ext in self._syntax_timeouts:
            return None, dict(meta, syntax="skipped", syntax_why="timeout")
        timeout = config.SYNTAX_CHECK_TIMEOUT_S
        if self.deadline is not None:
            left = int(self.deadline - self._clock() - config.WRAP_RESERVE_S)
            if left < config.BASH_MIN_TIMEOUT_S:
                return None, dict(meta, syntax="skipped", syntax_why="time")
            timeout = min(timeout, left)
        started = self._clock()
        try:
            outcome, output = self._check_once(programs, check, path, timeout)
            if outcome == "failed" and label == _NODE_CHECK[0] and ext != ".mjs" \
                    and _ESM_ERROR.search(output):
                # ES module syntax in a file node reads as CommonJS (no "type": "module" in the
                # package): once more as a module, on a copy under /work.
                copy = f"{config.WORK_DIR}/.a3/syntax_check.mjs"
                before = (f"mkdir -p {shlex.quote(config.WORK_DIR + '/.a3')} && "
                          f"cp -- {shlex.quote(path)} {shlex.quote(copy)} && ")
                outcome, output = self._check_once(programs, check, copy, timeout, before=before)
                label = meta["syntax_tool"] = f"{label}, as a module"
        except SandboxError:
            return None, dict(meta, syntax="skipped", syntax_why="sandbox",
                              syntax_s=round(self._clock() - started, 2))
        meta["syntax_s"] = round(self._clock() - started, 2)
        if outcome == "timeout":
            self._syntax_timeouts.add(ext)
            return None, dict(meta, syntax="timeout")
        if outcome == "no_tool":
            return None, dict(meta, syntax="skipped", syntax_why="no_tool")
        if outcome == "ok":
            return f"syntax check ({label}): ok", dict(meta, syntax="ok")
        if _INCONCLUSIVE.search(output):
            first = next((line.strip() for line in output.split("\n") if _INCONCLUSIVE.search(line)),
                         "")
            return (f"syntax check ({label}): inconclusive: {first[:200]} (syntax the checker alone "
                    "cannot judge, such as JSX or TypeScript)", dict(meta, syntax="inconclusive"))
        shown = output
        if len(shown) > config.SYNTAX_CHECK_CHARS:
            shown = shown[:config.SYNTAX_CHECK_CHARS].rstrip() + " [cut]"
        line = (f"syntax check ({label}): failed\n{shown}" if shown
                else f"syntax check ({label}): failed (no output)")
        return line, dict(meta, syntax="failed")

    def _check_once(self, programs, check, path, timeout, before=""):
        """('ok' | 'failed' | 'no_tool' | 'timeout', the checker's cleaned output)."""
        find = " || ".join(f"command -v {program}" for program in programs)
        script = (f'{before}prog=$({find}) 2>/dev/null; '
                  f'[ -n "$prog" ] || {{ echo {NO_TOOL_MARK}; exit 0; }}; '
                  f'set -- "$prog" {shlex.quote(path)}; {check}')
        r = self._run_check(script, timeout)
        raw = r.get("output", "") or ""
        if r.get("timed_out"):
            return "timeout", ""
        if NO_TOOL_MARK in raw:
            return "no_tool", ""
        lines = [line for line in clean_lines(raw, line_chars=300) if not _CHECK_NOISE.match(line)]
        output = "\n".join(lines).strip("\n")
        return ("ok" if r.get("exit_code") == 0 else "failed"), output

    # -- create ---------------------------------------------------------------------------

    def _create(self, path, content):
        rel = self._writable(path, new_file=True)
        code, _ = self._run(f"test -e {shlex.quote(path)}")
        if code == 0:
            raise ToolError(f"error: {path} already exists; edit it with str_replace.",
                            error_kind="exists")
        bad = _unencodable(content)
        if bad:
            raise ToolError(f"error: {path} was not created: {bad}")
        self._write(path, content)
        if rel is not None:
            self.edited.add(rel)
        count = content.count("\n") + (0 if content.endswith("\n") or not content else 1)
        if rel is None:
            text, meta = f"created {path} ({count} lines).", {}
        elif looks_like_test(rel):
            text, meta = (f"created {rel} ({count} lines). It is a test file, so it is removed "
                          "from the patch at the end.", {"temp_test": True})
        else:
            text, meta = (f"created {rel} ({count} lines). It is inside the repository, so it is "
                          "part of your patch.", {})
        line, check = self._syntax_check(path)
        if line:
            text += "\n" + line
        return text, False, False, None, dict(meta, **check)

    # -- finish ---------------------------------------------------------------------------

    def _finish(self, summary):
        try:
            review = self.workspace.review(keep=self.interface_paths, edited=self.edited)
        except SandboxError as exc:
            return (f"Finished. (The patch could not be checked: {exc}.)", False, True, None,
                    {"finish_round": 1})
        new_flags = set(review.flags) - self._confirmed
        if review.needs_confirmation and new_flags and self._finish_asks < 3:
            self._confirmed |= set(review.flags)
            self._finish_asks += 1
            return review.text, False, False, None, {"finish_round": self._finish_asks}
        return (f"Finished.\n{review.listing}", False, True, None,
                {"finish_round": self._finish_asks + 1})
