## 1. Consumer shutdown ordering (D1)

- [x] 1.1 Refactor `cmd/consumer/main.go`: after `<-ctx.Done()`, drain `errChan` to wait for `Router.Run()` to complete before returning (ensures all in-flight handlers finish before shutdown phases execute)
- [x] 1.2 Verify `Router.Run()` returns cleanly on context cancellation by reviewing the select/errChan interaction — ensure no goroutine leak or deadlock

## 2. HealthServer lifecycle fix (D2)

- [x] 2.1 Add `defer healthSrv.Close()` in `cmd/consumer/main.go` immediately after the `go healthSrv.Start()` goroutine, before DI initialization
- [x] 2.2 Verify double-close safety: Drain phase calls `Close()` again via `shutdown.AddDrainPhase(healthSrv)` — confirm `http.Server.Shutdown()` is idempotent

## 3. Nil-safe shutdown across all entry points (D3)

- [x] 3.1 Add `fallbackShutdownTimeout` constant and nil-guard for `app` in `cmd/consumer/main.go` defer block; use `bootLogger` instead of `app.Logger` on the error path
- [x] 3.2 Apply same nil-guard pattern to `cmd/api/main.go`
- [x] 3.3 Apply same nil-guard pattern to `cmd/job/concert-discovery/main.go`
- [x] 3.4 Apply same nil-guard pattern to `cmd/job/artist-image-sync/main.go`

## 4. Validation

- [x] 4.1 Run `make check` in backend repo to ensure all linting and tests pass
- [x] 4.2 Manual smoke test: start consumer locally, send SIGTERM, verify shutdown log output shows phased teardown in correct order
