## 1. Runtime config plumbing

- [ ] 1.1 Add optional `rpcTimeoutMs` to the `AppConfig` type in `shared/config/app-config.ts`, validated as an optional positive number
- [ ] 1.2 Default `rpcTimeoutMs` to `10_000` when absent/invalid during validation (define a named constant, e.g. `DEFAULT_RPC_TIMEOUT_MS`); ensure a malformed value falls back rather than failing bootstrap
- [ ] 1.3 Add the optional `rpcTimeoutMs` field to the tracked `config.json` (and note the additive field for per-environment ConfigMaps in `cloud-provisioning`)

## 2. Apply the default RPC timeout

- [ ] 2.1 Pass `defaultTimeoutMs: config.rpcTimeoutMs` into `createConnectTransport(...)` in `src/services/grpc-transport.ts`
- [ ] 2.2 Confirm no per-method/per-call `timeoutMs` overrides are added (single default only)
- [ ] 2.3 Verify the value flows through all three apps (fan-web, admin, organizer) via the shared transport factory

## 3. Bound the Service-Worker fetches

- [ ] 3.1 Add `AbortSignal.timeout(~10_000)` to the PostHog capture `fetch()` in `src/lib/analytics/notification-interaction.ts` (`sendInteraction`); confirm an abort takes the existing throw → stash → Background-Sync resend path with the reused `$insert_id`
- [ ] 3.2 Add `AbortSignal.timeout(~5_000)` to the cache-miss `fetch()` in `src/lib/push/push-renewal.ts` (`readVapidPublicKeyCacheFirst`); confirm an abort returns `null` (skip renewal, retry later) without throwing

## 4. Tests

- [ ] 4.1 Unit-test `AppConfig` validation: present value is used; absent/invalid falls back to 10s
- [ ] 4.2 Test that the transport is constructed with `defaultTimeoutMs` from config (fake config → assert transport option)
- [ ] 4.3 Test `sendInteraction` timeout path: a stalled fetch aborts and is stashed for resend (reused insert_id)
- [ ] 4.4 Test `readVapidPublicKeyCacheFirst` timeout path: a stalled cache-miss fetch aborts and returns `null` without throwing
- [ ] 4.5 (Optional) Test that an RPC exceeding the deadline rejects with `Code.DeadlineExceeded` and is not retried

## 5. Verification

- [ ] 5.1 `make check` (lint + typecheck + unit tests) passes in `frontend/`
- [ ] 5.2 Manually confirm a hung RPC aborts at ~10s (e.g. against a stalled/slow endpoint) and the app surfaces the error instead of an infinite spinner
- [ ] 5.3 Post-ship: review OTel RPC-duration p99 (including the auth-retry path) to confirm 10s does not clip legitimate recovery; adjust `rpcTimeoutMs` via config if needed
