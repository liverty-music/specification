---
name: plan-change
description: Takes a liverty-music change from idea to a ready-to-implement workspace in one run - writes the OpenSpec change with openspec-propose, opens and merges its plan PR from a worktree, syncs the store checkout, then creates one worktree per affected repository and opens them together as an OpenSpec workset in VS Code. Use this whenever the user wants to plan a new change and start working on it ("propose して PR して workset まで", "change を作って実装を始められる状態にして", "plan PR を出して workset を開いて", "/plan-change <idea>"), or asks for any two of propose / plan PR / workset in sequence. It stops before the push to show the change for approval only when the user has not already agreed to its content in the conversation. For only writing artifacts use openspec-propose; for only opening a workset of a merged change, start at step 6 of this skill.
---

# Plan a change and launch its workset

The routine after an idea is agreed is always the same: write the change, get it reviewed and merged on
`main`, then open the implementation worktrees. This skill runs it end to end. The user steps in at most once,
to approve the change before it leaves the machine, and not at all when they already agreed to its content.

```
propose (store checkout) -> plan worktree -> commit -> pre-push-review -> [approval unless agreed] -> push
  -> PR -> CI / review loop -> merge -> sync store -> worktrees -> workset -> VS Code
```

The procedures behind each step are in `README.md` ("Lifecycle of a change", "Branch work in this repository",
"Local: parallel work with worktrees") and `openspec/AGENTS.md`. Read them when a step below is unclear; this
skill only fixes the order, the names and the one possible stop.

Names used below: `<store>` is this specification checkout's absolute path (the store, always on `main`),
`<repos>` its parent directory (the four repositories side by side), `<change>` the kebab-case change name.
Write them as literal values in every command: each fenced block runs as its own Bash call, and neither shell
variables nor `cd` carry over from one call to the next.

## 1. Pre-flight

- `git -C "<store>" fetch origin && git -C "<store>" merge --ff-only origin/main`. Use `merge --ff-only`, never
  `git pull`: the store's working tree holds other changes' uncommitted progress, and a rebase with autostash
  can mix it up. If the fast-forward stops, report why and stop; another change's owner has to sync first.
- `openspec list --json` must show a `root`. If it does not, stop and report (see the openspec-propose skill).
- Pick `<change>`: a verb phrase in kebab-case naming the outcome (`narrow-artist-image-refresh`), that no
  folder in `openspec/changes/` or `openspec/changes/archive/` uses yet.

## 2. Write the change

Invoke the `openspec-propose` skill for `<change>` with the idea from the conversation. It writes
`openspec/changes/<change>/` in the store checkout. Follow its rules, the schema's artifact instructions, and
the project rules it points to (`openspec/AGENTS.md`, `rpc-design` for any RPC naming). Split `tasks.md` by
repository (README step 1): step 6 reads those sections to decide which worktrees to create.

Run `openspec validate <change> --strict` in the store checkout and fix every error before going on.

## 3. Plan worktree and commit

```bash
git -C "<store>" worktree add "<store>/.claude/worktrees/<change>-plan" -b <change>-plan origin/main
cd "<store>/.claude/worktrees/<change>-plan"
cp -r "<store>/openspec/changes/<change>" openspec/changes/
openspec validate <change> --strict
git add openspec/changes/<change>
```

Commit in the plan worktree with the git-commit-formatter rules, naming the directory on the command itself
(`git -C "<store>/.claude/worktrees/<change>-plan" commit ...`): the next Bash call starts in the store
checkout on `main`. This repository's plan commits read `docs(openspec): plan <change>`. The commit hooks run here, so a rejected commit means a real problem to fix.

From now on, **edit only in the plan worktree**. The store copy is retired at step 5, so a fix made there
would be lost, and a fix made only in the worktree is exactly what lands on `main`.

## 4. Review, then stop only for content not yet agreed

1. Run the `pre-push-review` skill on the plan worktree's range. Fix each accepted finding in the worktree and
   commit it; review the fix range again as that skill says.
2. **Decide whether to stop.** Everything after this step is outward-facing (a PR on a public repository, a
   merge to `main`, an auto-run of downstream jobs), so the change must leave the machine with content the
   user agreed to. Agreement given earlier in the conversation counts; asking again for the same content only
   adds a round trip.
   - **Go on to step 5 without stopping** when the user agreed to the change's content earlier in the
     conversation (an html-plan response, an explicit OK on the proposal or on its decisions) and every
     commit since then only makes the artifacts consistent with what was agreed: review fixes that resolve a
     contradiction, a stale Purpose, a missing case of an agreed rule. Points you raised that the user left
     unanswered do not block; list them in the step 7 report so they can be changed during implementation.
   - **Stop** when the user agreed to nothing yet (the skill started from an idea alone), or when a fix
     changes behaviour the user agreed to (a different screen, rule, wording or scope). Show:
     - the change name and one paragraph of what it does and why (from proposal.md);
     - the capabilities it adds, modifies and removes;
     - `tasks.md` section by section, with the repositories each section touches;
     - the pre-push-review table (findings, decisions, fixes);
     - for MODIFIED / REMOVED / RENAMED requirements, the relevant part of `openspec show <change> --diff`;
     - the worktrees step 6 will create, and which one opens first.

     Ask a direct yes/no question and wait. If the user asks for edits, make them in the worktree, commit,
     rerun pre-push-review on the new commits, and show the change again. Silence or an answer to some other
     question is not approval.

If pre-push-review cannot run, stop even when the content is agreed: say why and let the user decide whether
to push without it.

## 5. Push, PR, merge, sync

After approval:

1. Push from the plan worktree (`git -C "<store>/.claude/worktrees/<change>-plan" push -u origin HEAD`; a new
   shell starts in the store checkout on `main`, so never rely on an earlier `cd`) and open the PR in the same
   command line, `cd "<store>/.claude/worktrees/<change>-plan" && gh pr create ...`, as the `pull-request` skill
   describes (its feature-branch check must see `<change>-plan`, not `main`): the repository's PR template, `--assignee pannpers`, the body from a file. Fill *OpenSpec Traceability* with
   `OpenSpec-Change: <change>` and the store commit (`git -C "<store>" rev-parse --short origin/main`). When the change
   has MODIFIED, REMOVED or RENAMED requirements, append `openspec show <change> --diff` from
   "Specifications Changed (diffs)" onward in a collapsed `<details>` block (`openspec/AGENTS.md`).
   Proto files in a plan PR are unusual; if the change carries them, they go in a separate proto PR (README
   step 3), not here.
2. Run the pull-request skill's readiness loop: CI, conflicts, review comments (bot reviews included,
   through react-review). Merge with a merge commit once every gate holds; merging liverty-music PRs on green
   CI is allowed. Quote the merged state from `gh pr view <n> --json state,mergedAt,mergeCommit`.
3. Sync the store. The store copy has no progress yet (nothing has been applied), and the merged copy is the
   reviewed one, so retire the store copy instead of restoring it on top:

   ```bash
   S="<store>"; C="<change>"; K="$HOME/.cache/$C-plan-store-copy"
   cd "$S" && git fetch origin && mkdir -p ~/.cache || exit 1
   [ ! -e "$K" ] || { echo "leftover $K from an aborted run: inspect it, then remove it" >&2; exit 1; }
   mv "openspec/changes/$C" "$K" || exit 1
   git merge --ff-only origin/main || { mv "$K" "openspec/changes/$C"; echo "fast-forward stopped; store copy restored" >&2; exit 1; }
   diff -r "$K" "openspec/changes/$C"   # differences = the review fixes
   git worktree remove ".claude/worktrees/$C-plan" && git branch -d "$C-plan"
   ```

   When the fast-forward stops, the block puts the store copy back and leaves the plan worktree in place;
   report why (README "Branch work in this repository": usually another change's plan waiting to be synced)
   and stop. Otherwise read the `diff` output: every difference should be a fix made in steps 4 and 5.
   Anything else (for example a `tasks.md` check-off someone made in the store meanwhile) is real progress;
   copy it back and say so. Then delete the `~/.cache` copy.

## 6. Worktrees and workset

This step needs VS Code's `code` command on the local machine. Check with the bundled script, which looks on
PATH and then, under WSL, for the Windows install:

```bash
bash "<store>/.claude/skills/plan-change/scripts/open-workset.sh" --check
```

When it exits 1 (a cloud thread, or no VS Code), stop here and report the merged PR and the worktrees the
user would create.

1. **Repositories.** Read the section headings and task lines of the merged `tasks.md`. A repository is in when
   a task changes it: `specification` for proto files (`proto/`), `backend`, `frontend`, `cloud-provisioning`.
   Tasks that only edit OpenSpec artifacts or check prod read-only do not need a worktree. If a section's
   repository is unclear, ask rather than guess.
2. **Worktrees**, each cut from the repository's latest `origin/main`:

   | repository | `R` (checkout) | `W` (worktree path) | `B` (branch) | workset member |
   |---|---|---|---|---|
   | specification (proto) | `<store>` | `<store>/.claude/worktrees/<change>-proto` | `worktree-<change>-proto` | `specification-proto` |
   | backend / frontend / cloud-provisioning | `<repos>/<repo>` | `<repos>/<repo>/.claude/worktrees/<change>` | `worktree-<change>` | `<repo>` |

   For each row, run the bundled script with the row's literal values:

   ```bash
   bash "<store>/.claude/skills/plan-change/scripts/add-worktree.sh" <R> <W> <B>
   ```

   It creates the worktree from `origin/main`, attaches an existing branch, or reuses an existing directory,
   and never deletes or resets one, since it may hold someone's work. Only a new worktree directory gets the
   gitignored files the repository's `.worktreeinclude` lists (what `claude --worktree` would have copied).
   Report each line it prints, including how far a reused worktree is behind `origin/main`.

3. **Workset.** The first member is where VS Code's terminal and the Claude panel start, so it is where work
   starts: the proto worktree when the change has proto tasks (proto first, README step 3), otherwise the
   repository of the first implementation section of `tasks.md`. The store checkout is always the last
   member, named `store`, so `/opsx:apply` progress is visible.

   ```bash
   openspec workset create <change> --tool code \
     --member <first>=<path> [--member <repo>=<path> ...] --member store="<store>"
   ```

   If a workset of that name exists, show its members and ask before replacing it.
4. **Open it** with the bundled script, which puts `code` on PATH and strips the extension host's Electron
   variables that Bash inherits (they crash the new window's extension host):

   ```bash
   bash "<store>/.claude/skills/plan-change/scripts/open-workset.sh" <change>
   ```

   The window is open only when `Opening '<change>' in VS Code` is printed.

## 7. Report

Tell the user, in their language:

- the merged plan PR as a Markdown link, with the quoted merged state;
- the pre-push-review table (findings, decisions, fixes) and the sync `diff` result;
- when step 4 did not stop: the points raised earlier that the user left unanswered;
- the workset table (member, path, branch, which tasks it serves) and the line that confirmed the window;
- the first command to run in the new window: `/opsx:apply <change>` in the first member, and, when the
  change has proto tasks, that backend and frontend build against the new types only after the proto release
  and BSR generation.
