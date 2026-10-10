## 1. Spec tree slot (specification, in the plan PR)

- [x] 1.1 Allow `components/infrastructure/backend/process/<component>` in `scripts/check-spec-layout.py` (pattern and the "allowed:" message), add the slot to the spec tree in the `context` of `openspec/config.yaml`, and describe it in the `specs` instruction of the `liverty-clean-arch` schema as the one shared slot, for rules that bind every backend process (design D1). Verify `python3 scripts/check-spec-layout.py` passes with this change's three delta specs, and `openspec validate harden-backend-process-lifecycle --strict` passes

## 2. Structured logging (backend, components/infrastructure/backend/process/structured-logging)

- [ ] 2.1 Add `di.NewBootstrapLogger()`, which reads `config.LoggingConfig` from the environment, calls `provideLogger`, and falls back to JSON on a config error. Make `provideLogger` write the level as `severity` (`WARN` → `WARNING`) in JSON format (design D7). Verify unit tests that parse the buffered output as JSON cover the scenarios "Startup message" (INFO) and "Process gives up at startup" (one ERROR entry naming the dependency), and that text format still uses `level`
- [ ] 2.2 Replace every `logging.New()` in `cmd/{api,consumer,consumer/media-consumer,job/*}/main.go` with one `NewBootstrapLogger()` per binary, shared by `run()` and the fatal log in `main()`, and use it for the job logger in `cmd/job/normalize-venue-names`. Verify `git grep -n 'logging.New()' -- cmd` returns nothing, and `go build ./...` passes
- [ ] 2.3 Stop logging normal stops as errors: ignore `http.ErrServerClosed` from `HealthServer.Start()` in event-consumer and media-consumer, and make `shutdown.Shutdown` return nil when `Init` was never called (design D7). Verify unit tests for the scenarios "Normal shutdown" (no ERROR entry) and "Failed start" (exactly one ERROR entry for the start)
- [ ] 2.4 Pass the injected `*logging.Logger` to `connectWithRetry` instead of package-level `slog`, logging each retry at WARNING. Add a golangci-lint `forbidigo` rule that rejects package-level `slog` and `log.Print*` / `log.Fatal*` outside `_test.go` and `cmd/{analyze-*,replay-ab-log,annotated-fixture}`. Verify the scenario "Waiting for the broker" with a unit test, and verify `make lint` passes and fails on a probe file that calls `slog.Info`

## 3. Startup dependencies (backend, components/infrastructure/backend/process/startup-dependencies)

- [ ] 3.1 Publisher: add `nats.RetryOnFailedConnect(true)` and `nats.Timeout(5s)`, and log connect, disconnect and reconnect on the publisher connection (design D2). Verify unit tests: `NewPublisher` against a closed port returns a publisher and no error; for the scenario "Start while the broker is down", the API DI completes and a read call succeeds; for "Follow while the broker is down", the follow is stored and the call returns within 10 s
- [ ] 3.2 Consumers: make `ConnectNATS` wait for the first successful connect, with a 5-minute budget bounded by ctx, before the router binds durables (design D2). Verify the scenario "Broker back within the wait" with an embedded nats-server started 2 s late, and a test that the wait returns an error after the budget
- [ ] 3.3 Zitadel: build the three clients' token sources with `profile.WithStaticTokenEndpoint(issuer, issuer+"/oauth/v2/token")` through `zitadelconn.WithJWTProfileTokenSource` (design D3). Verify unit tests against a fake issuer for the scenarios "Start while the sign-in service is down" (construction makes no HTTP request) and "Recovery without restart" (503 then 200: the second identity removal succeeds), plus a test pinning the token endpoint URL
- [ ] 3.4 DB: retry the initial ping in `rdb.New` with backoff from 1 s up to 15 s, for 5 minutes in total, logging each attempt at WARNING (design D4). Verify the scenario "Database unreachable beyond the wait" with a fake clock: the attempts span at least 5 minutes, and then an error is returned

## 4. Health probes (backend, components/infrastructure/backend/process/health-probes)

- [ ] 4.1 Register the gRPC health service `liveness`, which reports SERVING without touching the database, including while shutting down (design D5). Verify the scenario "Database unreachable" under "API liveness reflects only the process" with a handler test against an unreachable DB stub
- [ ] 4.2 Make the readiness check (empty service name) answer from a cached DB check: `singleflight`, a 5 s result TTL, the check running under its own 10 s context, and NOT_SERVING while shutting down (design D5). Verify handler tests for the readiness scenarios "Database unreachable" and "Shutting down", and for "Concurrent checks against a slow database": 10 concurrent `Check` calls against an 8 s blocking stub produce one DB check and one pool acquisition
- [ ] 4.3 Make `ConsumerHealth` time-based: a disconnection that is reconnecting does not count, and liveness fails after 2 minutes of being connected (or closed) with the router stopped or a durable unbound (design D6). Verify unit tests with a fake clock for the scenarios "Broker restarts" (3 minutes disconnected: alive) and "Connected but not consuming" (unbound for 2 minutes: not alive)

## 5. Backend release (backend)

- [ ] 5.1 Re-check that cloud-provisioning has no log query, metric or alert filtering on `jsonPayload.level` (`git grep 'jsonPayload.level'`), open the backend PR citing this change, merge it, and cut a release. Verify CI is green and the release's Deploy Backend run (including `dispatch-prod-pin`) succeeds

## 6. Probe configuration (cloud-provisioning, after task 5.1 is deployed)

- [ ] 6.1 For fan-api, admin-console-api, organizer-console-api and reception-api: set `livenessProbe.grpc.service: liveness`, and add a `startupProbe` (gRPC, service `liveness`, `periodSeconds: 10`, `failureThreshold: 36`). Leave readiness and the Gateway HealthCheckPolicy on the default service (design D5). Verify `make lint` (kubeconform) passes, and that after ArgoCD sync the four Deployments roll out Healthy

## 7. Production verification

- [ ] 7.1 Delete the NATS pod in prod (`kubectl delete pod nats-0 -n nats`). Verify that no backend container restarts (`restart_count` delta 0), that there is no `no servers available for connection` exit, that no Container Crash Loop incident opens, and that event-consumer resumes consuming (JetStream consumer pending drops back to 0)
- [ ] 7.2 Verify in Cloud Logging that the new revision emits no plain-text lines (`textPayload:"level="` returns nothing), that entries carry `jsonPayload.severity`, and that a rollout of event-consumer records no ERROR entry
