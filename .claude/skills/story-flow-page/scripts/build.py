"""Assemble a story flow page from its parts.

usage: python3 build.py <work-dir> <out.html> "<title>"

<work-dir> holds main.html (the inside of <main>, with {{DIAGRAM:<name>}}
where a diagram's source goes) and one <name>.mmd file per diagram. The
script HTML-escapes each .mmd into its placeholder and puts the result
into assets/page-template.html, so an edit to a diagram is always made in
its .mmd file and re-embedded, never patched in the escaped page text.
"""

import html
import pathlib
import re
import sys

work, out, title = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
template = (pathlib.Path(__file__).parent.parent / "assets" / "page-template.html").read_text(encoding="utf-8")
main = (work / "main.html").read_text(encoding="utf-8")


def diagram(m: re.Match) -> str:
    return html.escape((work / f"{m.group(1)}.mmd").read_text(encoding="utf-8").rstrip("\n"), quote=False)


# Check main.html itself, before the diagrams go in: Mermaid source may
# contain "{{" (a hexagon node), which is not a leftover placeholder.
leftover = re.search(r"\{\{(?!DIAGRAM:[\w-]+\}\})[^}]*\}\}", main)
if leftover:
    sys.exit("main.html still has a placeholder: " + leftover.group(0))
main = re.sub(r"\{\{DIAGRAM:([\w-]+)\}\}", diagram, main)
page = template.replace("{{TITLE}}", html.escape(title), 1)
page = re.sub(r"<main>.*</main>", lambda _: "<main>\n" + main.strip("\n") + "\n</main>", page, flags=re.S)
out.write_text(page, encoding="utf-8")
print(f"wrote {out}")
