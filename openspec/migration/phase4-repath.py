#!/usr/bin/env python3
"""Phase 4: move every active change's delta specs onto the new tree.

Reads openspec/migration/phase4/inflight-classified.tsv and, per change,
splits each old flat delta (specs/<old_cap>/spec.md) into per-target deltas
(specs/<target_path>/spec.md), renaming requirements to new_req_name.
KEEP -> "## ADDED Requirements", KEEP:MODIFIED -> "## MODIFIED Requirements",
OUT:* -> block dropped (its content already lives in the change's
proposal/design). The proposal's capability lists and the change's schema
are rewritten too. Dry-run unless --apply."""
import csv, os, re, sys, shutil, collections
APPLY = "--apply" in sys.argv
C = "openspec/changes"; NEXT = "openspec/specs.next"
rows = list(csv.DictReader(open("openspec/migration/phase4/inflight-classified.tsv", encoding="utf-8"), delimiter="\t"))
fails = []
by_change = collections.defaultdict(list)
for r in rows: by_change[r["change"]].append(r)
def parse_delta(path):
    s = open(path, encoding="utf-8").read()
    blocks = {}
    for sec in re.split(r"(?=^## (?:ADDED|MODIFIED|REMOVED|RENAMED) Requirements)", s, flags=re.M)[1:]:
        kind = re.match(r"## (\w+) Requirements", sec).group(1)
        for b in re.split(r"(?=^### Requirement:)", sec, flags=re.M)[1:]:
            name = re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1)
            if name in blocks: fails.append(f"duplicate requirement {name} in {path}")
            blocks[name] = (kind, b.rstrip("\n") + "\n")
    return blocks
plan = {}  # change -> {target: {kind: [block]}}
for ch, crs in sorted(by_change.items()):
    caps = {r["old_cap"] for r in crs}
    blocks = {}
    for cap in caps:
        p = f"{C}/{ch}/specs/{cap}/spec.md"
        if not os.path.exists(p): fails.append(f"missing delta {p}"); continue
        for name, kb in parse_delta(p).items(): blocks[(cap, name)] = kb
    seen = set(); out = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in crs:
        k = (r["old_cap"], r["req_name"])
        if k not in blocks: fails.append(f"{ch}: no delta block for {k}"); continue
        seen.add(k); kind, b = blocks[k]
        if r["disposition"].startswith("OUT:") or r["disposition"].startswith("DROP:"): continue
        if kind != "ADDED": fails.append(f"{ch}: unexpected delta kind {kind} for {k}")
        newkind = "MODIFIED" if r["disposition"] == "KEEP:MODIFIED" else "ADDED"
        if not r["target_path"] or not r["new_req_name"]: fails.append(f"{ch}: KEEP row without target/name {k}"); continue
        nb = re.sub(r"^### Requirement:.*$", f"### Requirement: {r['new_req_name']}", b, count=1, flags=re.M)
        out[r["target_path"]][newkind].append(nb)
    for k in blocks:
        if k not in seen: fails.append(f"{ch}: delta requirement not classified {k}")
    for tp, kinds in out.items():
        names = [re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1) for bs in kinds.values() for b in bs]
        if len(names) != len(set(names)): fails.append(f"{ch}: duplicate new_req_name in {tp}")
        p = f"{NEXT}/{tp}/spec.md"
        if os.path.exists(p):
            existing = set(re.findall(r"^### Requirement:\s*(.+?)\s*$", open(p, encoding="utf-8").read(), re.M))
            for n in names:
                if n in existing and "ADDED" in kinds and any(b.startswith(f"### Requirement: {n}\n") for b in kinds["ADDED"]): fails.append(f"{ch}: ADDED {n} collides with existing requirement in {tp}")
                if n not in existing and "MODIFIED" in kinds and any(b.startswith(f"### Requirement: {n}\n") for b in kinds["MODIFIED"]): fails.append(f"{ch}: MODIFIED {n} has no counterpart in {tp}")
    plan[ch] = out
if fails:
    print("FAIL:"); [print("  -", f) for f in fails]; sys.exit(1)
def rewrite_proposal(ch, out):
    p = f"{C}/{ch}/proposal.md"; s = open(p, encoding="utf-8").read()
    new = [tp for tp in out if not os.path.exists(f"{NEXT}/{tp}/spec.md")]
    mod = [tp for tp in out if os.path.exists(f"{NEXT}/{tp}/spec.md")]
    def bullets(tps):
        if not tps: return "(none)\n"
        lines = []
        for tp in sorted(tps):
            names = [re.match(r"### Requirement:\s*(.+?)\s*$", b.split("\n")[0]).group(1) for bs in out[tp].values() for b in bs]
            lines.append(f"- `{tp}`: {'; '.join(names)}")
        return "\n".join(lines) + "\n"
    def repl(section, body):
        nonlocal s
        m = re.search(rf"(^### {section}\n)(.*?)(?=^##|\Z)", s, flags=re.M | re.S)
        if not m: fails.append(f"{ch}: proposal lacks '### {section}'"); return
        s = s[:m.start(2)] + "\n" + body + "\n" + s[m.end(2):]
    repl("New Capabilities", bullets(new)); repl("Modified Capabilities", bullets(mod))
    return p, s
summary = []
for ch, out in plan.items():
    caps = {r["old_cap"] for r in by_change[ch]}
    n_new = sum(len(bs) for k in out.values() for bs in k.values())
    dropped = [r["req_name"] for r in by_change[ch] if not r["disposition"].startswith("KEEP")]
    summary.append((ch, len(caps), len(out), n_new, dropped))
    pp, ps = rewrite_proposal(ch, out)
    if APPLY:
        for tp, kinds in out.items():
            os.makedirs(f"{C}/{ch}/specs/{tp}", exist_ok=True)
            body = "".join(f"## {kind} Requirements\n\n" + "\n".join(kinds[kind]) + "\n" for kind in ("ADDED", "MODIFIED") if kinds.get(kind))
            open(f"{C}/{ch}/specs/{tp}/spec.md", "w", encoding="utf-8").write(body.rstrip("\n") + "\n")
        for cap in caps: shutil.rmtree(f"{C}/{ch}/specs/{cap}")
        open(pp, "w", encoding="utf-8").write(ps)
        y = f"{C}/{ch}/.openspec.yaml"; t = open(y, encoding="utf-8").read()
        open(y, "w", encoding="utf-8").write(re.sub(r"^schema: .*$", "schema: liverty-clean-arch", t, flags=re.M))
if fails: print("FAIL:"); [print("  -", f) for f in fails]; sys.exit(1)
for ch, nc, nt, nr, dropped in summary:
    print(f"{ch:40} {nc} old cap -> {nt} targets, {nr} requirement blocks; dropped {len(dropped)}: {dropped}")
print("applied" if APPLY else "(dry run — pass --apply)")
