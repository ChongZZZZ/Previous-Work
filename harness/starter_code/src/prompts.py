"""What the model is told.

Written from general practice and the course's lectures only, never from runs on benchmark
tasks: the course forbids lessons learned offline on the benchmark, including instructions that
look general but encode one (announcement of 2026-10-10; PROGRESS.md). Its sources:
  * the working method is the lectures' (explore with extrinsic signals, reproduce first, the
    smallest change, verify with the closest tests before finishing; Lectures 4, 6, 7);
  * the order of the task's parts, requirements and interface before the issue, is the course
    notes' recommendation (Lecture 5 research, "requirements and interface first");
  * the environment is the sandbox as the assignment documents it: no network, Go modules only
    from the local cache (the assignment page), one CPU and a fresh shell per call (run_all.py),
    scratch space under /work (src/sandbox_server.py);
  * the integrity rules are the lectures' guardrails: no test edits, no history beyond HEAD, no
    stubs or hard-coded values (Lecture 7).

Nothing in SYSTEM_PROMPT depends on the task. It is sent first in every request, followed by the
tool schemas, so the same prefix is cached across all tasks of a run; the task itself goes in
the first user message.
"""
import re

from src import config

SYSTEM_PROMPT = f"""\
You are fixing an issue in a git repository. You work alone: nobody will answer questions, so \
make reasonable assumptions and keep going. When you finish, your changes are collected with \
`git diff` and checked by hidden tests.

The task has three parts:
- "Requirements": behaviours the change must have.
- "Interface": the names, signatures and file locations of what to add or change. Use exactly \
these names.
- the issue itself: what is wrong or missing.
Your change must satisfy all three.

How to work:
1. Explore before you edit: find the code involved (grep -rn, find), read it with view, and \
read the existing tests that cover it. Read several files or ranges in one view call.
2. Reproduce: write a small check that exercises the behaviour the task describes, and run it. \
Before your change it should fail or show the problem.
3. Change: make the smallest change that satisfies the requirements and the interface. Look at \
how similar code in the repository is written, and follow its conventions.
4. Verify: run your check again and make sure it passes, then run the existing tests closest to \
the code you changed. Do not finish with a change you have not run.
5. Call finish with a short summary of what you changed and how you verified it.

The environment:
- There is no network. Do not install or upgrade packages: the hidden tests run in a fresh copy \
of this environment. Go modules resolve only from the local module cache (GOPROXY=off); to see \
which versions of a module are there, run ls $(go env GOMODCACHE)/cache/download/<module>/@v/
- Each bash call is a fresh non-interactive shell at the repository root, without stdin. Do not \
start interactive programs or watchers.
- The machine has one CPU: run targeted tests (one file, one test) with a timeout, not whole \
suites.
- Scratch files (scripts, notes, logs, build output) go under /work/scratch: files you create \
inside the repository become part of your patch, except new test files, which are removed from \
the patch at the end.

Rules:
- Leave your changes as unstaged edits. Git commands that change the repository state (add, \
commit, stash, reset, checkout, restore, clean, ...) are refused. Use `git diff` or \
`git show HEAD:<path>` to see the original code.
- Work only from the repository as checked out at HEAD; do not consult other commits or \
branches.
- Do not modify existing test files: the fix belongs in the source code.
- No stubs, placeholders or hard-coded expected values: implement the behaviour.
- You have at most {config.TASK_MAX_CALLS} model calls and {config.TASK_MAX_S // 60} minutes \
for this task."""

NONE_GIVEN = "(none given)"

NUDGE = ("You did not call a tool, and text alone changes nothing. Continue with the next tool "
         "call. If the change is complete and verified, call finish. Text that only looks like a "
         "tool call is not run: use the tool-calling format.")
NUDGE_CUT_OFF = ("Your reply was cut off before it called a tool: it reached the output length "
                 "limit. Continue with the next tool call, and keep your thinking shorter.")
WRAP_UP = ("Budget: {why}. Wrap up now: finish the change you are making, run one quick check, "
           "and call finish. Unfinished work is still submitted as it stands.")
NOT_RUN = "[not run: the task's budget ran out before this call]"
FINISH_NOW = ("You have {left} model call{s} left for this {what}. Call finish now, with your "
              "summary; a reply without finish ends the {what}, and your changes are submitted "
              "as they stand.")


def task_parts(task):
    def part(key):
        text = (task.get(key) or "").strip()
        return text or NONE_GIVEN
    return (f"## Requirements\n\n{part('requirements')}\n\n"
            f"## Interface\n\n{part('interface')}\n\n"
            f"## Issue\n\n{part('problem_statement')}")


def task_message(task):
    """The first user message: requirements, interface, issue, then where the repository is."""
    return (task_parts(task) + "\n\n"
            f"The repository is at {task.get('workdir') or '/app'}; every bash call starts there.")


def wrap_up(why):
    return WRAP_UP.format(why=why)


def finish_now(left, what):
    return FINISH_NOW.format(left=left, s='' if left == 1 else 's', what=what)


# The planning step (src/solver.py, change 4; Lecture 8 research: BAAR's First-Large heuristic,
# Aider's architect and editor; "plan once at the start"): a stronger model explores and writes
# the plan in the first replies of the task, and the attempt's own model carries it out in the
# same conversation. The paragraph is part of the task message, so the system prompt and the
# tool schemas stay byte-identical; the hand-over and the notes are run-time facts.
PLAN_STEP = """

## How to start

{opening} The plan is the brief for the work that follows:
- the Requirements as a checklist, each with the check that would prove it;
- each Interface item with the file it belongs to;
- anything the task leaves ambiguous, and the reading you choose;
- the files and functions to change, and what to change in each and why;
- the existing tests nearest to that code, and the command that checks the change.
The plan is a guide, not a proof: check its claims against the code as you go."""
# change 4: the plan is expected within the exploring replies
PLAN_OPENING_WITHIN = ("Your first {calls} replies are a planning step. Explore with bash and view "
                       "only, several calls per reply where you can: edits and finish are refused "
                       "until the plan is written. Then write the plan as plain text, without tool "
                       "calls, in reply {calls} at the latest.")
# change 4a: the plan has a reply of its own after the exploring replies
PLAN_OPENING_REPLY = ("Your first {calls} replies are for exploring: bash and view only, several "
                      "calls per reply where you can; edits and finish are refused until the plan is "
                      "written. Your reply after them is the plan: plain text, without tool calls. "
                      "You may also write the plan earlier, as a reply without tool calls.")
PLAN_REFUSED = ("The planning step allows only bash and view. Write the plan first, as plain text "
                "without tool calls; the change comes after it.")
PLAN_NOW = ("Your exploring replies are used. This reply is the plan reply: write the plan now, as "
            "plain text and without tool calls.")
# change 4b: a plan reply that was not a plan (its reads were run) is asked for again
PLAN_AGAIN = ("Your last reply was not the plan ({chars} characters of text). This reply is the "
              "plan reply: write the plan now, as plain text and without tool calls, with the five "
              "items listed under \"How to start\".")
PLAN_REPLY_NOT_RUN = ("Not run: this was the plan reply, and the plan is taken from its text. The "
                      "change comes next.")
PLAN_HANDOVER = ("The planning step is over. Carry out the plan above: reproduce, make the change, "
                 "verify it, then call finish.")
PLAN_OVER = ("The planning step is over: {used}. Continue with the method above, using what you "
             "have read and planned so far: reproduce, make the change, verify it, then call finish.")


def plan_step(calls, plan_reply=False):
    opening = (PLAN_OPENING_REPLY if plan_reply else PLAN_OPENING_WITHIN).format(calls=calls)
    return PLAN_STEP.format(opening=opening)


def plan_step_implement(calls):
    return (f"\n\n## How to start\n\nYour first {calls} replies are the first engineer's turn: "
            "explore with bash and view, then make the change with str_replace and create, "
            "several calls per reply where you can. finish is not yours: when the change is "
            "made, say so in a reply without tool calls; you are then asked for one check of "
            "it, and a second engineer verifies the change and calls finish. If your replies "
            "run out first, the second engineer continues from where you stopped.")


def implement_summary(why):
    return {"implemented": "the change above is made",
            "calls": "its replies ran out, so the change above may be incomplete",
            "usd": "its budget ran out, so the change above may be incomplete",
            "none": "no change was made"}.get(why, "its turn ended before hand-over")


def implement_handover(why, check=None, result=""):
    facts = (check_facts(check["path"], check["command"], result).rstrip() + " "
             if check else "")
    return (f"The first engineer's turn is over: {implement_summary(why)}. {facts}"
            "Your job now is verification: run the check and the existing tests nearest the "
            "change, read the diff (`git diff`) against the Requirements and the Interface, "
            "fix what is wrong or missing, then call finish.")


def implement_record(why):
    if why == "none":
        return "No change was made during the first engineer's turn."
    return ("The first engineer's work is in the tree; inspect `git diff`: "
            + implement_summary(why) + ".")


def plan_again(chars):
    return PLAN_AGAIN.format(chars=chars)


def plan_over(why, calls):
    used = {"calls": f"its {calls} replies are used", "usd": "its budget is used",
            "no_plan": "the plan reply carried no text",
            "leak": "the plan reply came out as tool-call markup, not a plan"}.get(why, "it has ended")
    return PLAN_OVER.format(used=used)


# Change 11b: the plan reply without tools comes out as tool-call markup when the model wanted to
# read more (DeepSeek-style markers, or the generic forms); such a reply is not a plan.
TOOL_MARKUP = re.compile(r"<[｜|]DSML[｜|]|</?tool_calls>|<invoke name=|<function_calls>|<tool_call>")
PLAN_LEAK_NOTE = ("That reply came out as tool-call markup and nothing ran: no tools were offered, so "
                  "it is not a plan. This reply has the tools again: read what you still need. The "
                  "plan is asked for after it.")
PLAN_AFTER_LEAK = ("Your exploring replies are used. This reply is the plan reply: write the plan now, "
                   "as plain text and without tool calls. Tool-call markup in this reply is not run "
                   "and is not a plan.")


def looks_like_tool_markup(text):
    return bool(TOOL_MARKUP.search(text or ""))


# The pre-finish review (src/solver.py, change 3): a second model reads the task and the diff once,
# before the change is submitted, and lists the gaps against the Requirements and the Interface
# (Lecture 5 research: a one-shot checklist review of the final diff from a different tier).
# Byte-stable, so it is cached across tasks; the task and the diff go in the user message.
REVIEW_SYSTEM = """\
You review a code change made by another engineer against the task it was meant to solve. You \
are given the task (Requirements, Interface, Issue), the change as a unified diff, the engineer's \
summary and the last commands they ran. You cannot run anything: judge what the diff shows and \
say "cannot tell" where the diff alone does not settle it. New test files in the diff are the \
engineer's own checks and are removed before grading. Be concrete and brief: name the file and \
function, and the requirement or interface item each gap belongs to. Hidden tests will call the \
Interface exactly as written and check each Requirement literally."""

REVIEW_FORM = """\
Reply in exactly this form, nothing else:
Requirements:
- <requirement, shortened>: satisfied | not satisfied | cannot tell: <why, one line>
Interface:
- <item>: satisfied | not satisfied | cannot tell: <why, one line>
Gaps:
- <concrete fix, most important first>   (or the single word: none)"""

REVIEW_GAPS = ("A review by a second model compared your change with the Requirements and the "
               "Interface and found gaps:\n\n{review}\n\nFix them, or explain in your finish "
               "summary why they are not gaps; then call finish again. This review happens once.")


def review_message(task, diff, summary, commands):
    """The reviewer's user message: the task, the diff (cut to config.REVIEW_DIFF_CHARS), the
    engineer's summary, the last commands, and the form of the answer."""
    diff = diff or ""
    cut = len(diff) > config.REVIEW_DIFF_CHARS
    shown = diff[:config.REVIEW_DIFF_CHARS].rstrip("\n")
    text = task_parts(task) + "\n\n## The change\n\n```diff\n" + shown + "\n```"
    if cut:
        text += f"\n(The diff has {len(diff)} characters; the first {config.REVIEW_DIFF_CHARS} are shown.)"
    summary = " ".join(str(summary or "").split())
    text += "\n\n## The engineer's summary\n\n" + (summary or "(none given)")
    lines = command_lines(commands)
    if lines:
        text += "\n\n## The last commands they ran (exit code, seconds, command)\n" + lines
    return text + "\n\n" + REVIEW_FORM


def review_verdict(text):
    """('no_gaps' | 'gaps' | 'unparsed', the review as shown back to the model)."""
    import re
    text = str(text or "").strip()
    m = re.search(r"(?im)^\s*gaps\s*:", text) or re.search(r"(?i)\bgaps\s*:", text)
    if not m:
        return "unparsed", text
    rest = text[m.end():].strip()
    body = rest.lstrip("-*\u2022 ").strip().rstrip(".").lower()
    if not rest or body.startswith(("none", "no gap", "nothing")):
        return "no_gaps", text
    shown = text if len(text) <= config.REVIEW_SHOWN_CHARS else text[:config.REVIEW_SHOWN_CHARS].rstrip() + " [cut]"
    return "gaps", shown


# Compaction (src/solver.py, change 5; the professor's tip; Lecture 4 context engineering; TRACE's
# template, Lecture 8 research): the notes asked of the old conversation, and the section that
# follows the task message in the restarted one. Everything in it is a run-time fact or the
# model's own text.
COMPACT_NOTES = ("This conversation is about to be compacted: everything above will be replaced by "
                 "the notes you write now, the plan, the list of files you viewed, the last commands "
                 "with their exit codes, the last tool results and your current diff; the repository "
                 "stays as it is. This is not a request for a tool call. In at most 400 words, write "
                 "the notes you need to continue: (1) what you have established about the code "
                 "(files, functions, how the relevant parts work); (2) what you have changed so far "
                 "and why (the diff is shown separately); (3) what you ran and what the results "
                 "were; (4) what remains to do, in order, and the command that checks the change.")
COMPACT = """

## Earlier in this task

This conversation was compacted to keep the context short: your work so far is summarised \
below, and the repository is as you left it (your changes are still applied). Continue from \
here; do not redo what is done.{notes}{plan}{files}{commands}{results}

### Your changes so far (`git diff`)

{diff}

Full outputs you saved are under {out_dir}/; your scratch files are under {scratch_dir}/."""
COMPACT_NOTES_SECTION = "\n\n### Your notes, written just before the compaction\n\n{notes}"
COMPACT_NO_NOTES = "\n\n(No notes could be written before the compaction.)"
COMPACT_PLAN_SECTION = "\n\n### The plan written at the start\n\n{plan}"
COMPACT_FILES_SECTION = "\n\n### Files you viewed (most recent last)\n{lines}"
COMPACT_COMMANDS_SECTION = "\n\n### The last commands you ran (exit code, seconds, command)\n{lines}"
COMPACT_RESULTS_SECTION = "\n\n### The last tool results, verbatim\n\n{results}"


def compact_message(notes, plan, files, commands, results, diff, out_dir, scratch_dir):
    """The section appended to the task message when a conversation is restarted."""
    notes = " ".join(str(notes or "").split())
    if len(notes) > config.COMPACT_NOTES_CHARS:
        notes = notes[:config.COMPACT_NOTES_CHARS].rstrip() + " [cut]"
    notes_text = COMPACT_NOTES_SECTION.format(notes=notes) if notes else COMPACT_NO_NOTES
    plan = str(plan or "").strip()
    plan_text = COMPACT_PLAN_SECTION.format(plan=plan) if plan else ""
    files = [f for f in files if f]
    files_text = COMPACT_FILES_SECTION.format(lines="\n".join(f"- {f}" for f in files)) if files else ""
    lines = command_lines(commands)
    commands_text = COMPACT_COMMANDS_SECTION.format(lines=lines) if lines else ""
    results = str(results or "").strip()
    if len(results) > config.COMPACT_RESULTS_CHARS:
        results = results[:config.COMPACT_RESULTS_CHARS].rstrip() + "\n[cut]"
    results_text = COMPACT_RESULTS_SECTION.format(results=results) if results else ""
    diff = diff or ""
    if not diff.strip():
        shown = "(No changes yet, or the diff could not be read: see `git diff`.)"
    else:
        cut = len(diff) > config.COMPACT_DIFF_CHARS
        shown = "```diff\n" + diff[:config.COMPACT_DIFF_CHARS].rstrip("\n") + "\n```"
        if cut:
            shown += (f"\n(The diff has {len(diff)} characters; the first "
                      f"{config.COMPACT_DIFF_CHARS} are shown; `git diff` shows the rest.)")
    return COMPACT.format(notes=notes_text, plan=plan_text, files=files_text, commands=commands_text,
                          results=results_text, diff=shown, out_dir=out_dir, scratch_dir=scratch_dir)


# A retry's handoff (src/solver.py), appended to the task message of its fresh conversation. It
# says only what the dispatcher's evaluate() answered, F of T; that F = T can mean the tests
# never ran is run_all.py's own behaviour (a patch that does not apply or build is scored as
# every test failing).
RETRY = """

## Previous attempt

An earlier attempt at this task made the change below. The hidden tests gave it this verdict: \
{failed} of {total} fail. The change is still applied in the repository. Do not assume it is \
right: check it against the Requirements and the Interface, find what is wrong or missing, and \
fix it. You may keep, change or undo any part of it.{all_failed} This attempt has at most \
{calls} model calls and {minutes} minutes (these replace the limits above); a note will tell you \
when to wrap up.{assessment}{commands}{stash}{earlier}{saved}

{diff}"""
RETRY_ALL_FAILED = (" Every test failed, so the patch may not have built, or the tests may not "
                    "have run at all.")
RETRY_SUMMARY = "\n\nThe earlier attempt's own summary: {summary}"
RETRY_ASSESSMENT = ("\n\nThe earlier attempt's own assessment, written after it saw the verdict: "
                    "{reflection}")
RETRY_COMMANDS = "\n\nThe last commands the earlier attempt ran (exit code, seconds, command):\n{lines}"
RETRY_STASH = ("\n\nThe earlier attempt's own test files were moved out of the repository to "
               "{stash_dir}/ ({paths}); copy one back to rerun it. New test files are removed from "
               "the patch at the end.")
# The reflection asked of the attempt's own conversation once the verdict is known (Lecture 4
# research, Reflexion: a reflection grounded in the test feedback; without it, none).
REFLECT = ("The hidden tests were run on the change as it stands: {failed} of {total} fail. You "
           "cannot see which tests, and this is not a request for a tool call. In at most 200 "
           "words, write: (1) which Requirement or Interface item the failing tests most likely "
           "cover, and why; (2) what you assumed but did not check or run; (3) what you would "
           "change next, as concretely as you can.{all_failed}")
RETRY_EARLIER = "\n\nVerdicts so far: {items}; the change below is the latest attempt's."


def reflect_message(failed, total):
    return REFLECT.format(failed=failed, total=total,
                          all_failed=RETRY_ALL_FAILED if total and failed == total else "")


def command_lines(commands):
    """One line per (command, exit, elapsed seconds, timed out, timeout) tuple."""
    lines = []
    for command, exit_code, elapsed, timed_out, timeout in commands:
        text = " ".join(str(command or "").split())
        if len(text) > config.HANDOFF_COMMAND_CHARS:
            text = text[:config.HANDOFF_COMMAND_CHARS] + "..."
        if timed_out:
            lines.append(f"- timed out after {timeout} s: {text}")
        else:
            secs = f"{elapsed:.0f} s" if isinstance(elapsed, (int, float)) else "? s"
            lines.append(f"- exit {exit_code}, {secs}: {text}")
    return "\n".join(lines)


def retry_message(failed, total, summary, diff, calls, minutes, history=(), reflection="",
                  commands=(), stashed=(), stash_dir="", saved=""):
    """The handoff: the verdict; the earlier attempt's own assessment written after the verdict
    (reflection), or its finish summary when there is none; the last commands it ran with their
    exit codes; where its temporary test files were moved; its diff (cut to
    config.RETRY_DIFF_CHARS); the retry's own limits; and every verdict so far when there is
    more than one (history: (attempt, F, T) per graded attempt)."""
    diff = diff or ""
    if not diff.strip():
        shown = "(The diff could not be read; see it with `git diff`.)"
    else:
        cut = len(diff) > config.RETRY_DIFF_CHARS
        shown = "```diff\n" + diff[:config.RETRY_DIFF_CHARS].rstrip("\n") + "\n```"
        if cut:
            shown += (f"\n(The diff has {len(diff)} characters; the first "
                      f"{config.RETRY_DIFF_CHARS} are shown; `git status` and `git diff` show "
                      f"the rest.)")
    summary = " ".join(str(summary or "").split())
    reflection = " ".join(str(reflection or "").split())
    if reflection:
        assessment = RETRY_ASSESSMENT.format(reflection=reflection)
    else:
        assessment = RETRY_SUMMARY.format(summary=summary) if summary else ""
    lines = command_lines(commands)
    commands_text = RETRY_COMMANDS.format(lines=lines) if lines else ""
    stashed = [p for p in stashed if p]
    stash = RETRY_STASH.format(stash_dir=stash_dir, paths=", ".join(stashed)) if stashed and stash_dir else ""
    history = [h for h in history if h[1] is not None]
    earlier = ""
    if len(history) > 1:
        items = "; ".join(f"attempt {n}, {f} of {t} fail" for n, f, t in history)
        earlier = RETRY_EARLIER.format(items=items)
    return RETRY.format(
        failed=failed, total=total, calls=calls, minutes=minutes,
        all_failed=RETRY_ALL_FAILED if total and failed == total else "",
        assessment=assessment, commands=commands_text, stash=stash,
        earlier=earlier, saved=saved or "", diff=shown)


# Stall guards (src/solver.py, change 7; Lecture 4 research: Lewis's harness guards; the
# professor's tip 2, "ask Expert on a stall"): run-time notes appended to tool results, and the
# question put to a second model when an attempt stalls. Every line is a run-time fact.
STALL_WHAT = {"view": ("range", "the file has not changed"),
              "bash": ("command", "the output has not changed")}
STALL_REPEAT = "note: this is the same as your call {n}: the same {what} and the same result."
STALL_REPLACED = ("[Same as call {n}: the same {what} and the same result, which is already "
                  "above; {unchanged}.]")
STALL_EXPLORE = ("{calls} model calls in this attempt without an edit. Decide the change from "
                 "what you have read and make it, then verify it; {left} calls are left.")
STALL_EXPLORE_TIME = ("{minutes} minutes of this attempt without an edit. Decide the change from what "
                      "you have read and make it, then verify it; {left} minutes and {calls} calls are "
                      "left.")
STALL_SAME_FAILURE = ("note: this command has failed the same way {n} times ({how}). Change the "
                      "approach or the command rather than running it again.")
STALL_EXPERT_NOTE = ("A second model looked at your progress so far and wrote:\n\n{answer}\n\n"
                     "Take it as a pointer, not a proof: check it against the code.")
STALL_SYSTEM = """\
You advise an engineer who is fixing an issue in a git repository and has stalled. You are given \
the task (Requirements, Interface, Issue), the plan they started from, their change so far as a \
unified diff, the last commands they ran, the last tool results they saw and their last reply. \
You cannot run anything: judge from what is shown and say "cannot tell" where it does not \
settle a point. Be concrete and brief: name the file and function. Hidden tests will call the \
Interface exactly as written and check each Requirement literally."""
STALL_FORM = """\
Reply in at most 250 words, in this form:
What is wrong or missing: <against the Requirements and the Interface>
Change: <the file and function, and what to change in it>
Check: <the command that shows it works>
If a step they are stuck on is unnecessary, say so."""


def stall_repeat(n, tool):
    what, _ = STALL_WHAT[tool]
    return STALL_REPEAT.format(n=n, what=what)


def stall_replaced(n, tool):
    what, unchanged = STALL_WHAT[tool]
    return STALL_REPLACED.format(n=n, what=what, unchanged=unchanged)


def stall_explore(calls, left):
    return STALL_EXPLORE.format(calls=calls, left=left)


def stall_explore_time(minutes, left, calls):
    return STALL_EXPLORE_TIME.format(minutes=minutes, left=left, calls=calls)


def stall_same_failure(n, code):
    how = "timed out" if code == "timeout" else f"exit {code}"
    return STALL_SAME_FAILURE.format(n=n, how=how)


def stall_message(task, plan, diff, commands, results, last_reply, why_text):
    """The second model's user message: the task, the plan, the diff (cut), the last commands,
    the last tool results (cut), the model's last reply (cut), why it is asked, and the form."""
    text = task_parts(task)
    plan = str(plan or "").strip()
    if plan:
        text += "\n\n## The plan they started from\n\n" + plan
    diff = diff or ""
    if diff.strip():
        cut = len(diff) > config.STALL_EXPERT_DIFF_CHARS
        text += ("\n\n## Their change so far (`git diff`)\n\n```diff\n"
                 + diff[:config.STALL_EXPERT_DIFF_CHARS].rstrip("\n") + "\n```")
        if cut:
            text += (f"\n(The diff has {len(diff)} characters; the first "
                     f"{config.STALL_EXPERT_DIFF_CHARS} are shown.)")
    else:
        text += "\n\n## Their change so far\n\n(no file changed yet)"
    lines = command_lines(commands)
    if lines:
        text += "\n\n## The last commands they ran (exit code, seconds, command)\n" + lines
    shown = []
    for result in list(results)[-config.STALL_EXPERT_RESULTS:]:
        result = str(result or "")
        if len(result) > config.STALL_EXPERT_RESULT_CHARS:
            result = result[:config.STALL_EXPERT_RESULT_CHARS].rstrip() + " [cut]"
        shown.append(result)
    if shown:
        text += "\n\n## The last tool results they saw\n\n" + "\n\n---\n\n".join(shown)
    last_reply = " ".join(str(last_reply or "").split())
    if last_reply:
        if len(last_reply) > config.STALL_EXPERT_REPLY_CHARS:
            last_reply = last_reply[:config.STALL_EXPERT_REPLY_CHARS].rstrip() + " [cut]"
        text += "\n\n## Their last reply\n\n" + last_reply
    text += "\n\n## Why you are asked\n\n" + why_text
    return text + "\n\n" + STALL_FORM


# The re-attempt after an early empty end (src/solver.py, change 7, item 5): appended to the
# task message of the fresh conversation. The reason is the harness's own stop reason.
REATTEMPT = """

## Earlier in this task

An earlier attempt at this task ended {how}, before it made any change: the repository is as \
checked out. Start again with the method above.{plan} This attempt has at most {calls} model \
calls and {minutes} minutes (these replace the limits above); a note will tell you when to wrap \
up."""
REATTEMPT_HOW = {
    "no_tool_calls": ("after three replies in a row without a tool call (text alone changes "
                      "nothing: every step must be a tool call, in the tool-calling format)"),
    "api_error": "because the model API stopped answering for a while",
    "sandbox_dead": "because the sandbox stopped answering for a while"}
REATTEMPT_PLAN = "\n\n### The plan written at the start\n\n{plan}"


def reattempt_message(reason, plan, calls, minutes):
    plan = str(plan or "").strip()
    return REATTEMPT.format(how=REATTEMPT_HOW.get(reason, f"early ({reason})"),
                            plan=REATTEMPT_PLAN.format(plan=plan) if plan else "",
                            calls=calls, minutes=minutes)


# The independent second attempt (src/solver.py, change 8): a fresh first attempt told one
# sentence of fact, the verdict, and its own limits. Nothing of the earlier attempt is handed
# over, so the two draws are independent.
FRESH = """

## Earlier in this task

An earlier attempt at this task made a change that failed the hidden tests: {failed} of {total} \
fail. Its changes were set aside, so the repository is as checked out. Start afresh with the \
method above. This attempt has at most {calls} model calls and {minutes} minutes (these replace \
the limits above); a note will tell you when to wrap up."""
# In the handoff of a later retry: where an earlier, better attempt's change was saved.
RETRY_SAVED = ("\n\nAttempt {n}'s change ({failed} of {total} fail) was set aside as a diff at "
               "{path}; apply it with `git apply {path}` if you would rather start from it.")


def fresh_message(failed, total, calls, minutes):
    return FRESH.format(failed=failed, total=total, calls=calls, minutes=minutes)


def saved_note(n, failed, total, path):
    return RETRY_SAVED.format(n=n, failed=failed, total=total, path=path)


# The check reply (src/solver.py, change 11): after its plan, the planning model writes and runs
# a check; the hand-over carries the facts; the finish round names what has not been done. Every
# line is a run-time fact; nothing about any repository.
PLAN_CHECK_NOW = ("{opening} This reply is the check, not more exploration. In this one reply: create "
                  "one runnable check of the Requirements, as a new test file (at a test path; it is "
                  "removed from the patch at the end) or a script under {scratch}, and run it with "
                  "bash, so that it fails now, before the change. Use create and bash only; existing "
                  "files are not edited in the planning step. The change itself comes after this "
                  "reply.")
PLAN_CHECK_OPENING = "Your plan is noted."
PLAN_CHECK_OPENING_NO_PLAN = "No plan was taken from that reply."
PLAN_CHECK_AGAIN_NO_FILE = ("Nothing was created: that was exploration, and this is the last reply of the "
                            "planning step. Create the check now (create: a new test file or a script "
                            "under {scratch}) and run it (bash), both in this reply.")
PLAN_CHECK_AGAIN_NOT_RUN = ("The check is created but not run. Run it with bash now; this is the last "
                            "reply of the planning step.")
PLAN_CHECK_REFUSED = ("The check reply allows only bash, view, and create for a new test file or a file "
                      "under {scratch}; existing files are not edited in the planning step, and the "
                      "change comes after this reply.")
PLAN_HANDOVER_CHECK = ("The planning step is over. Carry out the plan above: reproduce, make the change, "
                       "verify it, then call finish. {check} Make it pass, then run the existing tests "
                       "nearest the change. The check is a guide, not a proof: the hidden tests judge "
                       "the Requirements and the Interface.")
CHECK_RUN = "The check written for it is at {path}; run it with `{command}`; it now ends with:\n{result}\n"
CHECK_COMMAND_ONLY = "The check written for it is the command `{command}`; it now ends with:\n{result}\n"
CHECK_UNRUN = "The check written for it is at {path}; it has not been run yet: run it first."
PLAN_CHECK_SECTION = ("\n\n### The check written at the start\n\nPath: {path}\nCommand: `{command}`\n"
                      "It ended with: {result}")
FINISH_CHECK_NOT_RUN = ("The check at {path} has not been run since your last edit. Run it{command} and "
                        "look at the result, then call finish again. This is asked once.")
FINISH_INTERFACE_MISSING = ("The task's Interface names paths that do not exist in the repository: "
                            "{paths}. Create them, or explain in your finish summary why they are not "
                            "needed; then call finish again. This is asked once.")


def _check_result(result):
    """The tail of the check's output (the verdict is at the end), cut to the configured size."""
    result = str(result or "").strip() or "(no output)"
    if len(result) > config.PLAN_CHECK_RESULT_CHARS:
        result = "[...] " + result[-config.PLAN_CHECK_RESULT_CHARS:].lstrip()
    return result


def check_facts(path, command, result):
    """The check's facts in one sentence: file and command, command only, or file not run yet."""
    if path and command:
        return CHECK_RUN.format(path=path, command=command, result=_check_result(result))
    if command:
        return CHECK_COMMAND_ONLY.format(command=command, result=_check_result(result))
    return CHECK_UNRUN.format(path=path)


def plan_check_now(scratch, plan=True):
    opening = PLAN_CHECK_OPENING if plan else PLAN_CHECK_OPENING_NO_PLAN
    return PLAN_CHECK_NOW.format(opening=opening, scratch=scratch)


def plan_check_now_after(scratch):
    return ("This reply is the check: create one runnable check of the Requirements against "
            "the change you made, as a new test file (at a test path; it is removed from the "
            f"patch at the end) or a script under {scratch}, and run it with bash in this same "
            "reply. It should distinguish the original behaviour from the required behaviour "
            "and pass with the change. Use create and bash; do not edit existing files. "
            "A second engineer verifies the change and calls finish after this reply.")


def implement_finish_refused(scratch):
    return ("finish is reserved for the second engineer. The change is taken as made. "
            + plan_check_now_after(scratch))


def implement_check_refused(scratch):
    return ("The check reply allows bash, view, and create for a new test file or a "
            f"script under {scratch}. Do not edit existing files; the second engineer "
            "verifies the change and calls finish after this reply.")


def plan_check_again(created, scratch):
    return PLAN_CHECK_AGAIN_NOT_RUN if created else PLAN_CHECK_AGAIN_NO_FILE.format(scratch=scratch)


def plan_over_check(why, calls, path, command, result):
    """The hand-over after a planning step that produced a check but no plan."""
    tail = PLAN_HANDOVER_CHECK.split("{check}", 1)[1].strip()
    return plan_over(why, calls) + " " + check_facts(path, command, result).rstrip("\n") + "\n" + tail


def plan_check_refused(scratch):
    return PLAN_CHECK_REFUSED.format(scratch=scratch)


def plan_handover_check(path, command, result):
    return PLAN_HANDOVER_CHECK.format(check=check_facts(path, command, result))


def plan_check_section(path, command, result):
    return PLAN_CHECK_SECTION.format(path=path or "(none; the command is the check)",
                                     command=command or "(not run yet)",
                                     result=_check_result(result) if command else "(not run)")


def finish_check_not_run(path, command):
    return FINISH_CHECK_NOT_RUN.format(path=path or "(the command below)",
                                       command=f" (`{command}`)" if command else "")


def finish_interface_missing(paths):
    return FINISH_INTERFACE_MISSING.format(paths=paths)
