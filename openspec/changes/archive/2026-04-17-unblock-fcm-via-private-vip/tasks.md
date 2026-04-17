## 1. Backend — observability (ships independently, unblocks future debugging)

- [x] 1.1 Create branch `281-capture-http-error-body` off `origin/main` in backend worktree (liverty-music/backend#281)
- [x] 1.2 Extend `pkg/api/errors.go::FromHTTP` — body capture via shared `pkg/httpx.CaptureResponseBody` helper (1024 byte cap, sanitize, truncation indicator)
- [x] 1.3 Helper drains remainder into `io.Discard` for connection reuse; read failures silently skipped (original error preserved)
- [x] 1.4 `webpush/sender.go` — body captured before 410/4xx error mapping using same helper
- [x] 1.5 `fanarttv/logo_fetcher.go` — body captured before non-200/non-404 error path using same helper
- [x] 1.6 Unit tests: `pkg/httpx/body_test.go` (9 cases), `pkg/api/errors_test.go` (4 cases)
- [x] 1.7 Unit tests: `webpush/sender_test.go` (+2 body cases), `fanarttv/logo_fetcher_test.go` (+1 body case)
- [x] 1.8 `make lint` + all tests pass
- [x] 1.9 Opened backend PR liverty-music/backend#282; CI + review pending
- [x] 1.10 Backend PR #282 merged → Deploy Backend workflow running (run 24546200920)

## 2. Cloud-provisioning — PGA VIP switch

- [x] 2.1 Create branch `195-switch-pga-to-private-vip` in cloud-provisioning worktree (liverty-music/cloud-provisioning#195)
- [x] 2.2 CNAME target changed from `restricted.googleapis.com.` to `private.googleapis.com.`
- [x] 2.3 A record renamed to `pga-private-googleapis-a`; IPs changed to 199.36.153.8–11
- [x] 2.4 Comment block rewritten with rationale (private VIP, no VPC-SC, DNS affects all nodes)
- [x] 2.5 Pulumi preview verified via CI on PR (dev preview deployment #227, prod preview deployment #168)
- [x] 2.6 `make lint-ts` passes (1 pre-existing warning unrelated to this change)
- [x] 2.7 Opened cloud-provisioning PR liverty-music/cloud-provisioning#196; CI pending

## 3. Dev validation gate (after cloud-provisioning merges)

- [x] 3.1 Backend deploy success (run 24546200920); Pulumi dev auto-deploy triggered; new pods rolled out (server-app 68s, consumer-app 38s)
- [x] 3.2 Pod-internal curl: HTTP 400 "a TTL header must be provided" (FCM application layer) — PGA 403 is GONE
- [x] 3.3 NotifyNewConcerts RPC: HTTP 200, duration 584ms (vs 290ms when PGA was blocking)
- [x] 3.4 Server-app logs: 0 ERROR lines (was 2 "status 403" before fix) — push delivery succeeded silently (success = metric only, no log)
- [x] 3.5 Dev running on new VIP without googleapis regressions (Cloud SQL, Maps, Gemini all operational post-deploy)

## 4–5. Staging / Production promotion

_Staging environment does not exist yet. Production promotion deferred until staging is provisioned. The PGA private VIP configuration is already in the Pulumi codebase (main branch) so both environments will inherit it when provisioned._

## 6. Documentation

- [x] 6.1 Updated `backend/docs/debug-rpc-notify-new-concerts.md` with "How to verify delivery succeeded" + troubleshooting table (included in backend PR #282)
  - States an HTTP 200 RPC response means "pipeline ran", not "delivery succeeded"
  - Names the `RecordPushSend("success" | "gone" | "error")` metric and the server-app log line shape
  - Gives the exact `kubectl logs` query pattern (`kubectl logs -n backend -l app=server --tail=0 -f`) an operator should run in parallel with the curl invocation
  - Includes a short troubleshooting table: 403 body "Your client does not have permission" → PGA blocking non-VPC-SC service → see cloud-provisioning; 410 Gone → subscription invalidated → auto-cleanup ran; client err / timeout → webpush library internal
- [x] 6.2 Archive this change

