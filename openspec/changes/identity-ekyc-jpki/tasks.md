## 0. Prerequisites (long-lead — start in parallel, non-code)

- [ ] 0.1 **Onboard Pocket Sign (PocketSign Verify)**: 加盟契約 (ride their 認定PF status — no own 主務大臣認定), register on PocketSign Platform, ¥300k init + per-verify fees, use the free sandbox for PoC (~2-3mo Verify integration lead time)
- [ ] 0.2 Legal/privacy review: JPKI-only (outside 番号法, never 個人番号/serial), 個情法 利用目的/最小保持(User.idのみ)/削除, Pocket Sign 利用規約 目的外利用 clauses, no 犯収法 取引時確認, data residency (越境), fallback fairness
- [ ] 0.3 Resolve Pocket Sign spikes S1-S6 (see design Open Questions): スマホJPKI cert support + same User.id; data minimization (User.id without PII); 目的外利用 limits; 越境; licence-path dedupe; proto field mapping

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Define `VerifiedIdentity` (account_ref, method enum JPKI/DRIVER_LICENCE, `pocket_sign_user_id` = tenant-scoped UUID person key, dedupe_strength enum STRONG/WEAK, verified_at, status) — type-safe IDs, protovalidate, **no 基本4情報 field by default**
- [ ] 1.2 Add account **verification level** (UNVERIFIED / IDENTITY_VERIFIED) surfaced to ④/⑤
- [ ] 1.3 Add a per-event/phase **verification requirement** (none / verified-any / JPKI-only) settable by organizer/admin
- [ ] 1.4 RPCs: StartVerify / CompleteVerify (challenge–response via Pocket Sign), 現況確認 ReCheck, GetMyVerificationStatus; admin/organizer SetEventVerificationRequirement
- [ ] 1.5 protovalidate; buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — Pocket Sign verification

- [ ] 2.1 Integrate the **Verify SDK (app) + Verify API (backend)** challenge–response: issue Nonce → validate signed response → accept physical card AND スマホJPKI; **delete the raw certificate/response immediately** after the API call
- [ ] 2.2 On success: create `VerifiedIdentity` with `pocket_sign_user_id`, set account verification_level=IDENTITY_VERIFIED; never store the 個人番号 or raw serial
- [ ] 2.3 **現況確認** periodic re-check (revocation / 基本4情報 change / expiry) → flag for re-verification (not hard-lock)

## 3. Backend — dedupe + per-person signal

- [ ] 3.1 Enforce **≤1 active IDENTITY_VERIFIED account per `pocket_sign_user_id`** (UNIQUE); rely on User.id stability across renewal (no 基本4情報 re-link needed — S1)
- [ ] 3.2 Second-User.id-match handling: reject with a clear message + account-recovery/support path (no silent second identity)
- [ ] 3.3 Expose the verified person (`User.id`) so ④/⑤ enforce per-person limits across accounts; document that per-person holds only where an event requires verification (else per-account)

## 4. Backend — privacy retention

- [ ] 4.1 利用目的 + acquisition notice + security controls; **store only `User.id`** (基本4情報 only if a justified use case needs it); honor JPKI 目的外利用禁止 (checks logged/reported to J-LIS)
- [ ] 4.2 Deletion path (purpose-end / valid request), subject to lawful retention

## 5. Frontend

- [ ] 5.1 Verification flow via the Pocket Sign Verify SDK (physical card NFC + スマホJPKI) in our app; show verification status
- [ ] 5.2 When an event requires verification, prompt UNVERIFIED fans to verify (or use the allowed fallback) before applying; **clearly inform** them of the requirement
- [ ] 5.3 運転免許証 fallback flow (Verify CardInfo) where the event allows it; surface the weaker-dedupe/limit where applicable

## 6. Consumer wiring (④/⑤)

- [ ] 6.1 ④ lottery-application: enforce per-**verified-person** limit (via `User.id`) where an event requires verification (extends "1 account / 1 application"); non-requiring events stay per-account
- [ ] 6.2 ⑤ ticket-purchase-and-issuance: gate on verification_level where required; where required, the **verified identity binds the covered ticket** (④'s 本人確認 name consistent with it)
- [ ] 6.3 Per-event requirement (none / verified-any / JPKI-only) enforced at apply/purchase, with the fallback honored

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend; wire ④/⑤ consumers
- [ ] 7.2 End-to-end (Pocket Sign sandbox): verify (card + スマホJPKI) upgrades account; **same User.id after a simulated renewal**; second User.id → rejected; per-person limit spans two accounts of one person; event-requires-verification prompts + fallback; JPKI-only event excludes licence fallback; no 個人番号/serial stored; 現況確認 flags a revoked cert; deletion works
- [ ] 7.3 Sync delta specs to main specs and archive the change
