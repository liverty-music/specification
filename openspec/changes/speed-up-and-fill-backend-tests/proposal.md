## Why

The backend's database tests are slow and fail now and then. One run of the `rdb` package takes 165 seconds: its 257 tests run one after another, because they all share one database and empty it with a `TRUNCATE` before every test (374 times per run). When every package ran together on 2026-11-10, the package failed once and passed on two runs by itself, and the cause is not known. Separately, some code that makes real decisions has no test at all: the consumers that react to a resale entry or a resold listing, the admin Organizer RPC handler, and two usecase methods that compose several reads (`SeriesUseCase.List`, `ConcertCandidateUseCase.List`) run at 0% coverage. For the two usecase methods and the admin handler, their specs state the behavior but no test checks it; for the two consumers, the usecases they call are tested, but the consumers' own dispatch, redelivery and payload checks are not.

## What Changes

- Each `rdb` test gets its own database, cloned from a template database that holds the applied migrations, so the tests no longer empty a shared database and can run in parallel.
- The other packages that write to the shared test database (the outbox test in `messaging`) use their own clone as well, so no two packages share rows.
- The one failure seen when every package ran together is reproduced and its cause recorded before the fix, and the fix is checked with repeated full runs.
- The time of the slow story tests (one workflow runtime each, 3 to 11 seconds per test) is measured, and they are changed only if they keep the package above its time target.
- Tests are added for the code that carries business decisions and has none: the resale entry and resold listing consumers, the admin Organizer handler, `SeriesUseCase.List`, `ConcertCandidateUseCase.List`, and the protobuf mapping of entity states and request inputs. Each test that verifies a spec scenario names it; the consumer tests verify no usecase scenario and name none.
- One-line methods that only pass a call through to an operation (`ArtistUseCase.GetOfficialSite`, `FollowUseCase.List`, `StripeWebhookUseCase.GetCardAuthorization`) get no usecase test of their own; the operation's contract test already covers what they return.
- Code that the change `restructure-backend-responsibilities` moves or rewrites is out of scope here; that change brings its own tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The change adds tests for behavior the specs already state and changes how the tests are run; no product behavior changes, so `.openspec.yaml` sets `skip_specs: true`. The tests it adds check scenarios of these existing specs:

- `components/usecase/series/list`
- `components/usecase/concert-candidate/list`
- `components/adapter/admin/api/rpc/organizer`

## Impact

- backend: the `rdb` test setup (`setup_test.go` and every test that uses the shared database), the `messaging` outbox test, `compose.yml` and the CI workflow (connection limit of the test database, where migrations are applied), the Makefile `test` target, and new tests in `internal/adapter/event`, `internal/adapter/rpc`, `internal/adapter/pb` and `internal/usecase`.
- A new test-only Go dependency (a template-database helper, see design.md).
- No production code, API, schema or deployed configuration changes.
