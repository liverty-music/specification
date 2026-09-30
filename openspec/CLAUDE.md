# OpenSpec authoring notes

## Plan PR bodies

- **Plan PR bodies show real spec diffs.** When a change carries `MODIFIED`, `REMOVED` or `RENAMED` requirements, append the part of `openspec show <change> --diff` from `Specifications Changed (diffs)` onward to the PR body inside a collapsed `<details>` block (the PR file diff only shows the delta file, not what it changes in the main spec). Skip it for changes that only add requirements. Refresh it with `gh pr edit` whenever the artifacts change during review.

## Spec tree

Specs follow the `liverty-clean-arch` schema (`openspec/schemas/liverty-clean-arch/`), whose `specs` instruction is the authoritative description of the tree and the writing rules. In short:

- `specs/stories/<story>/` — one user goal, named as a verb phrase, verified end to end.
- `specs/components/entity/<entity>/` — the ubiquitous language; language-independent, proto/Go/TS are derived from it. Write entities first.
- `specs/components/usecase/<entity>/<method>/` — one exported usecase method each.
- `specs/components/{adapter,infrastructure}/<audience>/<web|api>/.../<component>/` — outer layers, always from one audience's point of view (`fan`, `admin`, `organizer`); flows that cross audiences are stories.
- `scripts/check-spec-layout.py` (pre-commit) rejects any spec outside this layout.
