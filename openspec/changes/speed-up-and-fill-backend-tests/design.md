## Context

See proposal.md for why. This section records what was measured on 2026-11-10 in the backend at `0543dba5`, on an 8-core WSL machine with the compose PostgreSQL 18.

- `go test -count=1 -json ./internal/infrastructure/database/rdb/` takes 165.7 s (the package's `Elapsed`). The 257 top-level tests (817 `t.Run` subtests) add up to 164.7 s, so almost nothing runs in parallel; only 12 calls to `t.Parallel()` exist.
- Every test shares the database `test-db` through the package-level `testDB` (915 references) and empties it with `cleanDatabase(t)` (374 calls). `cleanTables` already empties all tables in one `TRUNCATE` statement; one statement per table had cost 181 s of a 271 s run (comment in `setup_test.go`, measured 2026-11-04).
- The slowest tests:
  - `TestMigrationGrants_IAMRoles`, 16.1 s. It applies every migration to a scratch database of its own.
  - The story tests, about 15 of them at 2.6 to 10.8 s each and about 60 s together. Each one empties the `dbos` tables, then starts and stops a workflow runtime (DBOS) on `test-db`. Some stop the worker on purpose to imitate a terminated Pod.
- The compose service and CI already run PostgreSQL with `fsync=off`, `synchronous_commit=off` and `full_page_writes=off` (compose.yml, `.github/workflows/ci.yml`). The usual "make the server non-durable" advice is therefore already applied, and there is no more to gain from it.
- Migrations are applied outside Go: `make test` and CI run `atlas migrate apply` against `test-db` before `go test` (139 migration files).
- Other packages also connect to `test-db` while `rdb` runs: `messaging` (the outbox test writes rows to `watermill_events_outbox`; the forwarder test connects too, but in a schema of its own) and, under the `integration` tag, `lastfm`. `workflow` and `rdb/migrationtest` create scratch databases of their own.
- The default `max_connections` of the test server is 100. A test database opened by `rdb.New` allows up to 10 connections, and each story test opens further pools for its workflow runtime and client.
- `go test ./...` without the Makefile panics in `internal/di` unless `GOLANG_PROTOBUF_REGISTRATION_CONFLICT=ignore` is set; the Makefile exports it. This change does not touch that.

## Goals / Non-Goals

**Goals:**

- The `rdb` package finishes in **60 s or less**: the median of three local runs of `go test -count=1 -json ./internal/infrastructure/database/rdb/` on the same 8-core machine, read from the package's `Elapsed`, after the migrations are applied. The baseline is 165.7 s. 60 s leaves room above the longest single test (16 s) and the longest story (11 s) once the tests run eight at a time. CI's "Run integration tests" step duration is recorded before and after, for information only, since the runner differs.
- Ten consecutive full runs (`make test`) pass with no failure.
- Every added test is annotated with the spec scenario it checks (`// @spec <capability> "<scenario>"`, the backend's existing convention).

**Non-Goals:**

- Faster tests in other packages, and the `GOLANG_PROTOBUF_REGISTRATION_CONFLICT` setup.
- Tests for code that `restructure-backend-responsibilities` (layers, errors, the clock) or `move-decisions-into-entities` (rules moved into entities, including the decisions now made in the repositories and consumers) moves or rewrites. Those changes bring their own tests, and `move-decisions-into-entities` shrinks the rdb tests to compare-and-set and parity cases. When it lands first, the tests here follow the code to its new place.
- Changing product behavior. A test that finds behavior different from its spec stops the task, and the gap is reported instead of being fixed here.

## Decisions

### Each test gets a database cloned from a migrated template

A test asks for a database and gets one of its own. That database is a copy (`CREATE DATABASE … TEMPLATE`) of a template database that holds the applied migrations. With no shared rows, the `TRUNCATE` between tests goes away and the tests can call `t.Parallel()`. The story tests also get their own `dbos` tables, so they can run in parallel without emptying them first.

Alternatives considered:

- **Roll back a transaction after each test** (go-txdb). This does not fit here. The repositories open their own transactions (56 places in `rdb`), the workflow runtime and the outbox use pools of their own, and go-txdb works on `database/sql`, while `rdb` uses `pgxpool`.
- **Keep one database and split the run across packages** (several `TEST_DB_NAME` values). This still runs each package's tests one after another and needs a database per package, prepared by hand.
- **Make the server non-durable.** Already done (Context).

Template cloning is the approach the Go community uses for this case: pgtestdb gives each test a migrated clone, about 20 ms per clone according to its authors, and IntegreSQL keeps a pool of such clones (sources below).

### pgtestdb manages the template, rather than a helper of our own

Two ways to get the template were compared.

| | pgtestdb with its Atlas migrator | Our own helper around `TEST_DB_NAME` |
|---|---|---|
| Template build | Runs `atlas migrate apply` into a template named after a hash of the migrations, once per hash | Needs a new step in `make test` and CI that applies the migrations to a dedicated template, since `CREATE DATABASE … TEMPLATE test-db` fails while other packages hold connections to `test-db` |
| A changed migration | A new hash gives a new template on its own | We must notice and drop the stale template, which is the usual failure of hand-written helpers |
| Concurrent packages | Go locks and PostgreSQL advisory locks are built in | We write the locking |
| Cost | One test-only dependency; the `atlas` CLI must be on PATH when tests run, which `make test` and CI already require | No dependency; more code to own |

Decision: pgtestdb. It removes the two parts that are easy to get wrong (a stale template and concurrent creation), and the only new requirement (`atlas` on PATH) already holds. The `rdb` setup adapts what pgtestdb returns into the `*rdb.Database` that the tests use today (a `pgxpool` built from the clone's connection settings). Before it is adopted, task 1.1 checks three things: the current module version, that the Atlas migrator applies the `-- atlas:txmode none` migrations that create the `dbos` schema, and how the clone's connection settings are returned. If one of them fails, the fallback is our own helper with the extra migration step from the table, and design.md is updated.

`make test` and CI keep applying the migrations to `test-db` for the packages that still use it, so the switch does not have to happen in one step.

### Bound the connections, rather than the parallelism alone

Eight tests in parallel, each with a pool of up to 10 connections and some with workflow pools, can pass 100 connections. Two settings keep the run inside the limit. The test pool is opened with at most 4 connections, which is enough for a test. The test server's `max_connections` is raised to 300 in compose.yml and in the CI service definition. Both are test-only settings in this repository; nothing deployed changes.

### Reproduce the failure before claiming a fix

The failure happened once, when every package ran together, and did not happen in two runs of `rdb` alone, so its cause is not known. The leading hypothesis: several `rdb` tests count outbox rows written after a mark (`outboxMark`, `"offset" > $1`), and the `messaging` outbox test writes rows into the same table of the same database at the same time. The hypothesis is checked before the switch. The full suite is run in a loop until it fails, and the failing test and the rows it read are recorded in this file. After the switch, the `messaging` test also gets its own clone, and ten full runs must pass.

### The story tests are measured before they are changed

With a database of their own, the story tests run alongside everything else, and the longest takes about 11 s, below the 60 s target. Sharing one workflow runtime among stories would work against what several stories check: a worker that stops and another that resumes. The time inside a story is still measured, to see whether it goes to starting the runtime, stopping it, or waiting for polling. A story is changed only if the package misses the target.

### What gets new tests, and what does not

A piece of code gets a test when it makes a decision a spec states and nothing tests it today:

| Code | Decision it makes | Spec scenarios it is checked against |
|---|---|---|
| `ResaleEntryChangedConsumer.HandleSendResaleEntryEnded` | Sends only for a Lapsed or Lost entry; redelivers later on Unavailable or DeadlineExceeded; refuses a payload without id or Order | none: the usecase scenarios are verified by `resale_entry_ended_test.go`; the consumer test checks only the dispatch, redelivery and payload checks |
| `ResaleEntryChangedConsumer.HandleStartWorkflow` | Starts the entry's workflow from the announcement | none (the usecase spec of the workflow start is missing; reported, not written here) |
| `ResaleListingSoldConsumer.HandleStartRefund` | Starts the refund of the sold listing; refuses a payload without id | none: `refund-sold` is verified by `resale_listing_uc_test.go`; the consumer test checks only the dispatch and payload check |
| `SeriesUseCase.List` | Pairs each Series with its authored concerts; one failed read fails the call | `usecase/series/list`, all four scenarios |
| `ConcertCandidateUseCase.List` | Pairs each pending candidate with its Artist; one failed read fails the call | `usecase/concert-candidate/list`, all three scenarios |
| `AdminOrganizerHandler` | Runs one usecase method per call and returns usecase errors unchanged | `adapter/admin/api/rpc/organizer` scenarios of "Each call runs one OrganizerUseCase method and returns the short name" |
| `pb` state and input mapping | Which proto value each entity state becomes, and how request inputs become entity values | One table test per enum: every entity value maps to a proto value other than UNSPECIFIED, and back to itself where a reverse mapping exists |

The decision at the boundary is checked by unit tests with the usecases mocked. The authentication gate and request validation of the admin handler run in interceptors that are already tested elsewhere, so those scenarios are not added here.

Not tested here: one-line pass-throughs (`ArtistUseCase.GetOfficialSite`, `FollowUseCase.List`, `StripeWebhookUseCase.GetCardAuthorization`). They contain no branch, and the operation's contract test already checks what they return.

## Risks / Trade-offs

- [Some `rdb` tests may depend on rows left by an earlier test, or on running alone] → The conversion goes file by file. A test that needs shared state keeps a database for its subtests and drops `t.Parallel()`, with a comment that says why.
- [Clones pile up on the test server] → pgtestdb drops the clone of a passed test and keeps a failed one to inspect. Failed clones are removed with `docker compose down -v`, the reset compose.yml already documents.
- [`restructure-backend-responsibilities` or `move-decisions-into-entities` moves `pb`, the consumers or repository decisions while this change adds tests to them] → The tests here are small and per file. Whichever change lands second moves or rebases them.
- [Parallel tests expose real races in repository code] → Such a failure is a finding, not noise. It is reported, and the test keeps running serially until the race is fixed.

## Sources

- pgtestdb: https://github.com/peterldowns/pgtestdb
- IntegreSQL: https://github.com/allaboutapps/integresql
- Encore, "Go integration tests with Postgres": https://encore.dev/articles/go-integration-tests-postgres
- go-txdb: https://github.com/DATA-DOG/go-txdb
- PostgreSQL, "Non-Durable Settings": https://www.postgresql.org/docs/current/non-durability.html
