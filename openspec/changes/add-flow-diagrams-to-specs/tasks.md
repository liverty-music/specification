# Tasks

All tasks are in the specification repository, on one branch in a worktree cut from origin/main (design.md decision 5).

## 1. specification: check script (scripts/check-diagrams.py)

- [ ] 1.1 Write `scripts/check-diagrams.py` with the story, event and usecase checks of design.md decision 4. Keep the docstring style of `check-story-diagrams.py`, and match entity names to spec directories case-insensitively with hyphens removed. Verify by running it on the current main specs: it must report each story that still has a usecase-beta fence, the 37 usecase specs that name 5 or more distinct entity operations, and no false positive for a usecase spec below the threshold.
- [ ] 1.2 Verify each check rejects a broken case. Using scratch copies of one story, one entity and one usecase spec outside the repository, confirm that the script fails for each of these: a usecase method missing from the story fence; an `evt` not listed by any entity; an event listed twice; a usecase diagram missing an operation its text names; and a usecase diagram naming an operation its text does not.

## 2. specification: schema (openspec/schemas/liverty-clean-arch/schema.yaml)

- [ ] 2.1 Rewrite the stories part of the specs instruction's "Layer contents": the `eventmodeling` fence with the element table and rules of design.md decision 1, an example fence, and no "Order is not drawn" sentence. Verify with `openspec instructions specs --change add-flow-diagrams-to-specs --json`, which must print the new text.
- [ ] 2.2 Add the events table to the entity part (design.md decision 2) and the sequence diagram to the usecase part (decision 3), with one short example each. Extend the "edited directly in the main spec" rule and the proposal instruction's "(Purpose)" note to a usecase's Purpose diagram. Add domain events to "What may be named in a spec". Verify the same way as 2.1.

## 3. specification: entity events (components/entity/*)

- [ ] 3.1 For every entity operation spec that announces something (search for "announced" in `openspec/specs/components/entity/`), add the event to the Purpose events table of the entity the event is about, which may differ from the operation's own entity (design.md decision 2), starting from the mapping there. Verify that `python3 scripts/check-diagrams.py` reports no duplicate event and that `openspec validate --specs` passes.

## 4. specification: usecase diagrams (components/usecase/*)

- [ ] 4.1 Add a `sequenceDiagram` fence (design.md decision 3) to the Purpose of each usecase spec the script lists, starting with order/issue, ticket/admit and concert/create-from-discovered. Verify that the script reports no usecase error and that `openspec validate --specs` passes.

## 5. specification: story diagrams (stories/*)

- [ ] 5.1 Replace the usecase-beta fence of every story with an `eventmodeling` fence (design.md decision 1), using only events listed in step 3. Add a fence to any story without one that names a usecase method. Verify that the script reports no story or event error and that `openspec validate --specs` passes.

## 6. specification: wiring and render check

- [ ] 6.1 Point the pre-commit hook (`.pre-commit-config.yaml`), the `make check` target and the `openspec-checks` CI step (`.github/workflows/ci.yml`, including its path filter) at `scripts/check-diagrams.py`, and delete `scripts/check-story-diagrams.py`. Verify with `make check` and `pre-commit run --all-files`.
- [ ] 6.2 Render every fence added or changed in steps 3 to 5 with Mermaid 12.3.0 in headless Chromium (design.md decision 6). Verify that every fence renders with no parse error, and look at the rendered lottery story (stories/win-tickets-in-a-lottery) and order/issue diagrams.
- [ ] 6.3 Open the PR and confirm in its rendered file view that the diagrams of win-tickets-in-a-lottery and order/issue display. Verify that CI Success passes.
