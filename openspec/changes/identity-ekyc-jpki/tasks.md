<!-- MVP SCOPE (2026-09-02, see design.md "MVP scope & corrections"):
     - Client path = PocketSign **Stamp** (stamp.v1.SessionService: CreateSession →
       PocketSign **app** via redirectUrl → FinalizeSession), riding on Verify.
       NOT an embedded SDK, NOT the デジタル認証アプリ path.
     - MVP = **JPKI-only**. 運転免許証 (Verify CardInfo) fallback = POST-MVP (task 5.3).
     - MVP stores **only provider_user_id**; verified-name (基本4情報 via 署名用証明書 + Consent)
       = POST-MVP. Covered-ticket 本人確認 in MVP = ④ self-declared name+contact. -->

## 0. Prerequisites (long-lead — start in parallel, non-code)

- [ ] 0.1 **Onboard Pocket Sign (PocketSign Verify)**: 加盟契約 (ride their 認定PF status — no own 主務大臣認定), register on PocketSign Platform, ¥300k init + per-verify fees, use the free sandbox for PoC (~2-3mo Verify integration lead time) <!-- MVP DECISION 2026-09-03: 加盟契約 DEFERRED to POST-MVP. The MVP runs the FREE mock/sandbox (verify.mock.p8n.app) in ALL envs INCLUDING PROD (see §7 deployment tasks + design "MVP scope & corrections"); the ¥300k contract + prod tenant (verify.p8n.app) are a single config flip made only after the MVP is proven. This task stays open but is NO LONGER an MVP blocker. -->
- [ ] 0.2 Legal/privacy review: JPKI-only (outside 番号法, never 個人番号/serial), 個情法 利用目的/最小保持(provider_user_idのみ)/削除, Pocket Sign 利用規約 目的外利用 clauses, no 犯収法 取引時確認, data residency (越境), fallback fairness
- [ ] 0.3 Resolve Pocket Sign spikes S1-S6 (see design Open Questions): スマホJPKI cert support + same provider user ID; data minimization (provider user ID without PII); 目的外利用 limits; 越境; licence-path dedupe; proto field mapping <!-- PARTIAL 2026-09-02 (see pocket-sign-integration-notes.md, from the public pocketsign.verify.v2 BSR schema): S6 RESOLVED (User.userId→provider_user_id opaque string; JPKICard/JPKIMobile Auth/Signature=our JPKI; Verification.isNewUser=dedupe signal; serialNumberMac=MAC not raw serial; CheckUserStatus/CertificateStatus.checkPurpose=現況確認+J-LIS). S1/S2/S5 strong schema evidence (still confirm userId across renewal on a live account; licence is a separate JPKI-less product=WEAK dedupe confirmed). S3/S4 (目的外利用 contract terms / 越境) remain for the 0.2 legal review — not answerable from the schema. -->


## 1. Proto / entity (specification → BSR)

- [x] 1.1 Define `IdentityVerification` (user_id, method enum JPKI/DRIVER_LICENCE, `provider_user_id` = the verification provider's ID for the User, dedupe_strength enum STRONG/WEAK, verify_time, status) — type-safe IDs, protovalidate, **no 基本4情報 field by default**
- [x] 1.2 Surface to ④/⑤ whether a fan is verified <!-- Shipped as an account-level verification level; unify-ticket-sales (D11, task 2.7) removed it: a client treats an Active IdentityVerification as verified. -->
- [x] 1.3 Add a per-sale **verification requirement** (none / verified-any / JPKI-only) settable by organizer/admin
- [x] 1.4 RPCs: `IdentityVerificationService.Start` / `Create` (via the provider's session), 現況確認 `Recheck`, `Get()`; organizer `TicketSaleService.SetVerificationRequirement`
- [x] 1.5 protovalidate; buf lint/breaking; merge PR → Release → BSR gen <!-- DONE 2026-09-02: spec PR #893 merged, Release v0.59.0 cut, buf-release.yml BSR gen success. -->
<!-- NOTE: the requirement (1.3/1.4) is set on the sale, since the first-party entry gate is the TicketSale (there is no separate first-party Event-level sale config); unify-ticket-sales moved it there. It is also settable when the sale is created (TicketSaleService.Create). -->
<!-- Proto surface, under the names unify-ticket-sales gives it (D11, D16, D17; v0.59.0 shipped earlier names): entity/v1/identity_verification.proto (IdentityVerificationId, ProviderUserId, VerificationMethod, DedupeStrength, VerificationStatus, VerificationRequirement enums + IdentityVerification); entity/v1/ticket_sale.proto (TicketSale.verification_requirement); rpc/identity_verification/v1/identity_verification_service.proto (Start/Create/Recheck/Get); rpc/organizer/ticket_sale/v1 (TicketSaleService.SetVerificationRequirement). The account-level verification level that v0.59.0 added to user.proto is removed. -->
<!-- Design note: ProviderUserId validation kept a bounded opaque string (not strict UUID) pending spike S6 (proto field mapping vs pocketsign.verify.v2). -->


## 2. Backend — Pocket Sign verification

- [ ] 2.1 Integrate **PocketSign Stamp** (`stamp.v1.SessionService`: `CreateSession` → PocketSign app via `redirectUrl` → `FinalizeSession`, riding on Verify) to verify the fan and obtain the provider user ID; accept physical card AND スマホJPKI; **delete the raw certificate/response immediately** after the call <!-- REOPENED 2026-09-02: the shipped VerifyClient (backend #428/#429) targets verify.v2 VerifyForDigitalIdentificationApp (デジタル認証アプリ path) = WRONG for our PWA plan; it is inert (config-gated) but MUST be rewritten to the Stamp SessionService path. The hand-rolled Nonce + `data` approach is dissolved by Stamp (the Session manages the challenge/callback). Interim scaffolding retained: IdentityVerifier interface + StubVerifier (UNAVAILABLE), config gate, dedupe/privacy usecase (2.2-4.2) are path-agnostic and stay. -->
- [x] 2.2 On success: create an Active `IdentityVerification` with `provider_user_id`, which marks the fan verified; never store the 個人番号 or raw serial <!-- Create usecase: only the provider user ID stored. Whether the fan is verified is derived from the status (Active). -->
- [x] 2.3 **現況確認** periodic re-check (revocation / 基本4情報 change / expiry) → flag for re-verification (not hard-lock) <!-- Recheck usecase: flags NEEDS_REVERIFICATION, does not hard-lock. -->

## 3. Backend — dedupe + per-person signal

- [x] 3.1 Enforce **≤1 Active IdentityVerification per `provider_user_id`** (UNIQUE); rely on provider user ID stability across renewal (no 基本4情報 re-link needed — S1) <!-- Partial unique index on (provider_user_id WHERE status=Active), created in migration 20260902000000 under the column's earlier name. -->
- [x] 3.2 Second provider user ID match handling: reject with a clear message + account-recovery/support path (no silent second IdentityVerification) <!-- Create returns AlreadyExists with recovery-path message when the provider_user_id maps to a different account. -->
- [x] 3.3 Expose the verified person (`provider_user_id`) so ④/⑤ enforce per-person limits across accounts; document that per-person holds only where a sale requires verification (else per-account) <!-- IdentityVerificationService.Get() returns the IdentityVerification so ④/⑤ can read provider_user_id. Documented in the IdentityVerification entity (backend) and spec. -->

## 4. Backend — privacy retention

- [x] 4.1 利用目的 + acquisition notice + security controls; **store only `provider_user_id`** (基本4情報 only if a justified use case needs it); honor JPKI 目的外利用禁止 (checks logged/reported to J-LIS) <!-- Only provider_user_id stored. No 基本4情報, no serial, no 個人番号 fields. Raw signedResponse discarded immediately in Create. -->
- [x] 4.2 Deletion path (purpose-end / valid request), subject to lawful retention <!-- Delete usecase: removes the IdentityVerification record by user_id. -->

## 5. Frontend

- [ ] 5.1 Verification flow via **PocketSign Stamp** (PWA → backend `CreateSession` → open the PocketSign app via `redirectUrl` → card read+sign there → callback → backend `FinalizeSession`); show verification status <!-- PARTIAL 2026-09-02 (frontend PR #578 merged→dev): verification STATUS display + verify entry point DONE (Settings, calls IdentityVerificationService.Get()); the actual card-read is STUBBED behind IPocketSignVerifyClient (isAvailable=false → "coming soon"). NOTE: rework the stub to the Stamp app-handoff (redirect + callback), NOT an embedded SDK, when backend 2.1 lands. -->
- [ ] 5.1a Show the verification result on Settings (`components/infrastructure/fan/web/route/settings` "The identity verification result is shown on Settings"; design "The verification result is shown on Settings"): the callback route shows only `<circular-progress>` and hands the outcome to Settings in app state; Settings shows success as a snackbar and a failure as a reason kept in the identity verification row, hides 本人確認する for AlreadyExists and shows the support contact; remove the unused `settings.identity.comingSoon` key; verify component tests: Verification succeeds, Card read not finished, Card already used by another account, Verification unavailable, Callback opened again after success, No verification on this device, Retry clears the reason

- [x] 5.2 When a sale requires verification, prompt unverified fans to verify (JPKI) before entering; **clearly inform** them of the requirement (`components/infrastructure/fan/web/route/lottery-entry` "An unverified fan is asked to verify before entering") <!-- MVP = JPKI-only, no fallback option to offer here. DONE 2026-09-03 (frontend): the lottery entry route gained an optional `verificationRequired` route param; a requiring sale reads the fan's IdentityVerification on entry and parks unverified fans on a new `verify-required` step (informative panel + CTA routing to /settings verify entry point). Fails OPEN on a read error (backend #435 re-validates at entry → FAILED_PRECONDITION). +5 gate tests (21 green), make lint 0 errors. unify-ticket-sales rebuilds the route on `ticketTypeId`; the gate moves with it. -->
- [ ] 5.3 運転免許証 fallback flow (Verify CardInfo) where the event allows it; surface the weaker-dedupe/limit where applicable <!-- POST-MVP (2026-09-02): dropped from MVP scope; MVP is JPKI-only. Requires the separate pocketsign.cardinfo product. Revisit if real data on fans excluded for lacking a My Number Card + legal (0.2) warrant it. -->

<!-- POST-MVP (verified-name binding): retrieve 基本4情報 (氏名) via the JPKI 署名用証明書 + PocketSign ConsentService and bind the *verified* name to the covered ticket. MVP uses ④ self-declared name (see 6.2); this is a stronger optional enhancement, legal sufficiency = task 0.2. -->

## 6. Consumer wiring (④/⑤)

- [ ] 6.1 ④ lottery entry (`LotteryEntryUseCase.Start`): enforce per-**verified-person** limit (via `provider_user_id`) where a sale requires verification (extends the per-account limit); non-requiring sales stay per-account
- [ ] 6.2 ⑤ checkout and ticket issuance: gate on an Active IdentityVerification where required <!-- MVP: the covered ticket is bound by the User's self-declared full name and phone number; the IdentityVerification supplies the per-person dedupe (provider_user_id) but NOT a verified name in MVP. Binding a *verified* 基本4情報 name (署名用+Consent) is POST-MVP. -->
- [ ] 6.3 Per-sale requirement enforced at entry/checkout <!-- MVP: None vs JPKI-only (Verified-any behaves as JPKI-only since no fallback ships); the licence fallback is POST-MVP. -->

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend; wire ④/⑤ consumers <!-- spec v0.59.0/v0.60.0 released + BSR gen done; backend #427/#432/#435/#436 + frontend #578/#581/#582/#584 all MERGED TO MAIN. What remains = the prod DEPLOYMENT of that code (7.2–7.6), which the original tasks never captured. -->

<!-- DEPLOYMENT for prod sandbox E2E (added 2026-09-03). Verified GAP: prod runs NONE of this — backend prod pin is v1.51.0 which predates ④ #426 + all identity verification PRs, and cloud-provisioning has ZERO POCKET_SIGN_* config. Per the MVP decision (design "MVP scope & corrections"), prod points at the MOCK sandbox host verify.mock.p8n.app, so no 加盟契約 (0.1) is needed to run this. -->
- [ ] 7.2 **Backend prod Release + pin**: cut a backend Release vX.Y.Z from main (must include ④ #426 lottery + identity verification #427/#432/#435/#436) → bump-prod-pin rewrites `backend/api` `newTag` in `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`. Confirm the rendered prod image contains `identity_verification_handler.go` + `pocketsign.StampClient` + the lottery entry verification gate.
- [ ] 7.3 **cloud-provisioning: wire `POCKET_SIGN_*` for prod fan-api (mock/sandbox)**:
  - GSM secret `pocket-sign-token` in project `liverty-music-prod` holding the **sandbox `sk_mock_…` token** (declared in Pulumi `src/`, value injected out-of-band; sandbox creds are low-risk but still a Secret).
  - ESO: add `POCKET_SIGN_TOKEN → pocket-sign-token` to `k8s/namespaces/backend/base/fan-api/external-secret.yaml` (`fan-api-backend-secrets`).
  - `k8s/namespaces/backend/overlays/prod/fan-api/configmap.env` (+ dev overlay): `POCKET_SIGN_BASE_URL=https://verify.mock.p8n.app`, `POCKET_SIGN_TENANT_ID=<sandbox tenant>`, `POCKET_SIGN_CALLBACK_URL=https://liverty-music.app/verify/callback` (fan-web apex). NB `PocketSignConfig.Validate` requires all-or-none + https + `*.p8n.app` host (mock passes).
- [ ] 7.4 **DB migrations reach prod**: confirm `identity_verifications` (created by #427; named so by unify-ticket-sales), the sale's `verification_requirement` (#435; on the ticket sale since unify-ticket-sales), and the ④ lottery tables (#426) migration files are registered in the prod Atlas overlay (`k8s/atlas/**` + kustomization `configMapGenerator.files`) and applied by the `backend-migrations` AtlasMigration Application before fan-api rolls.
- [ ] 7.5 **Frontend prod pin**: ensure the frontend prod pin (bump-prod-pin `component:frontend`) includes #581 (`/verify/callback` route) + #584 (lottery entry verify-gate); confirm `https://liverty-music.app/verify/callback` is reachable (auth-required route) on the deployed prod bundle.
- [ ] 7.6 **Reachable prod entry point for the gate**: the lottery entry route is currently reachable only via its explicit path with the `:verificationRequired?` param (not nav-wired). For E2E, configure a real **verification-required lottery TicketSale** (organizer `TicketSaleService.SetVerificationRequirement` / `Create`) and provide a way to reach its entry screen (deep link or temporary nav entry). Coordinate with the lottery entry route, which is the production entry point.
- [ ] 7.7 **End-to-end on the live prod sandbox** (via Stamp + PocketSign app): verify (card + スマホJPKI) creates an Active IdentityVerification; second provider user ID → rejected; per-person limit spans two accounts of one person; **event-requires-verification prompts the fan before entering (5.2)**; no 個人番号/serial/基本4情報 stored (only provider_user_id); 現況確認 flags a revoked cert; deletion works. <!-- MVP JPKI-only: fallback/licence E2E dropped (POST-MVP). Confirm the Stamp Session flow (CreateSession redirectUrl → PocketSign app → FinalizeSession) and that identify_user resolves the provider's user ID (`User.userId`) (cert must be >90min old, else ERROR_REASON_IDENTIFY_USER_TOO_EARLY). CAVEAT (mock-in-prod): mock cards are NOT a genuine 公的個人認証, so "**same provider user ID after a simulated renewal**" (spike S1) may not be reproducible on the sandbox — defer that specific assertion to the POST-MVP prod-tenant cutover. -->
- [ ] 7.8 Sync delta specs to main specs and archive the change

## 8. Test hardening (follow-up — /opsx:explore coverage audit 2026-09-04)

<!-- Gap audit of the identity verification / lottery-verification modules (fe + be). Only MEANINGFUL,
verified gaps are listed. Dismissed as false-alarms/by-design (do NOT add): entity
RequiresVerification() "undefined" (it IS defined on the TicketSale entity, used +
tested via the lottery entry usecase tests); config look-alike-domain rejection (a non-p8n.app host IS
rejected-tested at config_test.go:583 — only suffix-trick hosts are untested and the
allowlist logic is provably safe); MemoryCache.Close double-close "deadlock" (the
Close_IsSafeToCallTwice test passes — not a real gap); verify-session non-SecurityError,
label-key one-liners, AbortSignal propagation, verifiedAt=epoch, extreme enum ints.
The recently-shipped fixes ARE covered (requireManualReturn/callbackWithSessionId pinned;
FE persisted-session-id path). -->

### TIER 1 — meaningful (entry points / real behavior)
- [x] 8.1 **FE `settings-route` has NO spec file at all** (`src/routes/settings/settings-route.spec.ts` does not exist). Add one covering: `verifyIdentity()` (the Stamp entry point — calls `identity.verify('jpki')`; handles `redirecting` / `notAuthenticated` outcomes), the verification-status display getters (`isIdentityVerified` / method / dedupe keys derived from `identity.status`), and `loadVerificationStatus()`'s error path (logs, does not crash the route). Mock `IIdentityVerificationService` in DI.
- [x] 8.2 **BE lottery entry verification gate — non-NotFound error from `GetByUserID`.** `lottery_uc_test` only ever returns NotFound (the `getByUserIDFn` stub hook exists but is never used to inject a failure). Add a case: a requiring sale + `GetByUserID` returns `Unavailable` (DB outage) → assert the error PROPAGATES (retryable) and is NOT collapsed to `FAILED_PRECONDITION` (which would misreport an outage as "not verified").
- [x] 8.3 **BE IdentityVerification repository integration test (real DB).** Currently only incidentally touched by `lottery_pipeline_integration_test.go`; the repo's own invariants are unexercised. Add an rdb integration test (per the codebase's integration-not-unit convention for repos): Create dedupe — a 2nd ACTIVE row with the same `provider_user_id` → `AlreadyExists` (the partial unique index on Active `provider_user_id`, the core 1-person-1-account lever); Create with a missing user → `FailedPrecondition` (FK); `GetByUserID`/`GetByProviderUserID` → `NotFound`; `UpdateStatus`/`Delete` on a missing id → `NotFound` (RowsAffected==0).
- [x] 8.4 **FE `identity-verification-service.verify()` — no partial navigation on error.** Assert that when `startVerify()` throws, `window.location.href` is NOT assigned (the browser must not navigate to a half-built URL). The success-path order (persist session id BEFORE navigating) is already covered.

### TIER 2 — defensive / cheap (pin behavior, prevent regressions)
- [x] 8.5 **BE `verify_client.CompleteVerify` — nonce restore semantics.** Pin that the nonce is re-stored ONLY on `FailedPrecondition` (session-not-yet-completed, retryable) and is NOT restored on other error codes (e.g. `Unavailable`/`Internal`) — so a genuinely consumed nonce cannot be replayed.
- [x] 8.6 **BE `verify_client.StartVerify` — empty response guards.** Cover CreateSession returning an empty `id` or empty `redirectUrl` → `Internal` (currently only valid responses are tested).
- [x] 8.7 **FE lottery entry route gate — negative + fail-open paths.** `verificationRequired='false'` (and other non-`'true'` strings) parsed as false → no `IdentityVerificationService.Get()` call, no gate; and on a status-load error assert `step` stays `'count'` (fails open, NOT `'verify-required'`).
- [x] 8.8 **FE `verify-callback` `connectErrorKey` — unmapped ConnectError code.** Add a case for a ConnectError whose code is not in the switch (e.g. `Code.Internal`) → falls through to the generic key (distinct from the non-ConnectError generic case already tested).
- [x] 8.9 **FE `identity-verification-mapper` — enum default fall-throughs.** Ensure each proto→entity enum map (method / dedupe strength / status; level until unify-ticket-sales removed it) degrades an `UNSPECIFIED`/unknown value to its safe default rather than a wrong lane.
