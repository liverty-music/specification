## Context

See proposal.md - Why. Current code (backend and frontend `origin/main`, 2026-10-19):

- `backend internal/usecase/payout_account_uc.go:60-150`: `Get` loads the Organizer (for the owner email), and on `GetByOrganizerID` NotFound calls `provisionAndPersist` (Stripe `Create` with idempotency key `connected-account:<organizer id>` → `Upsert` pending → `CreateOnboardingLink`). With an account it refreshes the status and, while not active, creates a new Account Link on every call. Link failures are logged and swallowed.
- `backend internal/adapter/rpc/payout_account_handler.go:55-79`: maps every NotFound from the usecase to PermissionDenied ("organizer gone meanwhile") and copies `onboarding_url` into `GetResponse`.
- `backend internal/infrastructure/payment/stripe_settlement.go:393-397`: `CreateOnboardingLink` passes the same address as Stripe's `refresh_url` and `return_url`. The address is `STRIPE_ONBOARDING_RETURN_URL` (`pkg/config/config.go:1203`), set in cloud-provisioning to `https://organizer.liverty-music.app/` (prod `k8s/namespaces/backend/overlays/prod/fan-api/configmap.env:75`) and `https://organizer.dev.liverty-music.app/` (dev, line 69). `/` opens the console landing, which forwards to Home, not to Settings.
- `frontend organizer/home/home-route.ts:96-107` and `organizer/settings/settings-route.ts:157-166` call `PayoutAccountClient.get`; any failure becomes the "could not be loaded" state. Settings opens `onboardingUrl` with `target="_blank"` and re-reads the status on `visibilitychange`. Settings lives at `/organizers/{organizer id}/settings`, the payout part at `#payout` (`organizer/model/concert-model.ts:208-209`).
- `payout_accounts` (`backend internal/infrastructure/database/rdb/schema/schema.sql:988`) has `organizer_id` as primary key, `ON DELETE CASCADE` from `organizers`.

## Goals / Non-Goals

**Goals:**

- No call opens a payout account or creates an onboarding link except `StartOnboarding`.
- `Get` is a plain read with NotFound for "no account yet".
- The member leaves for Stripe and comes back in one tab, through the return address configured today.

**Non-Goals:**

- No "not set up" status value, no optional `payout_account` in `GetResponse` (owner decision 2026-10-19: NotFound is enough for the client).
- No change to settlement release, Organizer Delete, or the PayoutAccount entity and its operations.
- Closing the provider accounts of removed test Organizers (kept, as Organizer Delete keeps provider records).

## Decisions

### D1. Get reads only; NotFound passes through the boundary

`PayoutAccountUseCase.Get(ctx, organizerID) (*entity.PayoutAccount, error)`: `GetByOrganizerID` (NotFound returned as is), then the existing status refresh. It no longer calls `Organizer.Get`: the owner email was only needed to open the account, and the boundary has already resolved the caller's Organizer through `OrganizerUseCase.ResolveCaller` (PermissionDenied / FailedPrecondition). The handler drops its NotFound→PermissionDenied mapping for Get, so `connect.CodeNotFound` reaches the client. NotFound is therefore unambiguous on the wire: an unknown or foreign Organizer never gets past the gate.

Alternatives rejected: a `NOT_SET_UP` enum value or an optional `payout_account` (more concepts, and every reader must handle a second "absent" shape; owner rejected); keeping `Organizer.Get` in Get only to keep the old "Unknown Organizer" scenario (an extra read with no caller that needs it).

### D2. StartOnboarding: name and contract

`rpc StartOnboarding(StartOnboardingRequest) returns (StartOnboardingResponse)`. Checked against `.claude/skills/rpc-design/SKILL.md`: it is a domain verb on the PayoutAccount's own service, takes no caller id ("The caller is never named"), and verb-plus-object names are already used (`AuthorizeCard`, `AssociateArtist`). "Onboarding" is PayoutAccount vocabulary (its status is the "payout onboarding status"; the operation is `CreateOnboardingLink`), so no undefined term enters the API. No conflict. The bare `Start` (the skill's create-or-resume verb, as in `IdentityVerificationService.Start`, which also returns a redirect URL) would also fit; `StartOnboarding` is kept as decided with the owner because it reads as the member's action and pairs with `onboarding_url`.

Usecase `StartOnboarding(ctx, organizerID) (onboardingURL string, err error)`:

1. `Organizer.Get` (NotFound → the handler answers PermissionDenied, as the old Get did for a vanished Organizer).
2. `GetByOrganizerID`; on NotFound `Create(organizerID, owner email)` → `Upsert` pending (the old `provisionAndPersist` minus the link).
3. `CreateOnboardingLink(providerAccountID, returnURL)`; a failure fails the call (unlike the old Get, the link is the whole point; a swallowed failure would leave the button doing nothing).

No status refresh (Get does that, and Home reads Get when the member returns). No guard on an active account: the console never offers the action then, and refusing it would add a FailedPrecondition branch no screen reaches.

Double clicks and retries: Settings disables the action while a call is in flight; across calls, `Create`'s idempotency key returns the same provider account within 24 hours (`components/entity/payout-account/create` "Create does not open a second account on retry") and `Upsert` keeps one row per Organizer, so an Upsert or link failure followed by a retry reuses the account.

### D3. Proto

```proto
service PayoutAccountService {
  // Get ... Possible errors: + NOT_FOUND: The caller's Organizer has no payout account yet; call StartOnboarding.
  rpc Get(GetRequest) returns (GetResponse);
  // StartOnboarding opens the caller's Organizer's PayoutAccount at the payment provider when it has none
  // and returns a fresh single-use onboarding URL.
  // Possible errors: FAILED_PRECONDITION (deactivated), PERMISSION_DENIED, UNAUTHENTICATED, UNAVAILABLE.
  rpc StartOnboarding(StartOnboardingRequest) returns (StartOnboardingResponse);
}

message GetResponse {
  entity.v1.PayoutAccount payout_account = 3 [(buf.validate.field).required = true];
  reserved 1, 2;
  reserved "account", "onboarding_url";
}

message StartOnboardingRequest {}

message StartOnboardingResponse {
  // The provider-hosted onboarding page; single use, valid for a short time.
  entity.v1.Url onboarding_url = 1 [(buf.validate.field).required = true];
}
```

`entity.v1.Url` (URI, 1 to 2048 characters) follows `IdentityVerificationService.StartResponse.redirect_url`, instead of the bare `string` the removed field used. Removing field 2 fails `buf breaking`; the PR carries the `buf skip breaking` label. Release as the next minor (v0.90.0 after v0.89.0).

### D4. Return address: unchanged

Stripe's `return_url` and `refresh_url` both stay `STRIPE_ONBOARDING_RETURN_URL` (`stripe_settlement.go:396-397` passes the usecase's `returnURL` as both), which is `https://organizer.liverty-music.app/` in prod: the landing, which forwards to the caller's Home. Home reads Get and shows the 要対応 item while the account is not active, and that item opens Settings at the payout account (owner decision on #1183, 2026-10-19). StartOnboarding passes the same `returnURL` the old Get passed, so no backend config and no cloud-provisioning change.

Alternatives rejected: a console address that forwards to `/organizers/{id}/settings#payout`, or the backend building that URL from a console base URL. Each adds a route or config semantics for one fewer click after Stripe, and Home already says what is left to do.

### D5. Frontend

- `PayoutAccountClient.get` returns `PayoutAccountView | null`: `null` on `Code.NotFound` (a normal state, not logged as a failure); other errors propagate as today. `onboardingUrl` leaves `PayoutAccountView`. New `startOnboarding(signal?) → string`.
- Home: the home model's payout source becomes "absent | status"; absent and not-active both produce the 要対応 item (`organizer/model/home-model.ts:108-109`).
- Settings: three states (`none`, account, error). The button calls `startOnboarding()`, then `window.location.assign(url)`; it is disabled while the call runs. On failure the page shows `settings.payout.startFailed` (Stripe のページを開けませんでした。もう一度お試しください。) chosen from code, never the server text (archived `web-error-copy`). Drop the `visibilitychange` re-read (no second tab), `target="_blank"`, and the `newTab` / `opensNewTab` copy; add the same-tab explanation (e.g. Stripe のページに移動します。入力が終わると、Stripe からコンソールのホームに戻ります。), `settings.payout.start` (Stripe で登録する) and an external-site marker for screen readers. English catalog entries change alongside.

### D6. Production clean-up of the test Organizers

`fan-test` (01a142c8-2971-7993-a41f-620783586665) and `fan-test-2` (01a142c8-64c5-7b0d-b3e9-4b6c6768834b) are deactivated and hold `payout_accounts` rows from the old Get; Organizer Delete refuses them (`components/usecase/organizer/delete` "Delete SHALL check ... a payout-account record"). The admin console has no way to remove a payout account, and adding one for two test rows is not worth a feature. So: break-glass login as `postgres` (cloud-provisioning `docs/runbooks/cloud-sql-access.md` "Break-glass login as `postgres`"), the owner confirms the write at that time, then in one transaction `DELETE FROM payout_accounts WHERE organizer_id IN ('01a142c8-2971-7993-a41f-620783586665','01a142c8-64c5-7b0d-b3e9-4b6c6768834b')` expecting 2 rows, then Delete both from the admin Organizers screen, then read back that neither an `organizers` row nor a `payout_accounts` row remains (and the Organizations are gone at the identity provider, as Delete promises). Their Stripe accounts (Restricted, never paid) stay. Done after the backend is in production, so no Home visit re-opens them meanwhile (they are deactivated, so Get already fails with FailedPrecondition; the order is belt and braces).

## Risks / Trade-offs

- [Between the backend and frontend deploys the deployed console is wrong] An Organizer without an account sees "payout status could not be loaded" on Home and Settings (old client treats NotFound as a failure), and a pending Organizer sees no Stripe button (old client reads the now-absent `onboarding_url`). → Accepted: the product has no real Organizers yet (`liverty-music/CLAUDE.md` "Current operating state"). Deploy the frontend right after the backend; no compatibility shim (keeping `onboarding_url` populated for one release would mean a second proto change and Get creating links again).
- [Frontend before backend would break onboarding] `StartOnboarding` would answer Unimplemented. → The frontend is released only after the backend release is confirmed in production (task 5.1).
- [An Organizer that starts onboarding and abandons it keeps an account] Same as today, but now only after an explicit request. → Nothing to do; Delete still refuses it, which is the intended guard for an Organizer that may have provider records.
- [Stripe's return and refresh land on Home, not on Settings] One more click (the 要対応 item) to see the status or continue an expired link. → Owner decision; Home already names what is left to do.
- [Break-glass write in production] → Owner confirms at that time; one transaction with an expected row count, read back afterwards.

## Migration Plan

1. specification: proto PR (`buf skip breaking`), merge, Release v0.90.0, wait for `buf-release.yml`.
2. backend: consume v0.90.0, Get read-only, StartOnboarding, handler; release; confirm the rollout in production.
3. frontend: consume v0.90.0, client, Home, Settings; release right after step 2 is in production.
4. Production check and clean-up (D6), then close #1176.

Rollback: backend and frontend roll back together to their previous releases (the old frontend works with the old backend); the proto release stays (old backends ignore it).

## Open Questions

None.
