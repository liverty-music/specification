# Reconstruct — put implementation design back where it belonged

Some requirements in the main specs are not product behavior: they describe implementation design, code conventions, operational procedure, or CI/deploy mechanics. They exist because the change that introduced them wrote them into its delta `spec.md` instead of its `design.md`. Your job is to rewrite each assigned archived change **as it should have been written from the start** — with no migration markers, no dated notes, nothing that reveals this was done after the fact.

## Inputs
- `openspec/migration/reconstruct-batches.json` — under your batch key: a map of `<archived change>` → list of `{old_spec, old_req_name, disposition}` rows to relocate.
- For each change: `openspec/changes/archive/<change>/design.md`, `proposal.md`, and `specs/<old_spec>/spec.md` (the delta).
- The current text of each requirement: `openspec/specs/<old_spec>/spec.md` (read only — do NOT edit main specs).

## Per requirement
1. Read the requirement block (header, body, scenarios) from the main spec.
2. Read the change's `design.md` in full. Decide what information in the block is **not already** in design.md. Often design.md already holds the decision and the delta merely restated it as SHALL/scenarios — then nothing needs adding.
3. Integrate only the missing information into the **existing section that fits**, in the file's **existing voice and structure**:
   - a decision and its reasoning → `## Decisions` (extend an existing numbered decision, or add the next number in the same `**Decision**:` / `**Rationale**:` shape the file already uses)
   - constraints, invariants, failure handling → `## Decisions` or `## Risks / Trade-offs` (match the file's bullet shape)
   - operational steps, environment setup, rollout → `## Migration Plan` (add the section if the template has it and it is missing)
   - code/style conventions enforced by tooling → `## Decisions` as "enforced via <tool>", one line; the rule text itself will live in lint config
   Never paste SHALL/WHEN/THEN blocks into design.md. Rewrite as design prose. Never write "migrated", "moved from spec", a date, or a reference to this operation.
4. Remove the requirement block from the delta `specs/<old_spec>/spec.md`. Leave every other requirement in that delta untouched (some are KEEP). If the delta file has no requirements left, delete the file and its directory if empty.
5. If a deleted delta file was a new capability, fix `proposal.md`: remove that entry from `### New Capabilities` (leave "(none — see design.md)" if the list becomes empty, matching how the pilot did it). If the capability was under `### Modified Capabilities` and its only delta is gone, remove that bullet.

## Do NOT
- edit anything under `openspec/specs/` (main specs) — the coordinator removes the blocks there
- edit `tasks.md`, `.openspec.yaml`, or any change outside your batch
- invent new sections that the design template does not have
- run git or openspec write commands

## Report — write EXACTLY one file, TSV with header
`openspec/migration/reconstruct/<batch>.tsv`
  change	old_spec	old_req_name	disposition	design_section	delta_action	proposal_action	note
- `design_section`: the heading you integrated into (e.g. `Decisions §6`, `Risks / Trade-offs`, `Migration Plan`) or `already-covered` if design.md needed nothing
- `delta_action`: `removed-block` | `deleted-file` | `deleted-file+dir`
- `proposal_action`: `none` | `removed-new-capability` | `removed-modified-capability`
Use Python csv.writer, 8 columns per row, one row per assigned requirement, `old_spec`/`old_req_name` verbatim.

Reference: the pilot at `openspec/changes/archive/2026-03-15-hydrate-user-profile-on-startup/` shows the target shape (git show 2acedad).
