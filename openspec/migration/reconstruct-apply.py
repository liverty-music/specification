#!/usr/bin/env python3
"""After reconstruct agents finish: remove OUT requirement blocks from main
specs, delete specs left with no requirements, fill resolved_to, verify
conservation. Dry-run unless --apply. Hard-fails on malformed reports,
key mismatches, or any leftover migration marker in archived files."""
import csv, glob, os, re, sys, shutil, collections, subprocess
M = "openspec/migration"; S = "openspec/specs"; A = "openspec/changes/archive"
APPLY = "--apply" in sys.argv
# Optional overrides so a later batch can be applied on its own:
#   --batches <json>  --reports <glob>  --expect <total scenarios>
def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
BATCHES = opt("--batches", f"{M}/reconstruct-batches.json")
REPORTS = opt("--reports", f"{M}/reconstruct/reconstruct-*.tsv")
EXPECT = int(opt("--expect", "3588"))
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))
def wr(p, rows, fields):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
fails = []
# 1. reports: strict columns + key coverage against batches
import json
batches = json.load(open(BATCHES, encoding="utf-8"))
expected = {(ch, r["old_spec"], r["old_req_name"]) for b in batches.values() for ch, rows in b.items() for r in rows}
reports = []
for f in sorted(glob.glob(REPORTS)):
    lines = open(f, encoding="utf-8").read().rstrip("\n").split("\n"); n = lines[0].count("\t") + 1
    bad = [i for i, l in enumerate(lines[1:], 2) if l.count("\t") + 1 != n]
    if bad: fails.append(f"MALFORMED {f}: rows {bad[:5]}"); continue
    reports += rd(f)
got = {(r["change"], r["old_spec"], r["old_req_name"].strip()) for r in reports}
missing = expected - got; extra = got - expected
print(f"reports: {len(reports)} rows from {len(glob.glob(REPORTS))} files; expected {len(expected)}; missing {len(missing)}; extra {len(extra)}")
if missing: fails.append(f"{len(missing)} assigned requirements have no report"); [print("  missing:", m) for m in list(missing)[:10]]
if extra: fails.append(f"{len(extra)} report rows not assigned"); [print("  extra:", e) for e in list(extra)[:10]]
# 2. no migration markers leaked into archives
changed = subprocess.run(f"git diff --name-only -- {A}", shell=True, capture_output=True, text=True).stdout.split()
changed = [f for f in changed if f.endswith(("design.md", "proposal.md")) and os.path.exists(f)]
leak = [f for f in changed if re.search(r"migrated from spec|moved from spec|migration marker|moved here during|relocated during|as part of (the )?migration", open(f, encoding="utf-8").read(), re.I)]
if leak: fails.append(f"migration markers found in {len(leak)} archived files"); [print("  leak:", l) for l in leak[:10]]
# 3. delta specs: no reported-removed requirement should still exist in its delta
still = []
for r in reports:
    p = f"{A}/{r['change']}/specs/{r['old_spec']}/spec.md"
    if os.path.exists(p) and re.search(r"^### Requirement:\s*" + re.escape(r["old_req_name"].strip()) + r"\s*$", open(p, encoding="utf-8").read(), re.M): still.append((r["change"], r["old_spec"], r["old_req_name"]))
if still: fails.append(f"{len(still)} requirements still present in deltas"); [print("  still:", s) for s in still[:10]]
if fails:
    print("\nFAIL:"); [print("  -", x) for x in fails]; sys.exit(1)
# 4. main-spec removal set = reported rows + untraced OUT rows
untraced = rd(f"{M}/reconstruct-untraced.tsv")
to_remove = collections.defaultdict(set)
for r in reports: to_remove[r["old_spec"]].add(r["old_req_name"].strip())
for r in untraced: to_remove[r["old_spec"]].add(r["old_req_name"].strip())
sc = collections.Counter((r["old_spec"], r["old_req_name"].strip()) for r in rd(f"{M}/scenarios.tsv"))
removed_req = removed_sc = 0; emptied = []
for spec, names in sorted(to_remove.items()):
    p = f"{S}/{spec}/spec.md"
    if not os.path.exists(p): print("  (already gone)", spec); continue
    s = open(p, encoding="utf-8").read()
    parts = re.split(r"(?=^### Requirement:)", s, flags=re.M); head, blocks = parts[0], parts[1:]
    keep = []
    for b in blocks:
        name = re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1)
        if name in names: removed_req += 1; removed_sc += sc[(spec, name)]
        else: keep.append(b)
    if not keep: emptied.append(spec)
    if APPLY:
        if keep: open(p, "w", encoding="utf-8").write(head + "".join(keep).rstrip("\n") + "\n")
        else: shutil.rmtree(f"{S}/{spec}")
print(f"main specs: remove {removed_req} requirements / {removed_sc} scenarios; {len(emptied)} specs become empty and are deleted")
# 5. ledger resolved_to
req = rd(f"{M}/requirements.tsv"); fields = list(req[0].keys())
if "resolved_to" not in fields: fields.append("resolved_to")
ridx = {(r["change"], r["old_spec"], r["old_req_name"].strip()): r for r in reports}
n = 0
for r in req:
    r.setdefault("resolved_to", "")
    k = (r.get("origin_change", ""), r["old_spec"], r["old_req_name"].strip())
    if k in ridx: r["resolved_to"] = f"{A}/{k[0]}/design.md ({ridx[k]['design_section']})"; n += 1
    elif r["disposition"].startswith("OUT:") and not r.get("origin_change") and not r["resolved_to"]: r["resolved_to"] = "git-history (untraced)"; n += 1
if APPLY: wr(f"{M}/requirements.tsv", req, fields)
print(f"ledger: resolved_to set on {n} rows")
# 6. conservation: main-spec scenarios + resolved scenarios == EXPECT
if APPLY:
    main_sc = sum(1 for f in glob.glob(f"{S}/*/spec.md") for l in open(f, encoding="utf-8") if l.startswith("#### Scenario:"))
    res_sc = sum(sc[(r["old_spec"], r["old_req_name"].strip())] for r in req if r.get("resolved_to"))
    print(f"conservation: main {main_sc} + resolved {res_sc} = {main_sc + res_sc} (expect {EXPECT})")
    if main_sc + res_sc != EXPECT: print("FAIL: conservation broken"); sys.exit(1)
    out = subprocess.run("openspec validate --specs --json", shell=True, capture_output=True, text=True).stdout
    print("validate --specs:", json.loads(out)["summary"]["totals"])
else:
    print("(dry run — pass --apply)")
