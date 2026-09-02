<!-- MVP SCOPE (2026-09-02, see design.md "MVP scope & corrections"):
     - Client path = PocketSign **Stamp** (stamp.v1.SessionService: CreateSession →
       PocketSign **app** via redirectUrl → FinalizeSession), riding on Verify.
       NOT an embedded SDK, NOT the デジタル認証アプリ path.
     - MVP = **JPKI-only**. 運転免許証 (Verify CardInfo) fallback = POST-MVP (task 5.3).
     - MVP stores **only User.id**; verified-name (基本4情報 via 署名用証明書 + Consent)
       = POST-MVP. Covered-ticket 本人確認 in MVP = ④ self-declared name+contact. -->

## 0. Prerequisites (long-lead — start in parallel, non-code)

- [ ] 0.1 **Onboard Pocket Sign (PocketSign Verify)**: 加盟契約 (ride their 認定PF status — no own 主務大臣認定), register on PocketSign Platform, ¥300k init + per-verify fees, use the free sandbox for PoC (~2-3mo Verify integration lead time)
- [ ] 0.2 Legal/privacy review: JPKI-only (outside 番号法, never 個人番号/serial), 個情法 利用目的/最小保持(User.idのみ)/削除, Pocket Sign 利用規約 目的外利用 clauses, no 犯収法 取引時確認, data residency (越境), fallback fairness
- [ ] 0.3 Resolve Pocket Sign spikes S1-S6 (see design Open Questions): スマホJPKI cert support + same User.id; data minimization (User.id without PII); 目的外利用 limits; 越境; licence-path dedupe; proto field mapping <!-- PARTIAL 2026-09-02 (see pocket-sign-integration-notes.md, from the public pocketsign.verify.v2 BSR schema): S6 RESOLVED (User.userId→pocket_sign_user_id opaque string; JPKICard/JPKIMobile Auth/Signature=our JPKI; Verification.isNewUser=dedupe signal; serialNumberMac=MAC not raw serial; CheckUserStatus/CertificateStatus.checkPurpose=現況確認+J-LIS). S1/S2/S5 strong schema evidence (still confirm userId across renewal on a live account; licence is a separate JPKI-less product=WEAK dedupe confirmed). S3/S4 (目的外利用 contract terms / 越境) remain for the 0.2 legal review — not answerable from the schema. -->


## 1. Proto / entity (specification → BSR)

- [x] 1.1 Define `VerifiedIdentity` (account_ref, method enum JPKI/DRIVER_LICENCE, `pocket_sign_user_id` = tenant-scoped UUID person key, dedupe_strength enum STRONG/WEAK, verified_at, status) — type-safe IDs, protovalidate, **no 基本4情報 field by default**
- [x] 1.2 Add account **verification level** (UNVERIFIED / IDENTITY_VERIFIED) surfaced to ④/⑤
- [x] 1.3 Add a per-event/phase **verification requirement** (none / verified-any / JPKI-only) settable by organizer/admin
- [x] 1.4 RPCs: StartVerify / CompleteVerify (challenge–response via Pocket Sign), 現況確認 ReCheck, GetMyVerificationStatus; admin/organizer SetEventVerificationRequirement
- [x] 1.5 protovalidate; buf lint/breaking; merge PR → Release → BSR gen <!-- DONE 2026-09-02: spec PR #893 merged, Release v0.59.0 cut, buf-release.yml BSR gen success. -->
<!-- NOTE: SetEventVerificationRequirement (1.4) realized as SetPhaseVerificationRequirement on the organizer LotteryService, since the first-party apply gate is the LotterySalesPhase (there is no separate first-party Event-level sale config). The requirement is also settable at ConfigureLotteryPhase. -->
<!-- Proto surface added: entity/v1/verified_identity.proto (VerifiedIdentityId, PocketSignUserId, VerificationMethod, DedupeStrength, VerificationStatus, VerificationRequirement enums + VerifiedIdentity); entity/v1/user.proto (VerificationLevel enum + User.verification_level field 8, OUTPUT_ONLY); entity/v1/lottery_application.proto (LotterySalesPhase.verification_requirement field 8); rpc/identity/v1/identity_verification_service.proto (StartVerify/CompleteVerify/ReCheck/GetMyVerificationStatus); rpc/organizer/v1/lottery_service.proto (SetPhaseVerificationRequirement + ConfigureLotteryPhaseRequest.verification_requirement). -->
<!-- Design note: PocketSignUserId validation kept a bounded opaque string (not strict UUID) pending spike S6 (proto field mapping vs pocketsign.verify.v2). -->
<!-- Cycle avoided: VerificationLevel defined in user.proto (not verified_identity.proto) so user.proto need not import verified_identity.proto (which imports user.proto for UserId). -->


## 2. Backend — Pocket Sign verification

- [ ] 2.1 Integrate **PocketSign Stamp** (`stamp.v1.SessionService`: `CreateSession` → PocketSign app via `redirectUrl` → `FinalizeSession`, riding on Verify) to verify the fan and obtain the `User.id`; accept physical card AND スマホJPKI; **delete the raw certificate/response immediately** after the call <!-- REOPENED 2026-09-02: the shipped VerifyClient (backend #428/#429) targets verify.v2 VerifyForDigitalIdentificationApp (デジタル認証アプリ path) = WRONG for our PWA plan; it is inert (config-gated) but MUST be rewritten to the Stamp SessionService path. The hand-rolled Nonce + `data` approach is dissolved by Stamp (the Session manages the challenge/callback). Interim scaffolding retained: PocketSignVerifier interface + StubVerifier (UNAVAILABLE), config gate, dedupe/privacy usecase (2.2-4.2) are path-agnostic and stay. -->
- [x] 2.2 On success: create `VerifiedIdentity` with `pocket_sign_user_id`, set account verification_level=IDENTITY_VERIFIED; never store the 個人番号 or raw serial <!-- CompleteVerify usecase: only PocketSignUserID stored. VerifiedIdentityLevel derived from status. -->
- [x] 2.3 **現況確認** periodic re-check (revocation / 基本4情報 change / expiry) → flag for re-verification (not hard-lock) <!-- ReCheck usecase: flags NEEDS_REVERIFICATION, does not hard-lock. -->

## 3. Backend — dedupe + per-person signal

- [x] 3.1 Enforce **≤1 active IDENTITY_VERIFIED account per `pocket_sign_user_id`** (UNIQUE); rely on User.id stability across renewal (no 基本4情報 re-link needed — S1) <!-- Partial unique index uq_active_pocket_sign_user_id on (pocket_sign_user_id WHERE status=1) in migration 20260902000000. -->
- [x] 3.2 Second-User.id-match handling: reject with a clear message + account-recovery/support path (no silent second identity) <!-- CompleteVerify returns AlreadyExists with recovery-path message when pocket_sign_user_id maps to a different account. -->
- [x] 3.3 Expose the verified person (`User.id`) so ④/⑤ enforce per-person limits across accounts; document that per-person holds only where an event requires verification (else per-account) <!-- GetMyVerificationStatus returns (level, vi) so ④/⑤ can read pocket_sign_user_id. Documented in entity/verified_identity.go and spec. -->

## 4. Backend — privacy retention

- [x] 4.1 利用目的 + acquisition notice + security controls; **store only `User.id`** (基本4情報 only if a justified use case needs it); honor JPKI 目的外利用禁止 (checks logged/reported to J-LIS) <!-- Only pocket_sign_user_id stored. No 基本4情報, no serial, no 個人番号 fields. Raw signedResponse discarded immediately in CompleteVerify. -->
- [x] 4.2 Deletion path (purpose-end / valid request), subject to lawful retention <!-- Delete usecase: removes the VerifiedIdentity record by user_id. -->

## 5. Frontend

- [ ] 5.1 Verification flow via **PocketSign Stamp** (PWA → backend `CreateSession` → open the PocketSign app via `redirectUrl` → card read+sign there → callback → backend `FinalizeSession`); show verification status <!-- PARTIAL 2026-09-02 (frontend PR #578 merged→dev): verification STATUS display + verify entry point DONE (Settings, calls GetMyVerificationStatus); the actual card-read is STUBBED behind IPocketSignVerifyClient (isAvailable=false → "coming soon"). NOTE: rework the stub to the Stamp app-handoff (redirect + callback), NOT an embedded SDK, when backend 2.1 lands. -->

- [ ] 5.2 When an event requires verification, prompt UNVERIFIED fans to verify (JPKI) before applying; **clearly inform** them of the requirement <!-- MVP = JPKI-only, no fallback option to offer here. -->
- [ ] 5.3 運転免許証 fallback flow (Verify CardInfo) where the event allows it; surface the weaker-dedupe/limit where applicable <!-- POST-MVP (2026-09-02): dropped from MVP scope; MVP is JPKI-only. Requires the separate pocketsign.cardinfo product. Revisit if real card-holder-exclusion data + legal (0.2) warrant it. -->

<!-- POST-MVP (verified-name binding): retrieve 基本4情報 (氏名) via the JPKI 署名用証明書 + PocketSign ConsentService and bind the *verified* name to the covered ticket. MVP uses ④ self-declared name (see 6.2); this is a stronger optional enhancement, legal sufficiency = task 0.2. -->

## 6. Consumer wiring (④/⑤)

- [ ] 6.1 ④ lottery-application: enforce per-**verified-person** limit (via `User.id`) where an event requires verification (extends "1 account / 1 application"); non-requiring events stay per-account
- [ ] 6.2 ⑤ ticket-purchase-and-issuance: gate on verification_level where required <!-- MVP: the covered ticket is bound by ④'s self-declared name+contact (ApplicantIdentity); the verified identity supplies the per-person dedupe (User.id) but NOT a verified name in MVP. Binding a *verified* 基本4情報 name (署名用+Consent) is POST-MVP. -->
- [ ] 6.3 Per-event requirement enforced at apply/purchase <!-- MVP: none vs JPKI-only (VERIFIED_ANY behaves as JPKI-only since no fallback ships); the licence fallback is POST-MVP. -->

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend; wire ④/⑤ consumers
- [ ] 7.2 End-to-end (Pocket Sign sandbox, via Stamp + PocketSign app): verify (card + スマホJPKI) upgrades account; **same User.id after a simulated renewal**; second User.id → rejected; per-person limit spans two accounts of one person; event-requires-verification prompts (JPKI-only); no 個人番号/serial/基本4情報 stored (only User.id); 現況確認 flags a revoked cert; deletion works <!-- MVP JPKI-only: fallback/licence E2E dropped (POST-MVP). -->
<!-- Also confirm on the live sandbox: the Stamp Session flow (CreateSession redirectUrl → PocketSign app → FinalizeSession), and that identify_user resolves the User.id (cert must be >90min old, else ERROR_REASON_IDENTIFY_USER_TOO_EARLY). -->
- [ ] 7.3 Sync delta specs to main specs and archive the change
