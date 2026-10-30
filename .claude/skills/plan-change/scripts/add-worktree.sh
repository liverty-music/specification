#!/usr/bin/env bash
# Create or reuse one implementation worktree for plan-change step 6.
# Usage: add-worktree.sh <repo-checkout> <worktree-path> <branch>
# Prints "created", "attached" (existing branch, new directory) or "reused" (existing directory), then how
# far the worktree is behind origin/main. Never deletes or resets anything.
set -euo pipefail

R=$1 W=$2 B=$3
git -C "$R" fetch -q origin

if [ -d "$W" ]; then
  echo "reused $W"
else
  if git -C "$R" show-ref --verify --quiet "refs/heads/$B"; then
    git -C "$R" worktree add -q "$W" "$B"
    echo "attached $W ($B)"
  else
    git -C "$R" worktree add -q "$W" -b "$B" origin/main
    echo "created $W ($B)"
  fi
  # Copy the gitignored files .worktreeinclude lists, as `claude --worktree` would. Only into a new
  # directory: a reused worktree keeps its own copies.
  if [ -f "$R/.worktreeinclude" ]; then
    (cd "$R" && git ls-files --others --ignored --exclude-from=.worktreeinclude \
      | while read -r f; do mkdir -p "$(dirname "$W/$f")"; cp -p "$f" "$W/$f"; echo "copied $f"; done)
  fi
fi

echo "behind origin/main: $(git -C "$W" rev-list --count HEAD..origin/main)"
