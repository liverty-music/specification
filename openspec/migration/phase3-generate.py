#!/usr/bin/env python3
"""Phase 3: assemble openspec/specs.next/ from the ledger, the current main
specs, and the Phase 2 outputs. Never touches openspec/specs/.
Then verify: C3/C5 (paths in vocabulary), C7/C8 (scenario conservation),
C12 (unique requirement names per file), C19/C20/C21 (convention lint).
"""
import csv, os, re, sys, glob, shutil, hashlib, collections
M = "openspec/migration"; S = "openspec/specs"; N = "openspec/specs.next"
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))
norm = lambda s: re.sub(r"\s+", " ", s.strip().lower()); H = lambda s: hashlib.sha256(norm(s).encode()).hexdigest()[:8]
req = rd(f"{M}/requirements.tsv"); voc = rd(f"{M}/vocabulary.tsv")
vs = {r["target_path"] for r in voc}; tmpl = [v.split("<")[0] for v in vs if "<" in v]
ok_path = lambda tp: tp in vs or tp.startswith("stories/") or any(tp.startswith(t) for t in tmpl)
keep = [r for r in req if r["disposition"] == "KEEP"]
# ---- current main-spec blocks and purposes ----
blocks = {}; purposes = {}
for f in glob.glob(f"{S}/*/spec.md"):
    spec = f.split("/")[2]; t = open(f, encoding="utf-8").read()
    m = re.search(r"^## Purpose\s*\n(.*?)(?=^## )", t, re.S | re.M); purposes[spec] = (m.group(1).strip() if m else "")
    for b in re.split(r"(?=^### Requirement:)", t, flags=re.M)[1:]:
        name = re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1); blocks[(spec, name)] = b.rstrip("\n") + "\n"
# ---- phase 2 outputs ----
def strip_hdr(t): return "\n".join(l for l in t.split("\n") if not l.strip().startswith("<!--")).strip("\n") + "\n"
merged = {os.path.basename(f)[:-3]: strip_hdr(open(f, encoding="utf-8").read()) for f in glob.glob(f"{M}/phase2/output/merge/*.md")}
rewritten = {}
for f in glob.glob(f"{M}/phase2/output/rewrite/*.md") + glob.glob(f"{M}/phase2/output/rewrite2/*.md"):
    t = open(f, encoding="utf-8").read()
    if "<!-- DROP:" in t: rewritten[os.path.basename(f)[:-3]] = None
    else: rewritten[os.path.basename(f)[:-3]] = strip_hdr(t)
print(f"phase2 outputs: {len(merged)} merged, {len(rewritten)} rewritten ({sum(v is None for v in rewritten.values())} dropped)")
# ---- assemble ----
out = collections.defaultdict(list); srcs = collections.defaultdict(set); groups_done = set(); missing = []; conserved_hashes = collections.Counter(); changed_rows = []
scen_of = lambda b: re.split(r"(?=^#### Scenario:)", b, flags=re.M)[1:]
for r in keep:
    k = (r["old_spec"], r["old_req_name"].strip()); tp = r["target_path"]; srcs[tp].add(r["old_spec"])
    if r["merge_group"]:
        g = r["merge_group"]; changed_rows.append(k)
        if g in groups_done: continue
        groups_done.add(g)
        if g not in merged: missing.append(("merge", g)); continue
        out[tp].append(merged[g]); continue
    fn = f"{r['old_spec']}__{r['req_hash']}"
    if fn in rewritten:
        if rewritten[fn] is None: continue
        out[tp].append(rewritten[fn]); changed_rows.append(k); continue
    if k not in blocks: missing.append(("block", k)); continue
    b = blocks[k]
    if r["new_req_name"] and r["new_req_name"].strip() != k[1]: b = re.sub(r"^### Requirement:.*$", f"### Requirement: {r['new_req_name'].strip()}", b, count=1, flags=re.M)
    out[tp].append(b)
    for s in scen_of(b): conserved_hashes[H(s)] += 1
if missing: print("MISSING inputs:", missing[:10]); sys.exit(1)
# ---- write specs.next ----
if os.path.exists(N): shutil.rmtree(N)
titles = lambda tp: tp.split("/")[-1].replace("-", " ").title() if not tp.startswith("stories/") else tp.split("/")[-1].replace("-", " ").capitalize()
purpose_todo = []
for tp, bl in out.items():
    d = f"{N}/{tp}"; os.makedirs(d, exist_ok=True)
    ss = sorted(srcs[tp]); p = purposes.get(ss[0], "") if len(ss) == 1 else ""
    pf = f"{M}/phase2/output/purpose/{tp.replace('/', '__')}.md"
    if os.path.exists(pf): p = open(pf, encoding="utf-8").read().strip()
    if len(p) < 50: purpose_todo.append(tp); p = f"<!-- PURPOSE: write from sources {', '.join(ss)} -->\nTBD"
    with open(f"{d}/spec.md", "w", encoding="utf-8") as f:
        f.write(f"# {titles(tp)}\n\n## Purpose\n\n{p}\n\n## Requirements\n\n" + "\n".join(bl))
print(f"specs.next: {len(out)} specs written; {len(purpose_todo)} need a Purpose")
# ---- checks ----
fails = []
bad = [tp for tp in out if not ok_path(tp)]
if bad: fails.append(f"C5 paths outside vocabulary: {len(bad)} {bad[:5]}")
dupn = []
for tp, bl in out.items():
    names = [re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1) for b in bl]
    d = [n for n, c in collections.Counter(names).items() if c > 1]
    if d: dupn.append((tp, d))
if dupn: fails.append(f"C12 duplicate requirement names: {len(dupn)} {dupn[:5]}")
sc = rd(f"{M}/scenarios.tsv"); keep_keys = {(r["old_spec"], r["old_req_name"].strip()) for r in keep}
expected_unchanged = collections.Counter(r["scen_hash"] for r in sc if (r["old_spec"], r["old_req_name"].strip()) in keep_keys and (r["old_spec"], r["old_req_name"].strip()) not in set(changed_rows))
total_next = sum(len(scen_of(b)) for bl in out.values() for b in bl)
total_keep = sum(1 for r in sc if (r["old_spec"], r["old_req_name"].strip()) in keep_keys and r.get("routing") != "DEDUP")
print(f"C7 scenarios: specs.next {total_next} vs KEEP ledger {total_keep}")
diff = sum((expected_unchanged - conserved_hashes).values())
print(f"C8 unchanged-row scenario hashes missing from specs.next: {diff}")
if diff: fails.append("C8 conservation broken for unchanged rows")
if total_next != total_keep: fails.append(f"C7 scenario count mismatch ({total_next} vs {total_keep})")
CLS = re.compile(r"\b[a-z]+UseCase\b|\b\w+(Store|Manager|Canvas|Controller|Element|Sheet)\b(?![- ]?[a-z])|\b[\w/-]+\.(ts|go|tsx)\b")
HIST = re.compile(r"merkle_root|reintroduce|must not reintroduce|復活させ|再導入しない", re.I)
QUAL = re.compile(r"\b(promptly|quickly|reasonably fast|sufficient(ly)?|a minimum target)\b|速やか|十分に", re.I)
lint = collections.Counter()
for tp, bl in out.items():
    t = "\n".join(bl)
    if not tp.startswith("components/entity/") and CLS.search(t): lint["C19 impl-name"] += 1
    if HIST.search(t): lint["C20 historic"] += 1
    if QUAL.search(t): lint["C21 qualitative"] += 1
print("convention lint (files flagged):", dict(lint) or "clean")
print("\nFAIL:" if fails else "\nOK — specs.next assembled"); [print("  -", x) for x in fails]
sys.exit(1 if fails else 0)
