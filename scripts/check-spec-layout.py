#!/usr/bin/env python3
"""Pre-commit guard for the OpenSpec tree layout.

Every spec (main tree and active change deltas) must sit on one of the
Clean-Architecture paths the liverty-clean-arch schema defines:

  stories/<story>/spec.md
  components/entity/<entity>/spec.md
  components/usecase/<entity>/<method>/spec.md
  components/adapter/<audience>/<web|api>/<segment>[/<segment>...]/spec.md
  components/infrastructure/<audience>/<web|api>/<segment>[/<segment>...]/spec.md

with audience in {fan, admin, organizer}. Flat depth-1 specs and a root
specs/spec.md are rejected so the pre-migration layout cannot come back.
Archived changes are left as history and not checked."""
import re, sys, pathlib
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
OK = re.compile(
    rf"^(?:stories/{SLUG}"
    rf"|components/entity/{SLUG}"
    rf"|components/usecase/{SLUG}/{SLUG}"
    rf"|components/(?:adapter|infrastructure)/(?:fan|admin|organizer)/(?:web|api)/{SLUG}(?:/{SLUG})*)/spec\.md$")
root = pathlib.Path(__file__).resolve().parent.parent / "openspec"
roots = [root / "specs"] + [d / "specs" for d in (root / "changes").iterdir() if d.is_dir() and d.name != "archive"]
bad = []
for base in roots:
    if not base.is_dir(): continue
    for p in base.rglob("spec.md"):
        rel = p.relative_to(base).as_posix()
        if not OK.match(rel): bad.append(f"{p.relative_to(root.parent)}")
if bad:
    print("spec files outside the liverty-clean-arch layout:"); [print("  ", b) for b in bad]
    print("allowed: stories/<story>, components/entity/<e>, components/usecase/<e>/<m>, components/{adapter,infrastructure}/{fan,admin,organizer}/{web,api}/...")
    sys.exit(1)
print("spec layout OK")
