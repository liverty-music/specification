#!/usr/bin/env bash
# Open an OpenSpec workset in VS Code for plan-change step 6.
# Usage: open-workset.sh --check     exit 0 and print VS Code's bin directory, or exit 1 when there is none
#        open-workset.sh <workset>   open the workset in a new VS Code window
set -euo pipefail

code_dir() {
  if command -v code >/dev/null; then dirname "$(command -v code)"; return; fi
  # Under WSL, Bash started from VS Code often lacks `code` on PATH; use the Windows install. A glob,
  # not `ls`: `ls` is often aliased to a tool that quotes paths with spaces.
  for d in /mnt/c/Users/*/AppData/Local/Programs/"Microsoft VS Code"/bin; do
    if [ -x "$d/code" ]; then echo "$d"; return; fi
  done
  return 1
}

dir=$(code_dir) || { echo "no VS Code 'code' command found" >&2; exit 1; }
if [ "${1:-}" = --check ]; then echo "$dir"; exit 0; fi

# Bash inherits the extension host's Electron variables, which crash the new window's extension host.
PATH="$dir:$PATH" exec env -u ELECTRON_RUN_AS_NODE -u VSCODE_ESM_ENTRYPOINT -u VSCODE_HANDLES_SIGPIPE \
  -u VSCODE_HANDLES_UNCAUGHT_ERRORS -u VSCODE_NLS_CONFIG -u VSCODE_L10N_BUNDLE_LOCATION \
  -u VSCODE_RECONNECTION_GRACE_TIME openspec workset open "$1"
