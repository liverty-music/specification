## 1. Fix A — Disable automaticSilentRenew

- [x] 1.1 Add `automaticSilentRenew: false` to `createSettings()` in `shared/services/auth-service.ts`
- [x] 1.2 Remove the stale comment referencing `automaticSilentRenew` behaviour from `restoreSession()` if it no longer applies
- [x] 1.3 Run `make check` in the frontend repo and confirm no type errors or test failures

## 2. Fix B — Singleton refresh promise in connect-error-router

- [x] 2.1 Add module-level `let refreshPromise: Promise<User | null> | null = null` to `src/services/connect-error-router.ts`
- [x] 2.2 Replace the inline `signinSilent()` call in `createAuthRetryInterceptor` with the singleton pattern: check `refreshPromise`, start if null, always await the shared promise, clear in `.finally()`
- [x] 2.3 Update `test/services/connect-error-router.spec.ts` to cover the concurrent-401 deduplication scenario (two simultaneous Unauthenticated errors → one `signinSilent()` call)
- [x] 2.4 Run `make check` in the frontend repo and confirm all tests pass

## 3. Ship to prod

- [x] 3.1 Run pre-commit review (`/pre-commit-review`), fix any findings
- [x] 3.2 Commit both fixes following the Liverty-Music commit convention (body + `Refs:` footer)
- [x] 3.3 Open PR, wait for CI green, merge
- [x] 3.4 Cut a release tag (PATCH bump from current) and confirm `dispatch-prod-pin` and `Bump Prod Pin` CI complete successfully
- [x] 3.5 Verify in prod: open the PWA, confirm no `RefreshTokenInvalid` in Zitadel logs after SW update, and confirm update snack bar appears and reload completes without forced logout
