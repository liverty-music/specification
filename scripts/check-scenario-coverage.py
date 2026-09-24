#!/usr/bin/env python3
"""Archive gate: every scenario a change adds or modifies is covered by a test.

A test covers a scenario by carrying the annotation

    @spec <capability-path> "<scenario name>"

in a comment or in its name, e.g.

    // @spec components/entity/order/create "Second create for the same cart"

The scenarios checked are those under `## ADDED Requirements` and
`## MODIFIED Requirements` in the change's delta specs. The annotations are
searched in the test files of the implementing repositories: every sibling
checkout of this store whose `openspec/config.yaml` points at this store
(`store: <id>`), or the directories given with --repos.

A scenario that cannot be verified by an automated test is exempted by a line
anywhere in the change's own files (proposal, design, tasks):

    @spec-manual <capability-path> "<scenario name>" -- <how it is verified>

Usage: check-scenario-coverage.py <change> [--repos DIR ...]
Exit status 1 lists the uncovered scenarios."""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST_FILE = re.compile(r"(_test\.go|\.(test|spec)\.[cm]?[jt]sx?|_test\.py|test_[^/]*\.py)$")
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


def implementing_repos():
    sid = store_id()
    repos = []
    for d in ROOT.parent.iterdir():
        cfg = d / "openspec" / "config.yaml"
        if d != ROOT and cfg.is_file() and sid and re.search(rf"^store:\s*{re.escape(sid)}\s*$", cfg.read_text(), re.M):
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


def test_files(repo):
    for p in repo.rglob("*"):
        if not p.is_file() or SKIP_DIRS & set(p.parts):
            continue
        rel = p.relative_to(repo).parts
        if TEST_FILE.search(p.name) or TEST_DIRS & set(rel[:-1]):
            yield p


def annotations(repos, pattern):
    found = set()
    for repo in repos:
        for f in test_files(repo):
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            found.update(norm(a, b) for a, b in pattern.findall(text))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("change")
    ap.add_argument("--repos", nargs="*", type=pathlib.Path)
    args = ap.parse_args()

    change_dir = ROOT / "openspec" / "changes" / args.change
    if not change_dir.is_dir():
        sys.exit(f"no such change: {change_dir}")
    wanted = scenarios(change_dir)
    if not wanted:
        print(f"{args.change}: no added or modified scenarios")
        return
    repos = args.repos if args.repos else implementing_repos()
    covered = annotations(repos, ANNOTATION)
    manual = set()
    for f in change_dir.glob("*.md"):
        manual.update(norm(a, b) for a, b in MANUAL.findall(f.read_text()))

    missing = [(c, s) for c, s in wanted if norm(c, s) not in covered and norm(c, s) not in manual]
    print(f"{args.change}: {len(wanted) - len(missing)}/{len(wanted)} scenarios covered "
          f"(searched {', '.join(r.name for r in repos) or 'no repositories'})")
    if missing:
        print("scenarios with no test carrying `@spec <capability-path> \"<scenario name>\"`:")
        for c, s in missing:
            print(f'  @spec {c} "{s}"')
        sys.exit(1)


if __name__ == "__main__":
    main()
