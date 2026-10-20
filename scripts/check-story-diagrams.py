#!/usr/bin/env python3
"""Pre-commit guard for story usecase diagrams.

A story's Purpose draws its goal in a `mermaid` usecase-beta fence, and that
fence names every usecase method (OrderUseCase.Checkout) the story names
anywhere else (liverty-clean-arch schema, "Layer contents", stories): a story
that names a usecase method has the fence, and every method it names outside
the fence is in it.

Only main specs are checked, so an in-progress change never blocks unrelated
work; its stories are checked once archive writes them into the main tree.
Names are matched as text; the Mermaid itself is not parsed."""
import re, sys, pathlib
NAME = re.compile(r"\b[A-Z][A-Za-z]*UseCase\.[A-Z][A-Za-z]*\b")
FENCE = re.compile(r"^```mermaid\n(usecase-beta\n.*?)^```", re.M | re.S)
root = pathlib.Path(__file__).resolve().parent.parent / "openspec"

def split(text):
    """Return (names in the Purpose's usecase-beta fence or None, names elsewhere)."""
    m = re.search(r"^## Purpose\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    purpose = m.group(1) if m else ""
    f = FENCE.search(purpose)
    rest = text.replace(f.group(0), "") if f else text
    return (set(NAME.findall(f.group(1))) if f else None), set(NAME.findall(rest))

bad = []
def check(path, fence, named):
    rel = path.relative_to(root.parent)
    if named and fence is None:
        bad.append(f"{rel}: names {', '.join(sorted(named))} but its Purpose has no usecase-beta fence")
    elif fence is not None and named - fence:
        bad.append(f"{rel}: the Purpose's usecase-beta fence lacks {', '.join(sorted(named - fence))}")

for p in sorted((root / "specs" / "stories").glob("*/spec.md")):
    check(p, *split(p.read_text()))
if bad:
    print("story usecase diagrams out of step with the story text:"); [print("  ", b) for b in bad]
    print("draw every usecase method a story names in its Purpose's usecase-beta fence (liverty-clean-arch schema, Layer contents, stories)")
    sys.exit(1)
print("story diagrams OK")
