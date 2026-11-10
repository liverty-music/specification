## Why

The backend decides most of its business rules outside the entity layer. An audit of every non-test file of `internal/usecase`, `internal/adapter` and `internal/infrastructure` (2026-11-10) found about 85 rules in usecases, about 10 in adapters, about 77 in rdb repositories (in Go and in SQL) and 15 in the other infrastructure packages, besides the entity methods that state the same rule a second time. A rule that lives in a usecase can only be tested through mock-heavy usecase tests, and a rule that lives in a repository can only be tested against PostgreSQL. Several rules exist twice and already disagree: the per-ticket price of a cancellation notice and of the refund, Gemini's event dedup and `entity.FilterNewSeries`, Gemini's venue normalization and `entity.NormalizeVenueName`.

Change `restructure-backend-responsibilities` fixes the direction of the layers and the error and clock conventions. This change moves the decisions themselves, so that each rule has one home that a Go table test can check without mocks or a database.

## What Changes

- Every domain decision found by the audit moves to the entity that owns it: state transitions, eligibility, amounts and counts, windows and deadlines, "the same record" matching, and selection among candidates. A decision that is orchestration (which notification to send after which state, which usecase a Stripe webhook purpose dispatches to) moves to a usecase instead.
- Repositories stop deciding. Under the row locks they already take, a repository loads a snapshot, asks the entity for a plan (the next state and the states it may come from), and applies the plan with a compare-and-set `UPDATE … WHERE state = ANY($from)`. Zero rows affected means a concurrent writer won. `ResaleEntryRepository.DrawUnderLock` already works this way and becomes the pattern for the others.
- SQL keeps two kinds of conditions, each with a named Go owner:
  - Concurrency guards stay in the `WHERE` of the compare-and-set, but the allowed-from states come from the entity.
  - Read filters that paging needs (fan visibility, DRAFT exclusion, "due" filters) stay in SQL. Each gets a parity test asserting that the rows the SQL returns are exactly the rows the entity predicate accepts.
- Infrastructure adapters return what the external service said, not a decision: Gemini returns parsed drafts and the entity dedups and classifies them; the place and MusicBrainz clients return candidates and the usecase picks; mail senders send and the usecase decides whether and when; Pocket Sign returns the certificate state and the entity decides whether re-verification is needed.
- Usecases keep orchestration only. Their tests drop the cases that re-checked a moved rule and keep one test per usecase spec scenario.
- Lint limits are enforced after the moves: funlen 60 lines and 40 statements, gocognit 20, cyclop 15, test files excluded. Every remaining violation is split by responsibility. An exclusion is added only after the user agrees to it.
- Unused entity methods that still have no caller after the moves are deleted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Moving a rule to another layer keeps every outcome and error code a client observes; no spec states which layer decides a rule (the only specs that mention SQL or the database clock are frontend routes). `.openspec.yaml` sets `skip_specs: true`. Each moved rule is still checked against the spec that states it, for example `usecase/user/list-deletion-blockers`, `usecase/order/refund`, `entity/event`, `entity/series/publish-events`, `entity/ticket-sale` and `entity/checkout`.

## Impact

- Backend only: `internal/entity` grows methods and pure functions; `internal/usecase`, `internal/adapter` and `internal/infrastructure` lose decisions; `.golangci.yml` gains funlen, gocognit and cyclop.
- Order of work: this change starts after the layering and error work of `restructure-backend-responsibilities` has merged (its depguard rules and the apperr convention are what the moved code follows), and after `fix-backend-contract-drift` has fixed the bugs the audit found in rules that would move here. A rule that is wrong today is fixed there first, then moved here unchanged.
- Takes over from `restructure-backend-responsibilities` the parts that were about rules: its "rules move to the entity" table, the fan-visibility parity tests, and the function-size limits.
- Tests: entity table tests grow; usecase tests and rdb tests shrink. The rdb suite keeps one test per compare-and-set for the lost race and the parity tests.
- No API, proto, schema or migration change.
