#!/usr/bin/env python3
"""Guard for the ubiquitous language: reject words no entity defines.

The entities under openspec/specs/components/entity/ are the names every
repository uses. The words below were replaced by entity names and must not
come back. They are matched in any letter case and inside identifiers too
(ProvisionTenant, operator_email, multi-tenant, buyer_id).

Scope: the files git tracks under proto/, docs/, openspec/specs/ and
openspec/schemas/. openspec/changes/ is not checked: proposals, designs and
REMOVED or Migration text name old names on purpose, and archives are history.

The one exception is a proto line that starts with `reserved`, which keeps a
removed field name from being reused. There is no other exception: rephrase
the sentence instead. A later rename adds a row to WORDS.

Usage: check-forbidden-words.py [REPO_ROOT]   (default: this repository)
Prints `path:line: <word> - use <replacement>` per hit and exits 1 on any."""
import pathlib, re, subprocess, sys

# word -> replacement hint (design D2 of rename-organization-operations).
WORDS = {
    "tenant": "the Organizer's Organization (an Organization; Organizations, per Organizer)",
    "operator": "a member of the Organizer (the owner for the owner role; an identity for the account; an admin for Liverty Music staff)",
    "seller": "the Organizer",
    "buyer": "the User",
    "applicant": "the fan who entered",
}
SCOPE = ("proto/", "docs/", "openspec/specs/", "openspec/schemas/")
PATTERN = re.compile("|".join(WORDS), re.IGNORECASE)
RESERVED = re.compile(r"^\s*reserved\b")


def tracked_files(root: pathlib.Path):
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", *SCOPE],
                             check=True, capture_output=True).stdout.decode()
        return [root / p for p in out.split("\0") if p]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [p for s in SCOPE for p in sorted((root / s).rglob("*")) if p.is_file()]


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent)
    hits = 0
    for path in tracked_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        rel = path.relative_to(root).as_posix()
        for n, line in enumerate(text.splitlines(), 1):
            if rel.endswith(".proto") and RESERVED.match(line):
                continue
            for m in PATTERN.finditer(line):
                word = m.group(0).lower()
                print(f"{rel}:{n}: {m.group(0)} - use {WORDS[word]}")
                hits += 1
    if hits:
        print(f"{hits} forbidden word(s); see the rpc-design skill, \"Vocabulary traps\"")
        return 1
    print("forbidden words OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
