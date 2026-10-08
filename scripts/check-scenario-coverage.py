#!/usr/bin/env python3
"""Archive gate: every scenario a change adds or modifies is covered by a test.

A test covers a scenario by carrying the annotation

    @spec <capability-path> "<scenario name>"

in a comment or in its name, e.g.

    // @spec components/entity/order/create "Second create for the same cart"

The scenarios checked are those under `## ADDED Requirements` and
`## MODIFIED Requirements` in the change's delta specs. The annotations are
searched in the test files, including Storybook stories run as component
tests, of the implementing repositories: every sibling
checkout of this store whose `openspec/config.yaml` points at this store
(`store: <id>`), or the directories given with --repos. When this store is
run from a git worktree (e.g. `.claude/worktrees/<name>`), the siblings are
those of the store's main checkout, not of the worktree.

A sibling checkout is searched at its `origin/main`, not its working tree, so
the result matches CI whatever branch the checkout is on (run `git fetch` in it
first; this script never fetches). A sibling without an `origin/main` ref, a
directory given with --repos, or any repository under --worktree is searched
as it is on disk.

A scenario that cannot be verified by an automated test is exempted by a line
anywhere in the change's own files (proposal, design, tasks):

    @spec-manual <capability-path> "<scenario name>" -- <how it is verified>

Usage: check-scenario-coverage.py <change> [--repos DIR ...] [--worktree]
Exit status 1 lists the uncovered scenarios."""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST_FILE = re.compile(r"(_test\.go|\.(test|spec|stories)\.[cm]?[jt]sx?|_test\.py|test_[^/]*\.py)$")
TEST_DIRS = {"e2e", "test", "tests"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "coverage", "vendor", ".venv"}
DELTA = re.compile(r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$")
SCENARIO = re.compile(r"^#### Scenario:\s*(.+?)\s*$")
ANNOTATION = re.compile(r'@spec\s+(\S+)\s+"([^"]+)"')
MANUAL = re.compile(r'@spec-manual\s+(\S+)\s+"([^"]+)"')


def norm(path, name):
    return (path.strip("/"), " ".join(name.split()).lower())


def store_id():
    m = re.search(r"^id:\s*(\S+)", (ROOT / ".openspec-store" / "store.yaml").read_text(), re.M)
    return m.group(1) if m else None


def main_checkout():
    # A linked worktree shares the main checkout's git dir; its parent is the
    # main checkout, whose siblings are the implementing repositories.
    res = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return ROOT
    common = pathlib.Path(res.stdout.strip())
    return common.parent if common.name == ".git" else ROOT


def implementing_repos():
    sid = store_id()
    base = main_checkout()
    repos = []
    for d in base.parent.iterdir():
        cfg = d / "openspec" / "config.yaml"
        if d not in (ROOT, base) and cfg.is_file() and sid and re.search(rf"^store:\s*{re.escape(sid)}\s*$", cfg.read_text(), re.M):
            repos.append(d)
    return repos


def scenarios(change_dir):
    out = []
    specs = change_dir / "specs"
    for spec in sorted(specs.rglob("spec.md")):
        cap = spec.parent.relative_to(specs).as_posix()
        op = None
        for line in spec.read_text().splitlines():
            m = DELTA.match(line)
            if m:
                op = m.group(1)
                continue
            m = SCENARIO.match(line)
            if m and op in ("ADDED", "MODIFIED"):
                out.append((cap, m.group(1)))
    return out


def is_test_file(rel_parts):
    return bool(TEST_FILE.search(rel_parts[-1]) or TEST_DIRS & set(rel_parts[:-1]))


def worktree_texts(repo):
    for p in repo.rglob("*"):
        if not p.is_file() or SKIP_DIRS & set(p.parts):
            continue
        if is_test_file(p.relative_to(repo).parts):
            try:
                yield p.read_text(errors="ignore")
            except OSError:
                continue


def has_ref(repo, ref):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
                          capture_output=True).returncode == 0


def ref_texts(repo, ref):
    # Only files that mention @spec are read, so the search stays cheap on large repositories.
    grep = subprocess.run(["git", "-C", str(repo), "grep", "-I", "-l", "-F", "@spec", ref, "--"],
                          capture_output=True, text=True)
    for line in grep.stdout.splitlines():
        path = line.split(":", 1)[1]
        if is_test_file(tuple(path.split("/"))):
            yield subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                                 capture_output=True, text=True, errors="ignore").stdout


def annotations(sources, pattern):
    found = set()
    for texts in sources:
        for text in texts:
            found.update(norm(a, b) for a, b in pattern.findall(text))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("change")
    ap.add_argument("--repos", nargs="*", type=pathlib.Path)
    ap.add_argument("--worktree", action="store_true",
                    help="search sibling checkouts as they are on disk instead of at origin/main")
    args = ap.parse_args()

    change_dir = ROOT / "openspec" / "changes" / args.change
    if not change_dir.is_dir():
        sys.exit(f"no such change: {change_dir}")
    wanted = scenarios(change_dir)
    if not wanted:
        print(f"{args.change}: no added or modified scenarios")
        return
    if args.repos:
        searched = [(r, r.name, worktree_texts(r)) for r in args.repos]
    else:
        searched = []
        for r in implementing_repos():
            if not args.worktree and has_ref(r, "origin/main"):
                searched.append((r, f"{r.name}@origin/main", ref_texts(r, "origin/main")))
            else:
                searched.append((r, r.name, worktree_texts(r)))
    covered = annotations((texts for _, _, texts in searched), ANNOTATION)
    manual = set()
    for f in change_dir.glob("*.md"):
        manual.update(norm(a, b) for a, b in MANUAL.findall(f.read_text()))

    missing = [(c, s) for c, s in wanted if norm(c, s) not in covered and norm(c, s) not in manual]
    print(f"{args.change}: {len(wanted) - len(missing)}/{len(wanted)} scenarios covered "
          f"(searched {', '.join(label for _, label, _ in searched) or 'no repositories'})")
    if missing:
        print("scenarios with no test carrying `@spec <capability-path> \"<scenario name>\"`:")
        for c, s in missing:
            print(f'  @spec {c} "{s}"')
        sys.exit(1)


if __name__ == "__main__":
    main()
