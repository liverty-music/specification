#!/usr/bin/env bash
# Phase 3 verification: swap specs.next into a throwaway worktree and run the
# real openspec CLI against it. openspec/specs in the main checkout is never touched.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
WT="$(mktemp -d "${TMPDIR:-/tmp}/specs-next-check.XXXXXX")"
cleanup() { git -C "$ROOT" worktree remove --force "$WT" >/dev/null 2>&1 || true; rm -rf "$WT"; }
trap cleanup EXIT
git -C "$ROOT" worktree add --detach "$WT" HEAD >/dev/null 2>&1
rm -rf "$WT/openspec/specs"
cp -r "$ROOT/openspec/specs.next" "$WT/openspec/specs"
rm -rf "$WT/openspec/specs.next"
cd "$WT"
echo "=== C4: no depth-1 spec.md (flat layout must be gone) ==="
flat=$(find openspec/specs -mindepth 2 -maxdepth 2 -name spec.md | wc -l); echo "depth-1 specs: $flat"; [ "$flat" -eq 0 ]
echo "=== C1: openspec validate --specs --strict ==="
openspec validate --specs --strict --json > /tmp/strict.json 2>/tmp/strict.err || true
python3 - <<'PY'
import json
d=json.load(open("/tmp/strict.json")); t=d["summary"]["totals"]; print(t)
fails=[i for i in d.get("items",[]) if not i.get("valid",True)]
for i in fails[:20]:
    print(" ", i.get("id") or i.get("name"), "|", "; ".join(f"{x.get('level')}: {x.get('message')}" for x in i.get("issues",[])[:3]))
raise SystemExit(1 if t["failed"] else 0)
PY
echo "=== C3: openspec list --specs (nested ids resolve) ==="
openspec list --specs --json | python3 -c "import sys,json; d=json.load(sys.stdin); items=d if isinstance(d,list) else d.get('specs',d.get('items',[])); print('listed specs:',len(items))"
echo "=== C2: active changes still validate against the new tree ==="
openspec validate --changes --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['summary']['totals'])"
echo "PHASE 3 VERIFY OK"
