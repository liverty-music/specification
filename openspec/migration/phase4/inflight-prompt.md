# Phase 4 — place in-flight change deltas in the new tree

Active changes still describe their new requirements against the old flat capability names. Classify every requirement in `openspec/migration/phase4/inflight-requirements.tsv` into the new tree so each change's `specs/` can be rewritten.

Use exactly the criterion, decision tree and tie-breaks of `openspec/migration/pass1-prompt.md`, and the tree and audience rules of `openspec/schemas/liverty-clean-arch/schema.yaml` (specs instruction). Allowed `target_path` values are in `openspec/migration/vocabulary.tsv` (plus `stories/<story>` proposals and `<contract>` templates). Read each requirement's full text from `openspec/migration/phase4/input/<change>__<old_cap>.md`.

Before choosing a `new_req_name`, check `openspec/specs.next/<target_path>/spec.md` if it exists: the name must not collide with a requirement already there (archive rejects duplicates).

These are all ADDED requirements for unreleased features (resale, wallet/check-in, eKYC, organizer vetting, legal compliance, route rendering, shared UI). Most are product behavior and KEEP; only classify OUT when the requirement is truly not the product (CI, deployment, code convention). If a requirement is product behavior but has no vocabulary slot (a usecase method that does not exist yet because the feature is unimplemented), propose `components/usecase/<entity>/<method>` from the requirement's own verb and note `confidence=medium` — the code will follow the spec.

Output: `openspec/migration/phase4/inflight-classified.tsv`, TSV with header, csv.writer, 8 columns:
  change	old_cap	req_name	disposition	target_path	new_req_name	confidence	rationale
One row per input row, `change`/`old_cap`/`req_name` verbatim. Write nothing else.
