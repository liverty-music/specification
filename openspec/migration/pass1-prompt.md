# Pass 1 — requirement classification

You classify every `### Requirement:` block of the specs assigned to you into the new spec tree, or out of openspec. You do NOT rewrite any spec. You only produce TSV rows.

## Inputs (read all before starting)
- `openspec/migration/vocabulary.tsv` — the ONLY allowed values for `target_path`. Never invent a path. If nothing fits, use `NEEDS_HUMAN`.
- `openspec/migration/requirements.tsv` — the rows you must fill (match on `old_spec` + `old_req_name`, both exact).
- `openspec/migration/specs.tsv` — Pass 0 prior per spec: `band` is `KEEP?` / `OUT?` / `OUT?(plan)` / `REVIEW`. It is a hint, not a decision.
- Each spec at `openspec/specs/<old_spec>/spec.md`.

## What belongs in openspec
Only what the product does for its users (fan, organizer, admin). Code conventions, lint rules, CI, deployment, infrastructure, operations, test inventories, design tokens do NOT. When in doubt whether a requirement describes user-facing behavior, ask: "does a fan or organizer observe this?" If no actor observes it, it is OUT.

## Decision tree — apply IN ORDER, take the FIRST match
1. Describes a user's multi-step goal across screens/layers → `stories/<story>` (write the story name as a verb phrase, e.g. `stories/follow-an-artist`; stories are not yet in vocabulary — these are proposals, mark confidence ≤ medium)
2. Behavior of exactly one route → `components/infrastructure/ui/route/<route>`
3. Behavior of a UI surface shared across routes → `components/infrastructure/ui/global/<surface>`
4. Non-UI user-experience infrastructure (push, service-worker, locale, email) → `components/infrastructure/<kind>/<name>` (kind from vocabulary; propose `<name>` in kebab-case)
5. Backend response/state change for one operation → `components/usecase/<entity>/<method>` (must exist in vocabulary)
6. Invariant of an entity itself (fields, identity, validation) → `components/entity/<entity>`
7. No user actor appears → `OUT:lint` (code/style rule) | `OUT:runbook` (operational constraint) | `OUT:design-doc` (technology decision) | `OUT:delete` (CI/deploy mechanics with no lasting value)
8. Otherwise → `NEEDS_HUMAN`

## Tie-breaks (never copy a requirement to two targets)
- route vs usecase: what the user sees → route; the result of the call → usecase. If both are in one requirement, choose the dominant one and note `SPLIT-CANDIDATE` in rationale.
- story vs route: needs multiple routes → story; closes within one route → route.
- entity vs usecase: always true → entity; true after an operation → usecase.
- cross-cutting (errors, timeouts, telemetry, cors): telemetry/cors → OUT; user-visible errors → `ui/global/<surface>`; timeouts as experienced → route or story. Never `components/adapter`.
- mixed infra + product inside one spec: classify per requirement; the spec-level disposition becomes `SPLIT`.

## rewrite_flags (comma-separated, may be empty)
- `CLASSNAME` — names an implementation type or file (e.g. `BubbleManager`, `ArtistBubbleStore`, `concertUseCase`, `foo.ts`, `src/...`). Exported interfaces (`ConcertUseCase`, `ArtistRepository`) and proto message names are NOT flags.
- `THRESHOLD` — qualitative quantity ("promptly", "minimum target", "sufficient") without a number+unit.
- `HISTORIC` — prohibits reintroducing something already removed ("SHALL NOT include merkle_root", "removed with", "legacy", "retired"). Disposition for a purely historic requirement is `DROP:historic`.
- `DEDUP:<req_hash>` — this requirement duplicates another; point at the kept one.

## disposition values
`KEEP` | `OUT:lint` | `OUT:runbook` | `OUT:design-doc` | `OUT:delete` | `DROP:historic` | `DROP:duplicate` | `DROP:obsolete` | `NEEDS_HUMAN`
`target_path` is required for KEEP, empty otherwise. `new_req_name` required for KEEP (keep the old name unless it names an implementation type). `merge_group` only when 2+ requirements should become one — use a short id like `BUBBLE-CAP`.

## confidence
`high` — decision tree matched cleanly; `medium` — tie-break applied or story name proposed; `low` — genuinely unsure (prefer `NEEDS_HUMAN` over a low-confidence KEEP).

## rationale
One line. MUST name the code asset or actor that justified the decision (a route, an interface method, "no user actor", etc.).

## Output — write EXACTLY these two files, TSV with header, nothing else
`openspec/migration/pass1/<batch>.requirements.tsv`
  old_spec	old_req_name	disposition	target_path	new_req_name	merge_group	rewrite_flags	confidence	rationale
`openspec/migration/pass1/<batch>.specs.tsv`
  old_spec	disposition	primary_target	confidence	evidence	note
  (spec-level disposition: KEEP if all reqs KEEP; OUT:* if all OUT; SPLIT if mixed; NEEDS_HUMAN if any req NEEDS_HUMAN. primary_target = most common KEEP target. evidence = one line. note = destination file for OUT:* e.g. `cloud-provisioning/docs/runbooks/zitadel.md`)

Every requirement row in requirements.tsv for your specs MUST appear exactly once. Do not modify any file outside `openspec/migration/pass1/`.
