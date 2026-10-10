## Context

See proposal.md (Why). The vendors behind the spec's generic names: the message broker is NATS JetStream (single replica on Spot, streams and consumers owned by NACK), the sign-in service is Zitadel, the database is Cloud SQL for PostgreSQL through pgx/pgxpool, and the log collector is the GKE logging agent writing to Cloud Logging.

Current behavior that shapes the approach (backend `origin/main`, 2026-10-10):

- **Startup order.** DI calls `messaging.NewPublisher` first. It dials NATS with `MaxReconnects(-1)` and `ReconnectWait(1s)`, but without `RetryOnFailedConnect`, so an unreachable NATS fails startup in about 1 s (`internal/infrastructure/messaging/publisher.go:33-44`).
  - Only `ConnectNATS` retries (`connectWithRetry`, about 30 s in total), and it runs after the publisher.
  - Before #423, `EnsureStreams` ran first and was the startup wait. The archived `2026-03-10-fix-consumer-nats-resilience/design.md:107` relied on it.
- **Zitadel.** `zitadelconn.NewConnection` → `middleware.JWTProfileFromPath` → zitadel/oidc v3 `profile.NewJWTProfileTokenSource` calls `client.Discover` (HTTP) unless a token endpoint is given (`pkg/client/profile/jwt_profile.go:84-90`).
  - The gRPC dial is lazy: `grpc.Dial` without `WithBlock`.
  - Three clients are built in DI: `NewEmailVerifier`, `NewIdentityRemover` and `NewOrganizerProvisioner`.
- **DB ping at startup.** `rdb.New` pings once and fails startup on error.
- **API health.** fan, admin, organizer and reception serve gRPC health on their Connect port. `HealthCheckHandler.Check` calls `pgxpool.Pool.Ping` for every request (`internal/adapter/rpc/health_handler.go:52-66`).
  - kubelet readiness (every 10 s) and liveness (every 20 s), both with a 5 s timeout, and the Gateway HealthCheckPolicy all hit this handler.
  - The Connect server starts only after DI, so nothing answers probes during startup.
- **Pool growth.** pgxpool `Ping` acquires a pool connection. When no idle connection exists, puddle constructs one. If the caller's context ends first, construction continues in a goroutine and the connection joins the pool anyway (puddle v2.2.2 `initResourceValue`). On 2026-10-09, overlapping probes against a slow database grew every API pool to `MaxConns`, and the extra connections lived for the full 30 min `MaxConnLifetime`.
- **Consumer health.** event-consumer and media-consumer start an HTTP health server on :8081 before DI.
  - `/healthz` uses `ConsumerHealth.Live()`. It is unhealthy when NATS is disconnected, when the router is stopped, or when any expected durable is unbound. There is a grace of 3 consecutive observations.
  - With kubelet's `periodSeconds: 20` and `failureThreshold: 3`, a disconnection of about 100 s restarts the pod, even though the connection reconnects by itself.
- **Logging.** 19 `logging.New()` calls in `cmd/**` use go-logging defaults: text on stdout, which GKE records as INFO.
  - `messaging/streams.go` logs through package-level `slog`: text on stderr, which GKE records as ERROR.
  - The DI logger (`provideLogger`) honours `LOGGING_FORMAT`, which is `json` in prod. It writes slog's `level` key. GKE currently maps `level` to severity, but only `severity` is documented.

## Goals / Non-Goals

**Goals:**
- Every backend binary survives a NATS, Zitadel or DB outage of up to 5 minutes at startup without exiting (spec: startup-dependencies).
- Probes never restart a process for a dependency outage, and never grow the DB pool (spec: health-probes).
- Every line a deployed binary writes is JSON with a documented severity key (spec: structured-logging).

**Non-Goals:**
- Connection budget and pool sizes (cloud-provisioning#624) and ERROR-log alert coverage (cloud-provisioning#625).
- Changing the error code that Zitadel-backed operations return when Zitadel is down. They keep returning Internal, as their operation specs state.
- High availability for NATS. It stays a single replica.
- Local analysis CLIs (`cmd/analyze-*`, `cmd/replay-ab-log`, `cmd/annotated-fixture`). They are not deployed, and their stderr output is text for a human at a terminal.

## Decisions

### D1. New spec slot `components/infrastructure/backend/process/<component>`

The schema's infrastructure slots are per audience and have "no shared slot". But these rules bind every backend process, and event consumers and jobs serve no audience at all.

Writing the rules under `fan/api/server` would claim they apply only to the fan API, and it would leave consumers and jobs without a home. This is a deliberate exception: a shared slot limited to process-level rules. It is added in three places, in the same plan PR:
- `scripts/check-spec-layout.py`
- the spec tree in the `context` of `openspec/config.yaml`
- the `specs` instruction of the `liverty-clean-arch` schema

Rejected alternative: duplicating each rule under every audience. That gives four copies of the same rule, and still no place for consumers and jobs.

### D2. NATS: retry the initial connect instead of failing

- **Publisher.** Add `nats.RetryOnFailedConnect(true)` and `nats.Timeout(5s)`.
  - With this option, `Connect` returns a connection in RECONNECTING state instead of an error (nats.go v1.49 `nats.go:528-536`, `2693-2698`). `conn.JetStream()` does no network I/O, so `NewPublisher` succeeds.
  - Publishing while disconnected is buffered, and the JetStream publish times out after 5 s.
  - Existing usecases log a failed publish and continue (e.g. `follow_uc.go:105-109`). So a call returns within 10 s and keeps its own effect (spec: "An API server serves without the message broker").
- **Consumers.** `ConnectNATS` blocks until the connection is actually up, with a 5-minute budget bounded by ctx. It does this with `RetryOnFailedConnect`, waiting for the first `ConnectedHandler`/`ReconnectHandler`. It must wait before the router binds durables, because `js.Consumer` is an API request.
  - This replaces the 30 s `connectBackoff`.
  - The health server already runs before DI, so waiting does not trip liveness.
- **Logging.** Connection state changes on the publisher connection are logged at WARNING (disconnect) and INFO (reconnect).

Rejected alternatives:
- **An initContainer that waits for NATS.** It is an extra piece per workload, the pod still crashes if NATS drops between init and connect, and the API stays down even for calls that do not need NATS.
- **Restoring an `EnsureStreams`-like gate.** It would block API readiness on NATS for no benefit.

### D3. Zitadel: static token endpoint, so construction has no network I/O

Build each client's token source with `profile.NewJWTProfileTokenSource(..., profile.WithStaticTokenEndpoint(issuer, issuer+"/oauth/v2/token"))` and pass it through `zitadelconn.WithJWTProfileTokenSource`.

The prod discovery document confirms `token_endpoint = https://auth.liverty-music.app/oauth/v2/token`. The token is fetched on the first RPC. A Zitadel outage then surfaces as an error of that RPC, which maps to Internal per the operation specs. The next call after recovery succeeds.

Rejected alternatives:
- **A retry loop around construction.** It still blocks startup, and a long outage still exits the process.
- **A lazy wrapper that constructs on first use.** More code than an option the library already provides.

### D4. DB at startup: bounded retry

`rdb.New` retries the initial ping with exponential backoff (1 s up to 15 s), for 5 minutes in total. Each failed attempt is logged at WARNING. The final failure is returned to `main`, which logs it once at ERROR.

### D5. API probes: a separate liveness service, a coalesced readiness check, and a startupProbe

- **Liveness service.** Register a gRPC health service named `liveness`. It reports SERVING whenever the process can answer, including during graceful shutdown, so a draining pod is not killed early. It never touches the database.
  - cloud-provisioning sets `livenessProbe.grpc.service: liveness` on the fan, admin, organizer and reception Deployments.
- **Readiness.** The empty service name, used by kubelet readiness and the Gateway (HealthCheckPolicy leaves `grpcServiceName` unset), reports NOT_SERVING while shutting down. Otherwise it answers from a cached DB check:
  - at most one check runs at a time (`singleflight`);
  - a result is reused for 5 s;
  - the check runs under its own context with a 10 s timeout, not under the probe's context.
  - Because the check is never abandoned, a probe timeout cannot leave an orphaned connection construction behind. At most one pool acquisition for health is in flight.
  - A probe that arrives while the check is running and has no fresh result waits until its own deadline, then answers from the last completed result. Before any result exists, it answers not ready.
- **Startup.** The Connect server, and with it the health service, only starts after DI. DI can now wait up to 5 minutes, so the four API Deployments get a `startupProbe` on the `liveness` service (`periodSeconds: 10`, `failureThreshold: 36`, so 6 minutes). This is the Kubernetes mechanism for slow-starting containers. It disables liveness until the first success, and needs no code change.

Rejected alternatives:
- **Dropping the DB check from readiness.** Then a pod that cannot reach the DB keeps receiving traffic.
- **Starting the health server before DI for the API.** That needs a second listener, or a split of the Connect server. A startupProbe is simpler.

### D6. Consumer liveness: count disconnection as degraded, not dead

Change `ConsumerHealth` so that a NATS disconnection which is still reconnecting does not count against liveness:
- Track `connected` (as today) and `closed` (the `ClosedHandler`, which is reached only when nats.go gives up).
- While disconnected, an unbound durable is expected and does not count either.
- Liveness fails only when the consumer is connected, or closed, and the router is stopped or a durable is unbound continuously for 2 minutes.
- Replace the count-based grace with a time-based one: unhealthy since a timestamp. That makes the spec's "2 minutes" independent of the probe period.

This keeps the 2026-07 wedge detection (connected, consuming nothing) and stops restarts during a NATS reschedule.

`readyz` is unchanged. Consumers receive no Service traffic, so readiness only gates the rollout.

### D7. Logging: one bootstrap logger built from the logging config, with the documented severity key

- Add `di.NewBootstrapLogger()`. It reads only `config.LoggingConfig` from the environment and calls `provideLogger`. If loading fails, it falls back to `logging.WithFormat(logging.FormatJSON)`.
  - Every `cmd/**/main.go` creates exactly one logger with it, shared by `run()` and the fatal log in `main()`.
  - The same function is used to create the DI logger, so the two never diverge.
- `provideLogger` adds a `logging.WithReplaceAttr` that writes the level as `severity`, mapping slog `WARN` to Cloud Logging's `WARNING`.
  - Why: `severity` is the documented special field (GKE "About GKE logs": "Structured logs can include a severity field"). The current `level` mapping works only by undocumented behavior.
  - In text format (local, `.env.test`) the key stays `level`.
- `connectWithRetry` takes the injected `*logging.Logger` instead of package-level `slog`.
- golangci-lint `forbidigo` rejects `slog.(Debug|Info|Warn|Error|Log|Default)` and `log.Print*` / `log.Fatal*` outside `_test.go` and the analysis CLIs.
- **Normal stops** (spec: "Normal stops and retries are not errors"):
  - `cmd/consumer/main.go` and `media-consumer`: ignore `http.ErrServerClosed` from `HealthServer.Start()`, which `http.Server` returns on every normal shutdown.
  - `pkg/shutdown.Shutdown` returns nil when `Init` was never called. If start-up failed before `Init`, there is nothing to clean up, and the cause is already logged by `main`.

### D8. Verification without dev

The dev environment is stopped, so verification uses unit tests, plus checks in prod after release:
- An embedded nats-server started late for D2.
- A fake issuer returning 503 for D3.
- A blocking DB stub with N concurrent `Check` calls, counting acquisitions, for D5.
- A fake clock for D6.
- A logger written to a buffer and parsed as JSON for D7.
- In prod after release:
  - `kubectl delete pod nats-0 -n nats` produces no backend restarts.
  - `textPayload:"level="` returns nothing for the new revision.
  - `jsonPayload.severity` is present.

## Risks / Trade-offs

- **[A truly broken deploy now takes up to 6 minutes to fail, instead of seconds.]** → The startupProbe and the 5-minute waits trade fast failure for surviving node events. The final failure is logged once at ERROR, which alerts.
- **[While NATS is down, publishes are lost.]** Usecases already treat publishing as best effort. → Unchanged from a NATS outage after startup today. Durable delivery is the outbox's job where it matters.
- **[A hard-coded Zitadel token endpoint path.]** → `/oauth/v2/token` is Zitadel's documented endpoint and matches the prod discovery document. A unit test pins the issuer-derived URL.
- **[Logs keyed `severity` instead of `level`.]** A saved log query or log-based metric that filters on `jsonPayload.level` would break. → On 2026-10-10, cloud-provisioning `main` had no `jsonPayload.level` reference. The alert policies filter on the entry's `severity`, which the documented key keeps setting. A task re-checks this before the backend release.
- **[The D1 slot weakens the per-audience rule.]** → Limited to process-level rules in the schema instruction. Any other shared rule still needs its own decision.

## Migration Plan

1. specification: plan PR with this change and the D1 layout updates. Merge.
2. backend: one PR with D2–D7. Release.
3. cloud-provisioning: one PR with the liveness `service: liveness` and the startupProbe for the four API Deployments. Merge it only after the backend release is deployed: before that, the `liveness` service does not exist, and probes would fail.
4. Verify in prod (D8), then `/opsx:verify` and archive.

Rollback: revert the cloud-provisioning PR first (probes back to the default service), then roll the backend image back to the previous tag.
