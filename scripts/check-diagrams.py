#!/usr/bin/env python3
"""Pre-commit guard for the diagrams in story, entity and usecase Purposes.

The liverty-clean-arch schema ("Layer contents") asks for three diagrams that
summarize prose, and this script keeps each in step with the prose it draws:

- Stories: a story's Purpose draws the story in a `mermaid` eventmodeling
  fence. Every usecase method (OrderUseCase.Checkout) the story names outside
  the fence is a `cmd` or `rmo` frame in it, written with `_` for the first
  `.` (OrderUseCase_Checkout). A story that names a usecase method has the
  fence.
- Events: every `evt` frame of a story fence (LotteryEntry_Won) is a domain
  event listed in the events table of an entity's Purpose
  (LotteryEntry.Won). An event is listed once, by the entity its name
  starts with.
- Usecases: a usecase spec whose text outside the fence names 5 or more
  distinct entity operations (Order.Issue: an entity with a spec under
  components/entity/ and one of its operations) draws its flow in a
  `mermaid` sequenceDiagram fence in its Purpose. The operations in the
  fence's messages are exactly the ones its text names. A usecase spec that
  has the fence is held to it below the threshold too.

Entity names are matched to spec directories case-insensitively with hyphens
removed, so acronyms resolve (Event.GetOrganizerID -> event/get-organizer-id).
Only main specs are checked, so an in-progress change never blocks unrelated
work; its specs are checked once archive writes them into the main tree.
Names are matched as text; the Mermaid itself is not parsed."""
import re, sys, pathlib

THRESHOLD = 5
USECASE_METHOD = re.compile(r"\b[A-Z][A-Za-z]*UseCase\.[A-Z][A-Za-z]*\b")
DOTTED = re.compile(r"\b([A-Z][A-Za-z0-9]*)\.([A-Z][A-Za-z0-9]*)\b")
FENCE = re.compile(r"^```mermaid\n(\S+)\n(.*?)^```\n?", re.M | re.S)
FRAME = re.compile(r"^\s*(?:tf|rf|timeframe|resetframe)\s+\d+\s+(\w+)\s+([A-Za-z0-9_]+)", re.M)
PARTICIPANT = re.compile(r"^\s*(?:participant|actor)\s+(\w+)(?:\s+as\s+(.+?))?\s*$", re.M)
MESSAGE = re.compile(r"^\s*(\w+)\s*[-.x)>]+[+-]?\s*(\w+)\s*:\s*([A-Z][A-Za-z0-9]*)", re.M)
EVENT_ROW = re.compile(r"^\|\s*`?([A-Z][A-Za-z0-9]*\.[A-Z][A-Za-z0-9]*)`?\s*\|", re.M)
root = pathlib.Path(__file__).resolve().parent.parent / "openspec"
specs = root / "specs"
entities = {p.name.replace("-", ""): p.name for p in (specs / "components" / "entity").iterdir()
            if (p / "spec.md").exists()}


def purpose(text):
    m = re.search(r"^## Purpose\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def fence(text, kind):
    """Return (the body of the Purpose's mermaid fence of that kind or None, text without it)."""
    for f in FENCE.finditer(purpose(text)):
        if f.group(1) == kind:
            return f.group(2), text.replace(f.group(0), "")
    return None, text


def kinds(text):
    return {f.group(1) for f in FENCE.finditer(purpose(text))}


def events_table(text):
    """Event names listed in the Purpose's events table (header row starts with `| event |`)."""
    m = re.search(r"^\|\s*event\s*\|.*\n\|[-| :]+\|\n((?:\|.*\n?)*)", purpose(text), re.M)
    return EVENT_ROW.findall(m.group(1)) if m else []


def entity(name):
    return entities.get(name.lower())


bad = []


def rel(path):
    return path.relative_to(root.parent)


# Events: collect every listed event, each once, under the entity it is about.
listed = {}
for p in sorted((specs / "components" / "entity").glob("*/spec.md")):
    for name in events_table(p.read_text()):
        if name in listed:
            bad.append(f"{rel(p)}: event {name} is also listed by {listed[name]}")
            continue
        listed[name] = rel(p)
        if entity(name.split(".")[0]) != p.parent.name:
            bad.append(f"{rel(p)}: event {name} is listed by {p.parent.name}, not by the entity its name starts with")


def operations(text):
    """Distinct entity operations a text names (events are names, not operations)."""
    return {f"{a}.{b}" for a, b in DOTTED.findall(text) if entity(a) and f"{a}.{b}" not in listed}


# Stories: the eventmodeling fence draws every usecase method, and only listed events.
for p in sorted((specs / "stories").glob("*/spec.md")):
    text = p.read_text()
    body, rest = fence(text, "eventmodeling")
    named = set(USECASE_METHOD.findall(rest))
    if "usecase-beta" in kinds(text):
        bad.append(f"{rel(p)}: the Purpose still has a usecase-beta fence; draw the story as an eventmodeling fence")
    if body is None:
        if named:
            bad.append(f"{rel(p)}: names {', '.join(sorted(named))} but its Purpose has no eventmodeling fence")
        continue
    frames = [(k, n.replace("_", ".", 1)) for k, n in FRAME.findall(body)]
    drawn = {n for k, n in frames if k in ("cmd", "command", "rmo", "readmodel")}
    if named - drawn:
        bad.append(f"{rel(p)}: the eventmodeling fence lacks {', '.join(sorted(named - drawn))} as a cmd or rmo")
    unlisted = sorted({n for k, n in frames if k in ("evt", "event")} - listed.keys())
    if unlisted:
        bad.append(f"{rel(p)}: the eventmodeling fence draws {', '.join(unlisted)}, which no entity lists as an event")

# Usecases: 5 or more named entity operations need a sequenceDiagram naming exactly them.
for p in sorted((specs / "components" / "usecase").glob("*/*/spec.md")):
    text = p.read_text()
    body, rest = fence(text, "sequenceDiagram")
    named = operations(rest)
    if body is None:
        if len(named) >= THRESHOLD:
            bad.append(f"{rel(p)}: names {len(named)} entity operations but its Purpose has no sequenceDiagram fence")
        continue
    alias = {a: (b or a).strip() for a, b in PARTICIPANT.findall(body)}
    drawn = set()
    for src, dst, op in MESSAGE.findall(body):
        for side in (dst, src):
            name = alias.get(side, side)
            if entity(name):
                drawn.add(f"{name}.{op}")
                break
    if named - drawn:
        bad.append(f"{rel(p)}: the sequenceDiagram lacks {', '.join(sorted(named - drawn))}")
    if drawn - named:
        bad.append(f"{rel(p)}: the sequenceDiagram draws {', '.join(sorted(drawn - named))}, which its text does not name")

if bad:
    print("diagrams out of step with the spec text:"); [print("  ", b) for b in bad]
    print("keep each Purpose diagram in step with its spec (liverty-clean-arch schema, Layer contents)")
    sys.exit(1)
print("diagrams OK")
