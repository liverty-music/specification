# Pocket Sign Verify integration notes (spike findings + handoff)

Research notes for the `identity-ekyc-jpki` change. These **de-risk the vendor
integration ahead of onboarding** (Section 0) by grounding the design against the
**publicly published Pocket Sign schema** on the BSR. They do **not** replace the
Section 0 spikes that genuinely need a signed contract / sandbox access — each
finding below is marked with its confidence and what still needs vendor
confirmation.

## Source inspected

- BSR module: **`buf.build/gen/go/pocketsign/apis`**, package **`pocketsign.verify.v2`**
  (public; inspected commit `20260826021924-0ff29b2b0335`, protobuf-go build
  `v1.36.12`). This is the same `pocketsign.verify.v2` surface named in spike S6.
- Method of inspection: `go doc` + reading the generated `*.pb.go` field tags for
  `User`, `Verification`, `Certificate`, `CertificateContent`, `CertificateStatus`,
  `Consent`, and the `*UserStatus` / `*CertificateStatus` request/response messages.

## S6 — proto field mapping (**RESOLVED** against the published schema)

Our entities map onto `pocketsign.verify.v2` as follows:

| Our type / field (`liverty_music.entity.v1`) | Pocket Sign `pocketsign.verify.v2` source | Notes |
|---|---|---|
| `PocketSignUserId.value` (opaque string) | `User.userId` (string) | The tenant-scoped person key. It is a **string, not necessarily a UUID** — so keeping `PocketSignUserId` a bounded opaque string (not `string.uuid`) was the correct call. |
| `VerifiedIdentity.method` = JPKI | `CertificateContent` oneof: `JPKICardUserAuthentication` / `JPKICardDigitalSignature` / `JPKIMobileUserAuthentication` / `JPKIMobileDigitalSignature` + `Certificate.type` (`certificateType`) | Both **physical card** (`JPKICard*`) and **スマホJPKI** (`JPKIMobile*`) are first-class, each in 利用者証明用 (`*UserAuthentication`) and 署名用 (`*DigitalSignature`) variants. |
| (dedupe decision: new vs returning) | `Verification.isNewUser` (bool) | Pocket Sign itself tells us whether this `userId` is new to our tenant — a direct signal for the "second account for the same person" check (tasks 3.1/3.2). |
| (verification handle) | `Verification.verificationId`, `Verification.userIds`, `Verification.signCertificateJwe`, `Verification.hashAlgorithm`, `Verification.identifyUser` | The challenge/response artifacts. `signCertificateJwe` is the signed material we validate then **discard** (task 2.1 / privacy). |
| (never stored) | `User.serialNumberMac` | Pocket Sign returns a **MAC-hashed** serial, **not the raw 発行番号** — reinforces that we never receive or store the raw serial (task 4.1). Do **not** persist even this MAC unless a justified use case appears. |
| `VerificationStatus` (現況確認) | `CheckUserStatus` / `BatchCheckUserStatus`; `CheckCertificateStatus` / `CheckCertificateStatusByContent` / `BatchCheckCertificateStatus`; `CertificateStatus.{status, crlReason, checkMethod, checkPurpose}` | The 現況確認 / 失効確認 surface for task 2.3 (ReCheck). `CertificateStatus.checkPurpose` is the **J-LIS-logged `check_purpose`** our privacy requirement (4.1) calls out. |
| (consent step) | `CreateConsentForDigitalIdentificationApp*`, `Consent`, `Consent.Preference` | The デジタル認証アプリ consent flow that precedes a verification. |

**Implication for our proto:** no change needed. `PocketSignUserId` as an opaque
string is correct; `VerificationMethod` (JPKI vs DRIVER_LICENCE) sits one level
above Pocket Sign's card/mobile + auth/signature distinction (all four JPKI cert
contents collapse to our single `JPKI` method).

## S1 — same `userId` across cert types / renewal / スマホ (**strong evidence; confirm on live**)

- The schema models a single `User.userId` that carries multiple certificates
  (`latestCertificate`, `certificateStates`, both JPKICard and JPKIMobile contents),
  and `Verification.isNewUser` distinguishes new vs returning — i.e. the design
  intent is clearly **one stable person key across cert type and card/mobile**.
- **Still needs a live check** that `userId` is byte-identical after a card
  **renewal / re-issue** (not just across cert type) on a real account — the schema
  strongly implies it but does not prove the renewal case.

## S2 — data minimization: `userId` without 基本4情報 (**supported**)

- `User` exposes `userId` + `serialNumberMac` + certificate **metadata** without
  requiring `CertificateContent` (which is where 基本4情報 lives). So we can dedupe
  on `userId` **without receiving PII**. Our "store only `User.id`" design is
  achievable. Confirm during integration that the verify call can be configured to
  return the assertion + `userId` while omitting `certificateContent`.

## S5 — licence-path dedupe (**consistent with the WEAK-dedupe design**)

- `pocketsign.verify.v2` is **JPKI-only** — no driver-licence / CardInfo / 在留カード
  types appear anywhere in the module. The 運転免許証 fallback (design's "Verify
  CardInfo") is therefore a **separate Pocket Sign product/surface** that does not
  yield a `verify.v2` `userId`. This confirms the honest-caveat design: the licence
  path has **no equivalent stable per-person key** → `dedupe_strength = WEAK`.

## S3 / S4 — 目的外利用 limits / 越境 (**still vendor/legal, not answerable from the schema**)

- `CertificateStatus.checkPurpose` shows purpose is a first-class, logged concept
  (aligns with 目的外利用禁止 + J-LIS reporting), but the **contractual** limits (S3)
  and **data-residency / 越境** (S4) are answerable only from the Pocket Sign 利用規約
  and their infra docs — carry into the Section 0.2 legal review.

## Integration seams (turnkey for whoever completes Section 0)

When the Pocket Sign contract + sandbox land, the **only** code that changes is the
two stubs — everything around them (dedupe, privacy, RPC surface, UI) is done:

- **Backend** — replace `internal/infrastructure/pocketsign/stub_verifier.go`
  (`StubVerifier`, currently returns `UNAVAILABLE`) with a real client implementing
  `usecase.PocketSignVerifier` (`IssueChallenge` / `ValidateResponse` / `Recheck`).
  Wire it in `internal/di/provider.go` (the `TODO: replace StubVerifier ...` line).
  Map: `ValidateResponse` → the verify RPC returning `Verification` (read `userIds`
  → our `pocket_sign_user_id`, `isNewUser`, cert content type → our `method`);
  `Recheck` → `CheckUserStatus` / `CheckCertificateStatus`. Add the
  `buf.build/gen/go/pocketsign/apis/...` dependency at that point.
- **Frontend** — replace `src/adapter/pocket-sign/pocket-sign-verify-client.ts`
  (`StubPocketSignVerifyClient`, `isAvailable=false`) with the real Pocket Sign
  Verify **SDK** card-read (physical NFC + スマホJPKI). The `verify()` orchestration,
  the observable status, and the Settings UI already branch on `isAvailable`.
- Then build the deferred **5.2** (apply-time "requires verification" prompt — needs
  the lottery-application apply flow to exist) and **5.3** (運転免許証 fallback UI).

## Status of the shipped slice (2026-09-02)

- specification v0.59.0 (merged, BSR-generated), backend #427 (merged → dev),
  frontend #578 (merged → dev). All three are at **dev**; **prod needs a separate
  backend/frontend Release**. The feature is inert until Section 0 completes (both
  ends return "unavailable" / "coming soon").
