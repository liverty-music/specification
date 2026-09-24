# Phase 2 — merged bodies and rewrites

You produce the final text of requirements that will be placed in the new spec tree. You never edit `openspec/specs/**` or any archived change. You read input blocks and write output blocks.

## Rules for every requirement you write
- Format: `### Requirement: <name>` / one normative paragraph using SHALL / `#### Scenario: <title>` blocks with `- **WHEN**` / `- **THEN**` (and `- **AND**`) bullets. Exactly this shape; `openspec validate --strict` rejects anything else.
- Subject nouns are contracts and ubiquitous language only: entity names, exported interfaces and their methods (`ConcertUseCase.List`, `ArtistRepository`), audience + screen names (the discovery page, the organizer console), surface names (`bottom-sheet`, `dna-orb`), UI vocabulary (bubble, orb, lane, hype). Never an implementation type (`concertUseCase`, `BubbleManager`, `ArtistBubbleStore`, `EventDetailSheet` as a class), a file path, a package-internal function, or a TS/Go identifier. State frontend behavior from the audience's side: "the discovery page shows at most 50 artist bubbles", never "ArtistBubbleStore caps the field at 50".
- Thresholds are numbers with units. If a member says "a minimum target" and you cannot find the number in the members, keep the qualitative word and add `<!-- THRESHOLD: number unknown -->` on its own line after the paragraph so it is caught later.
- Do not add behavior that no member states. Do not drop a scenario. Do not merge two scenarios into one. Scenario titles may be edited only to remove implementation names.
- No dates, no "migrated", no reference to this operation.

## Merge task (`phase2/input/merge/<group>.md` → `phase2/output/merge/<group>.md`)
The input holds N member requirement blocks that describe one thing. Write ONE block:
1. Name: the clearest member name, or a better one in the same style. It must not name an implementation type.
2. Body: one paragraph that states the union of the members' normative content without repetition. If members conflict, the member whose spec was modified most recently wins — say which in the header comment.
3. Scenarios: every member scenario, in member order. Keep each scenario's bullets verbatim unless a bullet names an implementation type (then rewrite that bullet minimally).
Output file starts with the input's first-line header comment, then add `<!-- renamed_scenarios: <count> -->`, then the block.

## Rewrite task (`phase2/input/rewrite/<file>.md` → `phase2/output/rewrite/<file>.md`)
Flags in the header say why:
- `CLASSNAME`: rewrite so no implementation name remains, in body or scenarios. Same number of scenarios, same meaning.
- `HISTORIC`: remove sentences/bullets that only prohibit reintroducing something already removed ("SHALL NOT include merkle_root"). Keep current behavior. If nothing current remains, output only the header plus `<!-- DROP: entirely historical -->`.
Use the header's `new_name` unless it contains an implementation name; then choose a name in entity/audience terms.
Output file starts with the input's header comment, then the block.

## Batches
`phase2/merge-batches.json` and `phase2/rewrite-batches.json` map your batch key to the input file names you own. Write exactly one output file per input file, nothing else.
