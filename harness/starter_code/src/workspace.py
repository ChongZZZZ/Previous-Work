"""The repository as the patch will see it: snapshot, review and cleanup, run through the sandbox.

The host collects the patch with `git add -N . && git diff` (run_all.py extract_patch), which
sees only unstaged changes and includes every new untracked file, and `git apply` rejects a
whole patch that carries a binary file. So:
  * snapshot() records the starting state;
  * review() tells finish() what the patch would contain, and whether to ask the model to
    confirm (an empty patch, new files, or changed tests);
  * cleanup(), run once the loop has ended, moves HEAD back and unstages anything staged,
    puts back changed test files, and removes new test files and new binary files.
    Other new files are only reported: a "scratch" heuristic could delete a file the task
    needs, and the prompt already steers scratch work to /work.
Nothing here touches a file that existed, or was already changed, before the run.

Every git command runs with safe.directory='*': the repository's owner may differ from the
user the sandbox server runs as, and git would then refuse to work (as run_all.py does too).
"""
import collections
import re
import shlex

from src import config

Review = collections.namedtuple("Review", "text needs_confirmation listing flags")
GIT = "git -c safe.directory='*' -c core.quotepath=off"

# What counts as a test: the common test-file naming conventions of the main languages (pytest,
# Go, Jest/Mocha, RSpec, JUnit, xUnit), and files under a conventional test-directory name
# (test/, tests/, Jest's __tests__/ and __snapshots__/, Go's testdata/). Generic on purpose: no
# rule here may encode knowledge of a particular repository (course rule, PROGRESS.md
# 2026-10-10). spec/ is not a reserved test-directory name, so spec files are recognised by their
# names only.
TEST_NAME = re.compile(r"^test_.*\.py$|_tests?\.py$|^conftest\.py$|_test\.go$"
                       r"|\.(test|spec)\.[cm]?[jt]sx?$|_spec\.rb$|Tests?\.(java|kt|cs)$")
TEST_DIRS = {"test", "tests", "__tests__", "__snapshots__", "testdata"}


def looks_like_test(path):
    """Whether path (relative to the repository root) is a test file."""
    path = path.replace("\\", "/")
    parts = path.split("/")
    return (bool(TEST_NAME.search(parts[-1]))
            or bool(TEST_DIRS & {part.lower() for part in parts[:-1]}))


def test_reason(path):
    """Which rule makes path a test file, in words (for the refusal text)."""
    parts = path.replace("\\", "/").split("/")
    if TEST_NAME.search(parts[-1]):
        return f"its name follows a test-file naming convention"
    for part in parts[:-1]:
        if part.lower() in TEST_DIRS:
            return f"it is under a test directory, {part}/"
    return "it is not a test file"


def parse_status(out):
    """(two-letter code, path from the repository root) from `git status --porcelain=v1 -z`."""
    entries, fields = [], out.split("\0")
    i = 0
    while i < len(fields):
        field = fields[i]
        i += 1
        if len(field) < 4:
            continue
        code, path = field[:2], field[3:]
        if code[0] in "RC":  # a rename or copy is followed by its original path
            i += 1
        entries.append((code, path))
    return entries


class Workspace:
    def __init__(self, sb):
        self.sb = sb
        self.initial_head = None
        self.initial_untracked = set()
        self.initial_changed = set()
        self.snapshot_exit = None
        self.last_stashed = []         # new test files cleanup() moved out of the repository

    def run(self, command, timeout_s=None):
        """(exit code, output) of a harness command at the repository root."""
        r = self.sb.exec(command, timeout_s=timeout_s or config.HARNESS_EXEC_TIMEOUT_S)
        return r.get("exit_code"), r.get("output", "")

    def snapshot(self):
        self.run(f"mkdir -p {shlex.quote(config.WORK_DIR + '/scratch')}")
        code, out = self.run(f"{GIT} rev-parse --verify -q HEAD")
        self.snapshot_exit = code
        self.initial_head = out.strip() if code == 0 else None
        entries = self.status()
        self.initial_untracked = {path for code, path in entries if code == "??"}
        self.initial_changed = {path for code, path in entries if code != "??"}
        return self.snapshot_exit

    def status(self):
        code, out = self.run(f"{GIT} status --porcelain=v1 -z --untracked-files=all")
        return parse_status(out) if code == 0 else []

    def new_files(self, entries=None):
        entries = self.status() if entries is None else entries
        return [path for code, path in entries
                if code == "??" and path not in self.initial_untracked]

    def binaries(self, paths):
        """The paths that are binary by git's own test: a NUL byte in the first 8000 bytes."""
        # One sh -c argument must stay under Linux's 128 KB limit, so the paths go in chunks;
        # "./" keeps a name that starts with "-" from being read as an option.
        script = ('for f in "$@"; do [ -f "./$f" ] && [ ! -L "./$f" ] || continue; '
                  'a=$(head -c 8000 "./$f" | wc -c); b=$(head -c 8000 "./$f" | tr -d "\\000" | wc -c); '
                  '[ "$a" -ne "$b" ] && printf "%s\\0" "$f"; done 2>/dev/null; true')
        found, chunk, size = set(), [], 0
        for path in list(paths) + [None]:
            if path is not None and size + len(path) < 60_000:
                chunk.append(shlex.quote(path))
                size += len(path) + 3
                continue
            if chunk:
                _, out = self.run(f"sh -c {shlex.quote(script)} sh " + " ".join(chunk))
                found |= {p for p in out.split("\0") if p in paths}
            chunk, size = ([shlex.quote(path)], len(path) + 3) if path is not None else ([], 0)
        return found

    def binary_changes(self):
        """Tracked files whose change git can only describe as binary ('-\t-' in --numstat)."""
        code, out = self.run(f"{GIT} diff --numstat -z")
        found = set()
        for record in (out.split("\0") if code == 0 else []):
            fields = record.split("\t", 2)
            if len(fields) == 3 and fields[0] == "-" and fields[1] == "-" and fields[2]:
                found.add(fields[2])
        return found

    def review(self, keep=(), edited=None):
        """What the patch will contain after cleanup, and whether finish should ask for one
        confirmation round: a patch that would be empty, a new non-test file the task's Interface
        does not name, or a changed existing test file. It follows cleanup's rules exactly: new
        test files and new binaries are removed unless the Interface names them (keep), changed
        existing test files are always put back. edited: the paths changed through str_replace or
        create; any other change is labelled as made by a command (information only)."""
        keep = set(keep)
        entries = self.status()
        changed = [(code, path) for code, path in entries
                   if code != "??" and path not in self.initial_changed]
        new = self.new_files(entries)
        binary = self.binaries(new)
        binary_changed = self.binary_changes() if changed else set()

        def by_command(path):
            return " (changed by a command)" if edited is not None and path not in edited else ""
        lines, survivors = [], []
        for code, path in changed:
            if looks_like_test(path):
                lines.append(f"  modified: {path} (test file: put back at the end)")
            elif path in binary_changed and "D" not in code:
                lines.append(f"  modified: {path} (binary change: put back at the end, because a "
                             "binary diff makes the whole patch fail to apply)")
            else:
                lines.append(f"  {'deleted' if 'D' in code else 'modified'}: {path}{by_command(path)}")
                survivors.append(path)
        for path in new:
            if path in keep:
                label = by_command(path)
            elif path in binary:
                label = (" (binary: deleted at the end, because a binary file makes the whole patch "
                         "fail to apply)")
            elif looks_like_test(path):
                label = " (test file: removed at the end)"
            else:
                label = by_command(path)
            lines.append(f"  new file: {path}{label}")
            if path in keep or not (path in binary or looks_like_test(path)):
                survivors.append(path)
        listing = "Your patch will contain:\n" + "\n".join(lines) if lines else ""
        if not survivors:
            removed = f"\n{listing}" if lines else ""
            return Review("Your patch would be empty: after the end-of-task cleanup no file differs "
                          f"from the original.{removed}\nIf the task really needs no change, call "
                          "finish again; otherwise make the change first.", True,
                          "Your patch is empty." + removed, frozenset({"empty"}))
        notes, confirm = [], False
        unexpected = [path for path in new if path not in keep and not looks_like_test(path)
                      and path not in binary]
        if unexpected:
            confirm = True
            notes.append("New files inside the repository are part of the patch. Delete the ones "
                         "that are scratch files (reproduction scripts, notes, logs, build output); "
                         "keep scratch work under /work.")
        tests = [path for _, path in changed if looks_like_test(path)]
        if tests:
            confirm = True
            notes.append("You changed existing test files, and test files may not be changed: at "
                         f"the end they will be put back as they were ({', '.join(tests)}), so your "
                         "fix has to work without these changes.")
        flags = frozenset([f"new:{path}" for path in unexpected] + [f"test:{path}" for path in tests])
        if confirm:
            return Review(listing + "\n\n" + "\n".join(notes) + "\nThen call finish again.", True,
                          listing, flags)
        return Review(listing, False, listing, flags)

    def cleanup(self, keep=(), stash_dir=None):
        """Repair what would silently break or pollute the patch. Returns one note per repair.
        keep: new files never removed (the files the task's Interface names); a changed existing
        test file is put back whatever keep says. stash_dir: where new test files are moved
        (outside the repository), so a later attempt can rerun them; without it they are deleted.
        The paths moved are left in self.last_stashed."""
        notes = []
        self.last_stashed = []
        # A git command the bash timeout killed can leave index.lock behind; every later git
        # command that writes the index (and the host's `git add -N`) then fails. The model's
        # loop has ended, so no git command of its own is still running.
        _, out = self.run(f'd=$({GIT} rev-parse --git-dir) && [ -f "$d/index.lock" ] '
                          f'&& rm -f "$d/index.lock" && echo removed')
        if out.strip() == "removed":
            notes.append("removed a stale .git/index.lock left by a killed git command")
        code, out = self.run(f"{GIT} rev-parse --verify -q HEAD")
        head = out.strip() if code == 0 else None
        if self.initial_head and head != self.initial_head:
            code, out = self.run(f"{GIT} reset -q --soft {self.initial_head}")
            notes.append(f"HEAD had moved to {(head or '?')[:12]}; moved it back to "
                         f"{self.initial_head[:12]}, keeping the changes" if code == 0 else
                         f"could not move HEAD back to {self.initial_head[:12]}: {out.strip()[:200]}")
        code, _ = self.run(f"{GIT} diff --cached --quiet")
        if code not in (0, None):
            code, out = self.run(f"{GIT} reset -q")
            notes.append("unstaged the staged changes, so that git diff sees them" if code == 0
                         else f"could not unstage the staged changes: {out.strip()[:200]}")
        keep = set(keep)
        entries = self.status()
        for code, path in entries:
            if not looks_like_test(path) or (code == "??" and path in keep):
                continue
            q = shlex.quote(path)
            if code == "??":
                if path not in self.initial_untracked:
                    if stash_dir:
                        target = f"{stash_dir.rstrip('/')}/{path}"
                        parent = shlex.quote(target.rsplit("/", 1)[0])
                        code, out = self.run(f"mkdir -p -- {parent} && mv -f -- {q} {shlex.quote(target)}")
                        if code == 0:
                            self.last_stashed.append(path)
                            notes.append(f"moved the new test file {path} to {target}: test files "
                                         "may not be changed")
                            continue
                    code, out = self.run(f"rm -f -- {q}")
                    notes.append(f"removed the new test file {path}: test files may not be changed"
                                 if code == 0 else f"could not remove {path}: {out.strip()[:200]}")
            elif path not in self.initial_changed:
                if self.run(f"{GIT} cat-file -e HEAD:{q}")[0] == 0:
                    code, out = self.run(f"{GIT} checkout -q HEAD -- {q}")
                    notes.append(f"put back the original {path}: test files may not be changed"
                                 if code == 0 else f"could not put back {path}: {out.strip()[:200]}")
        for path in sorted(self.binary_changes() - self.initial_changed):
            if self.run(f"test -e {shlex.quote(path)}")[0] == 0:
                code, out = self.run(f"{GIT} checkout -q HEAD -- {shlex.quote(path)}")
                notes.append(f"put back the binary file {path}: git diff cannot carry a binary change, "
                             "and it would make the whole patch fail to apply" if code == 0 else
                             f"could not put back the binary file {path}: {out.strip()[:200]}")
        new = [p for p in self.new_files() if p not in keep]
        for path in sorted(self.binaries(new)):
            self.run(f"rm -f -- {shlex.quote(path)}")
            notes.append(f"deleted the new binary file {path}: git diff cannot carry it, and it "
                         "would make the whole patch fail to apply")
        return notes

    def set_aside(self, stash_dir):
        """Change 8: put the tree back to its starting state and keep what the attempt did under
        stash_dir: the tracked changes as stash_dir/tree.diff, the new files moved as they are
        (new test files are already there, moved by cleanup). Returns (notes, moved paths)."""
        notes, moved = [], []
        root = stash_dir.rstrip("/")
        d = shlex.quote(root)
        self.run(f"mkdir -p {d}")
        # The host's extract ran `git add -N .`: new files are intent-to-add entries until the
        # index is reset, and would otherwise look like tracked changes below.
        self.run(f"{GIT} reset -q")
        code, out = self.run(f"{GIT} diff > {d}/tree.diff")
        if code != 0:
            notes.append(f"could not save the tracked changes: {out.strip()[:200]}")
        for code, path in self.status():
            q = shlex.quote(path)
            if code == "??":
                if path in self.initial_untracked:
                    continue
                target = f"{root}/{path}"
                parent = shlex.quote(target.rsplit("/", 1)[0])
                code, out = self.run(f"mkdir -p -- {parent} && mv -f -- {q} {shlex.quote(target)}")
                if code == 0:
                    moved.append(path)
                else:
                    notes.append(f"could not move {path}: {out.strip()[:200]}")
            elif path not in self.initial_changed:
                code, out = self.run(f"{GIT} checkout -q HEAD -- {q}")
                if code != 0:
                    notes.append(f"could not put back {path}: {out.strip()[:200]}")
        return notes, moved

    def changed_paths(self):
        """Every path the patch would touch (for the ledger and the end-of-task checks)."""
        entries = self.status()
        return sorted({path for code, path in entries
                       if (code == "??" and path not in self.initial_untracked)
                       or (code != "??" and path not in self.initial_changed)})
