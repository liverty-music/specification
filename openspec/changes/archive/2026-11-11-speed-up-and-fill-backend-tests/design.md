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
- Every added test that verifies a spec scenario is annotated with it (`// @spec <capability> "<scenario>"`, the backend's existing convention). The consumer tests of tasks 3.1 and 3.2 verify no scenario (the usecase tests already do) and carry none.

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

`make test` and the CI test job no longer apply the migrations to `test-db`. After the switch no test reads its tables; it remains only as the database a test connects to when it creates a database of its own. Applying the migrations to it also did harm: a migration applied while a test's fake IAM roles exist grants them privileges there, and the roles can then never be dropped (see "Keep migrations and fake IAM roles apart"). The `atlas` CLI stays on PATH, because the template is built with it.

### Bound the connections, rather than the parallelism alone

Eight tests in parallel, each with a pool of up to 10 connections and some with workflow pools, can pass 100 connections. Two settings keep the run inside the limit. The test pool is opened with at most 4 connections, which is enough for a test. The test server's `max_connections` is raised to 300 in compose.yml and in the CI service definition. The pools the story tests open for their workflow runtime and client are capped at 4 connections too: with pgxpool's default of one per CPU, a run failed with `too many clients already` even at 300. All three are test-only settings in this repository; nothing deployed changes.

### Reproduce the failure before claiming a fix

The failure happened once, when every package ran together, and did not happen in two runs of `rdb` alone, so its cause is not known. The leading hypothesis: several `rdb` tests count outbox rows written after a mark (`outboxMark`, `"offset" > $1`), and the `messaging` outbox test writes rows into the same table of the same database at the same time. The hypothesis is checked before the switch. The full suite is run in a loop until it fails, and the failing test and the rows it read are recorded in this file. After the switch, the `messaging` test also gets its own clone, and ten full runs must pass.

### Keep migrations and fake IAM roles apart

Two tests create roles named like Cloud SQL IAM service accounts (`<name>@<project>.iam`): the grants test, which checks what each role may do, and the reception tests, which connect as `reception-api`. Roles belong to the whole server, and the grant migrations grant to every role matching their patterns that exists when they run. A migration applied in any database while such a role exists, by another package such as `rdb/migrationtest`, by the template build, or by another checkout, grants the role privileges there. The test can then not drop the role, and every later run that creates the same name fails. Without a fix, `make test` failed 8 of 10 runs on this.

Two measures, both in test code:

- The roles are named for the run (`<name>@test-<random>.iam`, `reception-api@admit-test-<random>.iam`), so a role another run left behind never blocks this one. The migrations match by pattern, so what the grants test checks is unchanged.
- One server-wide advisory lock (`testutil.LockMigrations`, taken in the `postgres` database so that it holds across packages and processes) keeps applying migrations and holding fake IAM roles apart. The template build and each `migrationtest` atlas run hold it while atlas runs; the grants and reception tests hold it from creating their roles until they drop them.

Alternative considered: removing the role's privileges in every database before dropping it. It reached into other tests' databases, and its `DROP OWNED BY` collided with a concurrent `migrationtest` migration (`tuple concurrently updated`), so it was dropped. The template build still removes the privileges of fake IAM roles from the template, for roles that a checkout without the lock leaves behind.

### The story tests are measured before they are changed

With a database of their own, the story tests run alongside everything else, and the longest takes about 11 s, below the 60 s target. Sharing one workflow runtime among stories would work against what several stories check: a worker that stops and another that resumes. Only if the package misses the target is the time inside a story measured, to see whether it goes to starting the runtime, stopping it, or waiting for polling, and is a story changed. The package met the target (task 2.7), so neither was done; only the duration of each story (5 to 11 s) is recorded.

### What gets new tests, and what does not

A piece of code gets a test when it makes a decision a spec states and nothing tests it today:

| Code | Decision it makes | Spec scenarios it is checked against |
|---|---|---|
| `ResaleEntryConsumer.HandleSendResaleEntryEnded` | Sends only for a Lapsed or Lost entry; redelivers later on Unavailable or DeadlineExceeded; refuses a payload without id or Order | none: the usecase scenarios are verified by `resale_entry_ended_test.go`; the consumer test checks only the dispatch, redelivery and payload checks |
| `ResaleEntryConsumer.HandleStartWorkflow` | Starts the entry's workflow from the announcement | none (the usecase spec of the workflow start is missing; reported, not written here) |
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

## Implementation record

Measured and checked on 2026-11-10 in the backend worktree `speed-up-and-fill-backend-tests` (base `be6c28f4`).

### pgtestdb check (task 1.1)

pgtestdb is adopted; no check failed, so the fallback helper is not needed.

- Version: `github.com/peterldowns/pgtestdb` and `.../migrators/atlasmigrator` v0.1.1, the latest of both modules.
- The Atlas migrator runs `atlas migrate apply --url <template> --dir file://<dir>`. It applied all 139 files, the two `-- atlas:txmode none` dbos migrations included: a throwaway test read `app.users` and `dbos.workflow_status` (both empty) on three clones, and `app.atlas_schema_revisions` held 138 rows. The template is built with `search_path=app`, as the operator applies the migrations.
- `pgtestdb.Custom` returns a `pgtestdb.Config` (host, port, user, database) for the clone, which `rdb.New` turns into the `pgxpool` the tests use.
- Cost: building the template took 36.6 s; each later clone took 0.1 to 1.1 s one at a time; 80 create-and-drop cycles over 8 sessions took 10.5 s with the default `WAL_LOG` strategy (4.4 s with `FILE_COPY`, not used).

Two deviations from pgtestdb's defaults, both in `internal/testutil/database.go`:

- The clones are owned by `test-user`, the server's superuser, instead of pgtestdb's unprivileged role: the rdb tests create roles and grant them privileges, as the shared `test-db` allowed.
- After migrating the template, the migrator runs `DROP OWNED BY` for every role named like an IAM service account. The grant migrations grant to every such role that exists when they run, and roles belong to the whole server; a template built while another test holds those roles would pass their privileges to every clone, and the roles could then never be dropped.

### Baseline (task 1.2)

Measured on the unchanged tree (`be6c28f4`) after the machine was rebooted, against a database only the measurement used (`TEST_DB_NAME`, a fresh copy of the migrated template), one run after another:

| Run | `Elapsed` | Result |
|---|---|---|
| 1 | 202.2 s | 1 test failed (`TestMigrationGrants_IAMRoles`: roles left by another run could not be dropped) |
| 2 | 128.6 s | aborted: `terminating connection due to administrator command` in `cleanTables`; not counted |
| 3 | 189.3 s | 1 test failed (same as run 1) |
| 4 | 111.0 s | passed |

Median of the three complete runs: **189.3 s**; the 165.7 s of the Context section lies inside their spread (111 to 202 s). CI: the "Run integration tests" step of the last green run on `main` (run 42738927523, `0543dba5`) took 3 min 25 s (205 s), the whole module included.

### The failure (task 1.3)

The loop was not run 20 times: the unchanged tree failed in its first runs, and every failure came from state that another process left on the shared server, not from the rdb tests themselves. The leading hypothesis (the `messaging` outbox test writing outbox rows while an rdb test counts them) is unconfirmed: no failing test read outbox rows, and in these runs the `messaging` test did not run alongside.

- `TestUserRepository_GetByEmail/fails_with_Internal_when_two_users_have_the_address_once_letter_case_is_ignored`: `failed to create user: ERROR: duplicate key value violates unique constraint`. Another worktree (`fix-backend-contract-drift`) had applied its migration `20261110080127_users_email_unique_ignoring_case` to `test-db` at 08:01:47 UTC, during the run; `atlas migrate status --env local` then showed version 20261110080127, which this tree does not have.
- `TestLotteryStory_StoppedAfterTheFirstCharge` and four other lottery stories: `the series is not the organizer's (permission_denied)`, in the same run. Inference, not verified: another process wrote to or emptied the shared tables during the story.
- `TestMigrationGrants_IAMRoles`, `TestTicketUseCase_Admit_Integration`, `TestScannerUseCase_Open_Integration` (on a database of this measurement's own): `role "organizer-console-api@test.iam" cannot be dropped because some objects depend on it (SQLSTATE 2BP01)`. The test roles held privileges in `test-db` (14 dependencies), `test-db-contract-drift` (197) and `migration-test-db` (276): a database migrated while the roles exist is granted to them, and a test can drop the role only in its own database.
- `TestMigration_EnterLotteryAtConfirm` (`rdb/migrationtest`): `ERROR: deadlock detected (SQLSTATE 40P01)` while the rdb package ran in the same `make test`.

What changed in response:

- Every test that read or wrote app tables has a database of its own, so no other test, package or worktree shares its rows (rdb and messaging).
- `make test` and the CI test job no longer apply the migrations to `test-db`: after the switch no test reads its tables, and applying them while the test roles exist is how the roles became impossible to drop. The `atlas` CLI stays on PATH for the template.
- The tests that create server-wide roles name them for the run (`<name>@test-<random>.iam`, `reception-api@admit-test-<random>.iam`), so a role another run left behind never blocks them; the grant migrations match roles by pattern, so the checks are unchanged.
- One server-wide advisory lock (`testutil.LockMigrations`, taken in the `postgres` database) keeps applying migrations and holding fake IAM roles apart, across packages and processes: the template build and each `migrationtest` atlas run hold it while atlas runs, and the grants and reception tests hold it from creating their roles until they drop them. Without it, `make test` failed 8 of 10 runs: `rdb/migrationtest` applied migrations in another process while an rdb test held its role, and `DROP ROLE` then failed with `2BP01`. Removing the role's privileges in the other database instead made `migrationtest` fail with `tuple concurrently updated (XX000)`, so that approach was dropped.
- `TestMigrationGrants_IAMRoles` applies the migrations to an empty database of its own (`grants-<random>`), dropped at cleanup, and runs in parallel. The two reception tests share one role per run and stay serial, with a comment that says why.

Not changed: `rdb/migrationtest` still uses a scratch database with a fixed name (`migration-test-db`), so two worktrees running it at the same moment can still collide.

Until every checkout has this change: a checkout whose compose.yml lacks `max_connections=300` recreates the shared `postgres` container on its next `make test`, and the tests running at that moment fail with `connection refused` (seen once, in run 5 of the first ten-run loop). Its tests also still create `@test.iam` roles without the lock; the template drops their privileges, and this change's tests no longer depend on dropping them.

### Conversion (tasks 2.3 to 2.6)

- 280 rdb tests take `db := newTestDB(t)` (a clone with at most 4 connections) and `t.Parallel()`; helpers and fixtures take the database as a parameter or field. `testDB`, `cleanDatabase` and `setupTestDatabase` are gone.
- `cleanTables(t, db)` stays: subtests of one test run one after another on their parent's database and empty it between cases, which is cheaper than a clone per subtest.
- The story tests no longer `TRUNCATE` the `dbos` tables: each starts its workflow runtime on its own database.
- `messaging`: the outbox subtests and each forwarder subtest connect to a clone of their own; the forwarder no longer needs a schema of its own.
- `max_connections=300` in compose.yml and the CI test service; `SHOW max_connections` on the recreated compose service returns 300.
- The pools the story tests open for their workflow runtime and client allow at most 4 connections, as `newTestDB`. With pgxpool's default (one per CPU, 8 here), a run failed with `FATAL: sorry, too many clients already (SQLSTATE 53300)` even at `max_connections=300`.
- `go test -count=3 -race ./internal/infrastructure/database/rdb/` (grants test skipped) passed in 106 s; the story tests passed `-count=3 -race` again after the pool limit; the role-based tests passed `-count=2` on their own.

### Target (task 2.7)

Final code, three runs one after another on an otherwise idle server (2026-11-11): 48.6 s, 54.7 s, 62.6 s, all passing. Median: **54.7 s**, against the 60 s target and the 189.3 s baseline.

`TestMigrationGrants_IAMRoles` is the critical path: it starts with the package and ends with it, because it applies all 139 migrations with atlas to an empty database of its own while the other tests run. It took 14 to 25 s with the server to itself and 38 to 59 s while another session's `make test` used the same server; the package time follows it. The story tests (5 to 11 s each) are not the cause, so they were not changed.

Earlier sets of three, kept for the record: 26.5, 30.5, 39.0 s with the grants test already parallel but before the migration lock (all passing; `make test` then still failed on role drops), and 70.4, 66.4, 84.2 s while another session ran `make test` on the same server.

CI, backend PR #804 (run 42941657897, all checks green): "Run integration tests" took 3 min 48 s (228 s), against 3 min 25 s (205 s) before. The step includes compiling every package with `-race` and coverage, and it ends with the slowest package of the module. Within it the rdb package went from 88.4 s to 54.7 s. `rdb/migrationtest` went from 20.1 s to 36.9 s; the inference, not verified, is that it waits for the migration lock while the template is built and while the grants test holds its roles. The CI number is for information only, as the Goals section says; the target is the local median.

### Ten runs of make test (task 2.8)

All ten passed on the final code (2026-11-11): runs 1 to 6 in one loop (208, 177, 207, 295, 446 s, and a sixth that spanned the machine's sleep); a reboot stopped run 7 with no failure, and runs 7 to 10 were run again (122, 132, 95, 76 s; run 8 was paused once to let another session commit). After the runs no fake IAM role and no copied database was left on the server.

The failure of task 1.3 is gone: none of the ten runs failed. Before the migration lock, the first ten-run loop on per-test databases failed 8 of 10 runs on role drops and once on a container recreated by another checkout (see above).

### Untested decisions (tasks 3.1 to 3.7)

- `internal/adapter/pb` coverage: 39.4% before, 61.6% after.
- Gaps between behavior and spec found by the new tests: none.
- Already noted above and still open: `ResaleEntryConsumer.HandleStartWorkflow` has no usecase spec for the workflow start.

## Sources

- pgtestdb: https://github.com/peterldowns/pgtestdb
- IntegreSQL: https://github.com/allaboutapps/integresql
- Encore, "Go integration tests with Postgres": https://encore.dev/articles/go-integration-tests-postgres
- go-txdb: https://github.com/DATA-DOG/go-txdb
- PostgreSQL, "Non-Durable Settings": https://www.postgresql.org/docs/current/non-durability.html
