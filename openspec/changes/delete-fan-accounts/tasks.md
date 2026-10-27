## 1. Proto (specification)

- [ ] 1.1 Add `liverty_music.entity.v1.DeletionBlocker` (Kind enum + count), fan `UserService.ListDeletionBlockers` and `UserService.Delete` (with `id_token`, `min_len: 1`), and admin `UserService.GetByEmail` (email, max 165, returns `User` + `repeated DeletionBlocker`), following the `rpc-design` skill (design D1, D3); verify `buf lint` and `buf breaking` pass in CI
- [ ] 1.2 Release the specification version and confirm BSR generation finished (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3` shows success)

## 2. Entity operations (backend)

- [ ] 2.1 Declare `LotteryEntry.ListByUser` and implement it in the RDB repository; verify contract tests for "Entries for two ticket types" and "Never entered" pass (`components/entity/lottery-entry/list-by-user`)
- [ ] 2.2 Declare `Checkout.ListByUser` and implement it in the RDB repository; verify contract tests for "Two checkouts" and "Never checked out" pass (`components/entity/checkout/list-by-user`)
- [ ] 2.3 Add `User.SerializeDeletion` (exclusive `pg_advisory_xact_lock` on `user:<id>`, design D2), and in `Checkout.GetOrCreateHeld`, `LotteryEntry.Create` and `ResaleListing.Create` take the shared lock of the same key and fail with NotFound when the users row is gone; verify an integration test where a create blocked during a deletion stores nothing and fails with NotFound, and the existing contract tests of the three creators still pass

## 3. Usecases (backend)

- [ ] 3.1 Implement `UserUseCase.ListDeletionBlockers`; verify unit tests with the operations mocked for "Ticket for a concert next week", "Ticket for today's concert", "Ticket for a past concert", "Listed resale", "Entry awaiting its draw", "Card authorized, not yet charged", "Lapsed hold", "Finished entries and withdrawn listings" and "Unknown user" (`components/usecase/user/list-deletion-blockers`)
- [ ] 3.2 Change `UserUseCase.Delete` to run ListDeletionBlockers, DeleteIdentity and User.Delete inside `User.SerializeDeletion`; verify unit tests for "Existing user", "Unknown user", "User holding a ticket", "User whose concerts are over", "User with a listed resale", "User with an entry awaiting its draw", "User paying for tickets", "User with only refunded purchases" and "Retry after the record failed" (`components/usecase/user/delete`)
- [ ] 3.3 Implement `UserUseCase.GetByEmail`; verify unit tests for "Registered address" and "Unregistered address" (`components/usecase/user/get-by-email`)

## 4. RPC handlers and configuration (backend, cloud-provisioning)

- [ ] 4.1 Add the fresh-sign-in check (design D3: ID token signature, issuer, `aud` contains the fan client id, `sub` equals the caller's, `auth_time` within 300 s) and the fan `ListDeletionBlockers` and `Delete` handlers; verify handler tests for "Deleting only oneself", "Caller holds an upcoming ticket", "Nothing in progress", "Fresh sign-in", "Old sign-in", "Proof of another identity", "No proof" and "Caller with an upcoming ticket" (`components/adapter/fan/api/rpc/user`)
- [ ] 4.2 Add the admin `GetByEmail` handler; verify handler tests for "Non-admin looks up a user", "Admin finds a fan", "Fan with nothing in progress", "Unregistered address" and "Malformed address", and that the existing Delete tests still pass (`components/adapter/admin/api/rpc/user`)
- [ ] 4.3 Add `DeleteIdentity` to the identity service's fan API procedures and build the identity remover on the fan workload (design D3, "Where the identity is removed"); verify the identity listener tests: the fan API's listener serves `DeleteIdentity` and `VerifyEmail` and refuses every other procedure with PermissionDenied
- [ ] 4.4 (cloud-provisioning) Set `FAN_OIDC_CLIENT_ID` (the fan app's Zitadel client id) on the fan API in the prod and dev overlays, and update the identity NetworkPolicy comment to say the fan API's listener also serves `DeleteIdentity` (design D3); merge and verify in prod that the fan API pods carry the variable
- [ ] 4.5 Release and deploy the backend after 4.4 is in prod; verify in prod that the rollout finished and that the admin `GetByEmail` for the owner's own address returns the User with no blocker (read-only check)

## 5. Fan frontend

- [ ] 5.1 Upgrade the generated schema package and swap placeholder types (`consume-proto-release` skill); verify `make check` passes
- [ ] 5.2 Generalize `PasskeyAuthService` into the fresh-sign-in service with a return screen in the request state, and route `/auth/passkeys-callback` by it (design D4); verify unit tests for both return targets, and run passkey management in prod with Playwright to confirm it still opens after a fresh sign-in
- [ ] 5.3 Add the withdrawal route (blockers, statements, confirmation dialog, fresh sign-in, Delete, local sign-out and `analytics.reset()`, deleted-account view; design D5, D6) with ja/en copy; verify component tests for "Fan with an upcoming ticket", "Read fails", "Fan with nothing in progress", "Fan confirms", "Fan cancels", "Fresh sign-in abandoned", "Different account", "Deletion succeeds" and "Ticket bought in another tab" (`components/infrastructure/fan/web/route/delete-account`)
- [ ] 5.4 Add the Delete account control below Sign Out in Settings; verify component tests for "Signed-in fan" and "Guest" (`components/infrastructure/fan/web/route/settings`)
- [ ] 5.5 Add the withdrawal section to the Privacy Policy (ja/en) with the 7-year retention period (design D7); verify the legal-document test for "Withdrawal disclosed" passes (`components/infrastructure/fan/web/global/legal-document`)
- [ ] 5.6 Release and deploy the frontend; with Playwright against prod, open Settings → Delete account as the prod test user (who holds no blocker) and confirm the statements and the delete control appear, then cancel at the confirmation dialog

## 6. Admin frontend

- [ ] 6.1 Add the admin Users route and its navigation link (email field, user and blockers, confirmation dialog, outcome); verify component tests for "Registered fan", "Unregistered address", "Fan with an upcoming ticket", "Admin confirms", "Admin cancels", "Deleted" and "Blocker appeared meanwhile" (`components/infrastructure/admin/web/route/users`)
- [ ] 6.2 Deploy and, signed in to the prod admin console, look up the owner's address and confirm name, email, id and "no blocker" are shown without deleting

## 7. Stories (prod E2E)

- [ ] 7.1 Add a prod E2E for `stories/delete-my-account` that signs up a throwaway account, deletes it from Settings after the fresh sign-in, and confirms the passkey no longer reaches an account ("Fan whose concerts are over" without a ticket, "Signing up again"); record the scenarios that need a held ticket ("Ticket for next week", "After the concert") as known gaps in `docs/ci-coverage-gaps.md`; verify the E2E passes against prod
- [ ] 7.2 Add a prod E2E for `stories/delete-a-fan-account` that deletes a throwaway account from the admin Users screen ("Request by email") and records "Fan with a ticket for an upcoming concert" as a known gap; verify it passes against prod, or record the admin Google sign-in limit as the gap if the admin session cannot be automated
