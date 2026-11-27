#!/usr/bin/env python3
"""Remove the worktrees that finished changes left behind.

Looks at `<repo>/.claude/worktrees/*` in the store's main checkout and in every
sibling checkout whose `openspec/config.yaml` points at the store. A worktree is
removed only when removing it loses nothing and nobody is using it:

- its branch has a merged pull request and no open one;
- HEAD is contained in origin/main or in a merged pull request's head;
- it is not locked and has no uncommitted or untracked file;
- every ignored file in it can be regenerated, or is identical to the file at
  the same path in the repository's main checkout;
- its change is no longer an active change on the store's origin/main, and when
  it belongs to no archived change either (ad-hoc work), its pull request
  merged more than 24 hours ago;
- no worktree of the same change is in use: a process has its working
  directory or an open file there, VS Code watches it, or a Claude session
  there wrote its transcript in the last 24 hours.

After removing, it also removes each saved OpenSpec workset of a change that is
not active and whose worktrees are all gone. Branches are never deleted.

Usage: sweep-worktrees.py [--apply]   (without --apply it only reports)
Exit status 1 means a removal or a check failed. Run it on a local machine: the
in-use checks read /proc."""
import argparse
import datetime
import filecmp
import glob
import json
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Ignored paths that a build, a test run or a download recreates.
REGENERABLE = re.compile(
    r"(^|/)(node_modules|dist[\w-]*|coverage[\w.-]*|test-results|playwright-report|storybook-static|"
    r"\.vitest-attachments|\.vite|\.cache|\.turbo|bin|tmp|__pycache__)(/|$)"
    r"|^k8s/.*/charts/$|\.(pyc|tsbuildinfo)$")
CHANGE_SUFFIX = re.compile(r"-(proto\d*|plan|archive)$")
RECENT_SECONDS = 24 * 60 * 60


def run(*cmd, check=True):
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if check and res.returncode != 0:
        sys.exit(f"error: {' '.join(map(str, cmd))}\n{res.stderr.strip()}")
    return res


def git(repo, *args, check=True):
    return run("git", "-C", str(repo), *args, check=check)


def main_checkout():
    common = pathlib.Path(git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    return common.parent


def repositories(store):
    sid = re.search(r"^id:\s*(\S+)", (store / ".openspec-store" / "store.yaml").read_text(), re.M).group(1)
    repos = [store]
    for d in sorted(store.parent.iterdir()):
        cfg = d / "openspec" / "config.yaml"
        if d != store and cfg.is_file() and re.search(rf"^store:\s*{re.escape(sid)}\s*$", cfg.read_text(), re.M):
            repos.append(d)
    return repos


def worktrees(repo):
    prefix = f"{repo}/.claude/worktrees/"
    for block in git(repo, "worktree", "list", "--porcelain").stdout.strip().split("\n\n"):
        fields = dict((line.split(" ", 1) + [""])[:2] for line in block.splitlines())
        if fields["worktree"].startswith(prefix):
            yield fields


def change_of(path):
    return CHANGE_SUFFIX.sub("", os.path.basename(path))


def in_use(paths):
    """Map each worktree path somebody is using to the reason."""
    used = {}
    inodes = {os.stat(p).st_ino: p for p in paths if os.path.isdir(p)}
    inside = re.compile("(" + "|".join(map(re.escape, sorted(paths, key=len, reverse=True))) + r")(?=/|\x00|$)")
    for proc in glob.glob("/proc/[0-9]*"):
        if int(proc[6:]) == os.getpid():
            continue
        links = []
        for link in [proc + "/cwd", *glob.glob(proc + "/fd/*")]:
            try:
                links.append(os.readlink(link))
            except OSError:
                pass
        for target in links:
            m = inside.match(target)
            if m:
                used[m.group(1)] = f"used by process {proc[6:]}"
        try:
            if b"type=fileWatcher" not in pathlib.Path(proc, "cmdline").read_bytes():
                continue
        except OSError:
            continue
        # A window that opened the store also watches the store's own worktrees
        # unless files.watcherExclude skips them, so this errs towards keeping.
        for info in glob.glob(proc + "/fdinfo/*"):
            try:
                text = pathlib.Path(info).read_text()
            except OSError:
                continue
            for ino in re.findall(r"^inotify wd:\w+ ino:(\w+)", text, re.M):
                path = inodes.get(int(ino, 16))
                if path:
                    used[path] = "watched by a VS Code window"
    for path in paths:
        slug = re.sub(r"[^A-Za-z0-9]", "-", path)
        logs = glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}/*.jsonl"))
        if logs and time.time() - max(map(os.path.getmtime, logs)) < RECENT_SECONDS:
            used[path] = "Claude session in the last 24 hours"
    return used


def irreplaceable(repo, path):
    """Ignored files that exist only in this worktree."""
    out = git(path, "status", "--porcelain", "-z", "--ignored").stdout
    lost = []
    for entry in out.split("\0"):
        if not entry.startswith("!! ") or REGENERABLE.search(entry[3:]):
            continue
        rel = entry[3:]
        here = pathlib.Path(path, rel)
        files = [f for f in here.rglob("*") if f.is_file()] if here.is_dir() else [here]
        for f in files:
            twin = repo / f.relative_to(path)
            if REGENERABLE.search(str(f.relative_to(path))):
                continue
            if not (twin.is_file() and filecmp.cmp(f, twin, shallow=False)):
                lost.append(str(f.relative_to(path)))
    return lost


def pull_requests(repo):
    out = run("gh", "pr", "list", "-R", git(repo, "remote", "get-url", "origin").stdout.strip(),
              "--state", "all", "--limit", "2000", "--json", "headRefName,headRefOid,mergedAt,state").stdout
    prs = {}
    for pr in json.loads(out):
        prs.setdefault(pr["headRefName"], []).append(pr)
    return prs


def merged_recently(pr):
    merged = datetime.datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
    return time.time() - merged.timestamp() < RECENT_SECONDS


def keep_reason(repo, tree, prs, active, archived):
    path, head = tree["worktree"], tree["HEAD"]
    mine = prs.get(tree.get("branch", "").removeprefix("refs/heads/"), [])
    merged_prs = [pr for pr in mine if pr["state"] == "MERGED"]
    merged = [pr["headRefOid"] for pr in merged_prs]
    if not merged:
        return "no merged pull request"
    if any(pr["state"] == "OPEN" for pr in mine):
        return "open pull request"
    if "locked" in tree:
        return "locked"
    if not os.path.isdir(path):
        return "directory is missing (run git worktree prune)"
    change = change_of(path)
    if change in active:
        return f"change {change} is not archived"
    if change not in archived and any(map(merged_recently, merged_prs)):
        return "belongs to no archived change and merged less than 24 hours ago"
    if git(path, "status", "--porcelain").stdout:
        return "uncommitted or untracked files"
    if not any(git(repo, "merge-base", "--is-ancestor", head, c, check=False).returncode == 0
               for c in ["origin/main", *merged]):
        return "commits that no merged pull request contains"
    lost = irreplaceable(repo, path)
    if lost:
        return f"{len(lost)} ignored file(s) found only here, e.g. {lost[0]}"
    return None


def remove_worksets(apply, active):
    listed = json.loads(run("openspec", "workset", "list", "--json").stdout)["worksets"]
    for ws in listed:
        trees = [m["path"] for m in ws["members"] if "/.claude/worktrees/" in m["path"]]
        if ws["name"] not in active and trees and not any(os.path.exists(p) for p in trees):
            print(f"{'remove' if apply else 'would remove'} workset {ws['name']}")
            if apply:
                run("openspec", "workset", "remove", ws["name"], "--yes")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="remove; without it, only report")
    args = parser.parse_args()
    if not os.path.isdir("/proc/self/fd"):
        sys.exit("error: the in-use checks need /proc")

    store = main_checkout()
    repos = repositories(store)
    for repo in repos:
        git(repo, "fetch", "--quiet", "origin")
    listed = git(store, "ls-tree", "-d", "--name-only", "origin/main", "openspec/changes/").stdout.split()
    active = {os.path.basename(p) for p in listed} - {"archive"}
    dated = git(store, "ls-tree", "-d", "--name-only", "origin/main", "openspec/changes/archive/").stdout.split()
    archived = {re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(p)) for p in dated}
    trees = [(repo, tree) for repo in repos for tree in worktrees(repo)]
    if not trees:
        used = {}
    else:
        used = in_use([tree["worktree"] for _, tree in trees])
    busy = {change_of(p): f"{os.path.basename(p)}: {why}" for p, why in used.items()}

    failed = 0
    prs = {repo: pull_requests(repo) for repo in repos}
    for repo, tree in trees:
        path = tree["worktree"]
        name = f"{repo.name}/{os.path.basename(path)}"
        reason = keep_reason(repo, tree, prs[repo], active, archived)
        if not reason and change_of(path) in busy:
            reason = f"in use ({busy[change_of(path)]})"
        if reason:
            print(f"keep   {name}: {reason}")
        elif not args.apply:
            print(f"would remove {name}")
        else:
            res = git(repo, "worktree", "remove", path, check=False)
            if res.returncode == 0:
                print(f"remove {name}")
            else:
                failed += 1
                print(f"FAILED {name}: {res.stderr.strip()}")
    remove_worksets(args.apply, active)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
