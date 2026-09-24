# Re-audit — corrected inclusion criterion

Pass 1 classified some requirements OUT because "no user actor observes this". That criterion was wrong. Re-judge ONLY the rows listed for your batch in `openspec/migration/reaudit-candidates.tsv` (filter by `old_spec` ∈ your batch from `reaudit-batches.json`).

## The corrected criterion (read `openspec/migration/pass1-prompt.md` § "What belongs in openspec")
A requirement belongs in openspec iff it specifies what the product does — UI behavior, API contracts (inputs/outputs/errors/authorization/idempotency/rate limits/event contracts), background behavior (discovery, lottery, notifications), entity invariants. Observability by a human is irrelevant.
It stays OUT iff it is not the product: CI, deployment, infra provisioning, ops procedures, code/style conventions, test inventories, observability plumbing, performance-only implementation choices.

## Where a re-admitted requirement goes
- API contract of one operation → `components/usecase/<entity>/<method>` (vocabulary.tsv)
- Cross-cutting API rule protecting an entity (auth scoping, NotFound on missing record) → `components/entity/<entity>` — once, never duplicated into usecases
- Background pipeline behavior → the usecase that runs it (e.g. concert discovery → `components/usecase/concert/search-new-concerts` or `create-from-discovered`)
- Notification / push delivery semantics → `components/infrastructure/push/<name>` or the notification usecase
- If the requirement is product behavior but names only implementation (function names, struct names), it is still KEEP: set `rewrite_flags=CLASSNAME` so Phase 2 rewrites it in entity terms
- If it is genuinely a cross-cutting API property with no entity home (e.g. global rate limiting), use `NEEDS_HUMAN` and say so in rationale

## Output — write EXACTLY one file, TSV with header
`openspec/migration/reaudit/<batch>.tsv`
  old_spec	old_req_name	disposition	target_path	new_req_name	merge_group	rewrite_flags	confidence	rationale
Every candidate row for your batch must appear exactly once, `old_spec`/`old_req_name` verbatim. Keep `disposition` as the current OUT value when it is still correct under the new criterion (state why in one line). Use Python csv.writer; exactly 9 columns per row; no tabs/newlines inside fields. Do not modify any other file.
