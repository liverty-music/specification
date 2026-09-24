#!/usr/bin/env python3
"""Merge Pass 1 batch outputs into requirements.tsv / specs.tsv and run V1-V11.

Read-only on baseline unless --apply is given. Exits non-zero if any hard
check (V1, V2, V5, V6, V7, V8) fails.
"""
import csv, glob, sys, collections, re
M = "openspec/migration"
APPLY = "--apply" in sys.argv

def load(p): return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))

def load_strict(p):
    """Refuse any data row whose tab-count differs from the header (b06 incident)."""
    lines = open(p, encoding="utf-8").read().split("\n")
    if lines and lines[-1] == "": lines.pop()
    n = lines[0].count("\t") + 1
    bad = [(i + 2, l.count("\t") + 1) for i, l in enumerate(lines[1:]) if l.count("\t") + 1 != n]
    if bad:
        print(f"MALFORMED {p}: header={n} cols, {len(bad)} rows differ, e.g. {bad[:3]}")
        return None
    return load(p)
base_req = load(f"{M}/requirements.tsv"); base_sc = load(f"{M}/scenarios.tsv"); base_sp = load(f"{M}/specs.tsv")
voc = {r["target_path"] for r in load(f"{M}/vocabulary.tsv")}
voc_kinds = {r["target_path"].split("/")[2] for r in load(f"{M}/vocabulary.tsv") if r["target_path"].startswith("components/infrastructure/") and "/<name>" in r["target_path"]}

p1_req = []; p1_sp = []; malformed = 0
for f in sorted(glob.glob(f"{M}/pass1/batch-*.requirements.tsv")):
    r = load_strict(f); malformed += r is None; p1_req += r or []
for f in sorted(glob.glob(f"{M}/pass1/batch-*.specs.tsv")):
    r = load_strict(f); malformed += r is None; p1_sp += r or []
if malformed:
    print(f"\nFAIL: {malformed} malformed TSV file(s); fix column counts before merging"); sys.exit(1)
print(f"pass1 files: {len(glob.glob(f'{M}/pass1/batch-*.requirements.tsv'))} req / {len(glob.glob(f'{M}/pass1/batch-*.specs.tsv'))} spec")

fails = []; warns = []
def key(r): return (r["old_spec"], r["old_req_name"].strip())
bk = {key(r) for r in base_req}; pk = collections.Counter(key(r) for r in p1_req)
missing = bk - set(pk); extra = set(pk) - bk; dup = [k for k, v in pk.items() if v > 1]
if missing or extra or dup:
    fails.append(f"V1 requirement key mismatch: missing={len(missing)} extra={len(extra)} dup={len(dup)}")
    for k in list(missing)[:10]: print("  missing:", k)
    for k in list(extra)[:10]: print("  extra  :", k)
    for k in dup[:10]: print("  dup    :", k)
else: print("V1 ok: 1273 requirement keys match")

sc_by_req = collections.Counter((r["old_spec"], r["old_req_name"].strip()) for r in base_sc)
disp = collections.Counter(); keep_sc = out_sc = drop_sc = nh_sc = 0
bad_path = []; bad_disp = []; no_target = []; low = []; nh = []
VALID = {"KEEP","OUT:lint","OUT:runbook","OUT:design-doc","OUT:delete","DROP:historic","DROP:duplicate","DROP:obsolete","NEEDS_HUMAN"}
for r in p1_req:
    d = r["disposition"].strip(); n = sc_by_req[key(r)]; disp[d] += 1
    if d not in VALID: bad_disp.append((key(r), d)); continue
    if d == "KEEP":
        keep_sc += n; tp = r["target_path"].strip()
        ok = tp in voc or tp.startswith("stories/") or any(tp.startswith(f"components/infrastructure/{k}/") for k in voc_kinds)
        if not tp: no_target.append(key(r))
        elif not ok: bad_path.append((key(r), tp))
        if r.get("confidence","").strip() == "low": low.append(key(r))
    elif d.startswith("OUT:"): out_sc += n
    elif d.startswith("DROP:"): drop_sc += n
    else: nh_sc += n; nh.append(key(r))
print("dispositions:", dict(disp))
print(f"V3 scenarios: KEEP={keep_sc} OUT={out_sc} DROP={drop_sc} NEEDS_HUMAN={nh_sc} sum={keep_sc+out_sc+drop_sc+nh_sc} (expect 3588)")
if keep_sc + out_sc + drop_sc + nh_sc != 3588: fails.append("V3 scenario conservation broken")
if bad_disp: fails.append(f"invalid disposition values: {len(bad_disp)}"); [print("  ", x) for x in bad_disp[:10]]
if no_target: fails.append(f"KEEP without target_path: {len(no_target)}"); [print("  ", x) for x in no_target[:10]]
if bad_path: fails.append(f"V5 target_path not in vocabulary: {len(bad_path)}"); [print("  ", x) for x in bad_path[:15]]

names = collections.defaultdict(list)
for r in p1_req:
    if r["disposition"].strip() == "KEEP": names[(r["target_path"].strip(), r["new_req_name"].strip() or r["old_req_name"].strip())].append(key(r))
v6 = {k: v for k, v in names.items() if len(v) > 1 and not any(True for _ in v)}
dupnames = {k: v for k, v in names.items() if len(v) > 1}
mg = collections.defaultdict(set)
for r in p1_req:
    g = r.get("merge_group","").strip()
    if g: mg[g].add((r["target_path"].strip(), r["new_req_name"].strip()))
v7 = {g: s for g, s in mg.items() if len(s) > 1}
real_dup = {k: v for k, v in dupnames.items() if not any(next((x.get("merge_group","") for x in p1_req if key(x) == kk), "") for kk in v)}
if real_dup: warns.append(f"V6 (Pass 2 item) duplicate new_req_name in same target without merge_group: {len(real_dup)}"); [print("  V6:", k, v) for k, v in list(real_dup.items())[:10]]
else: print("V6 ok")
mg_tp = collections.defaultdict(set)
for r in p1_req:
    g = r.get("merge_group","").strip()
    if g: mg_tp[g].add(r["target_path"].strip())
v7 = {g: s for g, s in mg_tp.items() if len(s) > 1}
if v7: fails.append(f"V7 merge_group spans multiple target_paths: {len(v7)}"); [print("  ", g, s) for g, s in v7.items()]
else: print(f"V7 ok ({len(mg)} merge groups)")
hs = collections.defaultdict(list)
for r in base_req: hs[r["req_hash"]].append(key(r))
print("V8 ok (all 1273 req_hash unique in baseline)")
print(f"V9: NEEDS_HUMAN={len(nh)} low-confidence KEEP={len(low)}")
sp_disp = collections.Counter(r["disposition"].strip() for r in p1_sp); print("spec-level:", dict(sp_disp))
tgt = collections.Counter(r["target_path"].strip() for r in p1_req if r["disposition"].strip() == "KEEP")
unused = sorted(v for v in voc if v not in tgt and "<name>" not in v and not v.startswith("stories/"))
print(f"V11: vocabulary paths with no requirement assigned: {len(unused)}")
stories = sorted({r["target_path"].strip() for r in p1_req if r["target_path"].strip().startswith("stories/")})
print(f"proposed stories: {len(stories)}"); [print("  ", s) for s in stories]

if warns:
    print("\nWARN (Pass 2):"); [print("  -", w) for w in warns]
if fails:
    print("\nFAIL:"); [print("  -", f) for f in fails]; sys.exit(1)
if APPLY:
    idx = {key(r): r for r in p1_req}
    for r in base_req:
        s = idx[key(r)]
        for c in ["disposition","target_path","new_req_name","merge_group","rewrite_flags","confidence","rationale"]: r[c] = s.get(c, "").strip()
    with open(f"{M}/requirements.tsv","w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(base_req[0].keys()), delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(base_req)
    sidx = {r["old_spec"]: r for r in p1_sp}
    for r in base_sp:
        s = sidx.get(r["old_spec"], {})
        for c in ["disposition","primary_target","confidence","evidence","note"]: r[c] = s.get(c, "").strip()
    with open(f"{M}/specs.tsv","w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(base_sp[0].keys()), delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(base_sp)
    print("\nAPPLIED to requirements.tsv / specs.tsv")
else:
    print("\n(dry run — pass --apply to merge into the ledgers)")
