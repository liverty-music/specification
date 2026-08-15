## 1. Specification (proto)

- [x] 1.1 Add optional `from` field (`entity.v1.LocalDate from = 1;`) to `ListByFollowerRequest` in `concert_service.proto`, with a doc comment describing the today-onward default when omitted
- [x] 1.2 Run buf lint/format/breaking locally-equivalent checks; open the specification PR
- [x] 1.3 After review + CI pass, merge and publish a Release tag; monitor `buf-release.yml` BSR generation to success

## 2. Backend implementation (prepare in parallel with §1)

- [x] 2.1 Thread a `from` (nullable date) argument through the concert handler → use case → repository for `ListByFollower`
- [x] 2.2 Add `AND e.local_event_date >= COALESCE($2, CURRENT_DATE)` to `listConcertsByFollowerQuery`, binding `from` (or nil) as `$2`
- [x] 2.3 Map the request `from` LocalDate to the repository argument in the handler (TODO marker until generated types land)
- [x] 2.4 Unit tests: default (nil) returns future-only; explicit past `from` returns past-inclusive; empty result returns empty groups, not error
- [x] 2.5 After BSR gen: `go get` the new schema version, `go mod tidy`, swap TODO placeholders for generated types, `make check`

## 3. Frontend implementation (prepare in parallel with §1)

- [x] 3.1 Add a `from` argument to `ConcertClient.listByFollower` (wrap in `LocalDate`) and to `ConcertStore.listByFollower`; incorporate `from` into the store cache key
- [x] 3.2 Dashboard: on default load, pass the client's current local date as `from` (reuse the existing plain-date lib / All-Nearby date source)
- [x] 3.3 Parse and validate the `from` query param from the URL; ignore missing/malformed values (fall back to today-onward)
- [x] 3.4 Add the collapsible date facet to the filter bottom sheet: "過去のコンサートも表示" affordance → single "この日付以降を表示" date field, committed by the shared confirm button
- [x] 3.5 On confirm, sync the chosen date to the URL via `replaceState`; clearing back to today removes the param and reverts to today-onward
- [x] 3.6 Re-fetch `ListByFollower(from)` on date change; ensure artist/journey chip counts recompute over the loaded (past-inclusive) set
- [x] 3.7 Empty-state: when the default view has no upcoming concerts, keep the "過去のコンサートも表示" affordance available
- [x] 3.8 Tests: URL round-trip (reload preserves `from`), default today-onward request, past-date re-fetch, combined artist+journey+date facets
- [x] 3.9 After BSR gen: `npm install` the new schema package, swap TODO placeholders for generated types, `make check`

## 4. Ship & verify

- [x] 4.1 Open backend and frontend PRs once green locally; merge after CI + review
- [x] 4.2 Cut backend and frontend releases; confirm prod rollout (ArgoCD sync / pin bump)
- [x] 4.3 Prod verify: dashboard defaults to today-onward; expanding "過去も表示" with a past date shows past concerts; reload preserves the filter
