## Context

See [proposal.md](./proposal.md) for motivation. This is the **heavy anti-scalp
lever** of the tiered model (roadmap Guiding Decision): bind 1 account = 1 verified
person so bulk scalping is structurally impossible. Grounded in the session's JPKI
research and the merged roadmap `identity-ekyc-jpki` backlog entry. It attaches to
the existing `identity-management` Zitadel account and feeds ④/⑤'s per-person
limits. Authored ahead of ④/⑤ implementation; the ④/⑤ enforcement hooks are folded
in when this lands.

## Goals / Non-Goals

**Goals:**
- Kill bulk/industrial scalping via a legally clean **JPKI (マイナンバーカード)** account
  verification (**vendor: Pocket Sign / PocketSign Verify**), exposing a
  **per-person** limit signal to ④/⑤.
- Stay **outside 番号法** (JPKI only, never 個人番号) and **proportionate** (ticketing
  is not a 犯収法 obligor → no 取引時確認).
- Privacy by design: store **only Pocket Sign's `User.id`**, delete raw cert data,
  deletion path.

**Non-Goals:**
- **顔認証 entry** — a separate per-event high-assurance tier (`face-auth-entry`);
  this change is account-level identity, not gate biometrics.
- **犯収法 取引時確認** — not required (ticketing not a 特定事業者); do not build the
  heavy AML flow.
- **Mandatory-for-all verification** — it is a lane; ④/⑤/events opt in.
- Running our own JPKI 署名検証者 認定 — ride on Pocket Sign's 認定 (see decision).
- 券面事項 read (マイナンバー / 顔写真 / card-face images) — never requested (番号法).

## MVP scope & corrections (2026-09-02)

These decisions were refined after grounding the design against the public Pocket
Sign schema and product line. Where they conflict with an older bullet below, **these
win**.

- **Client path = PocketSign Stamp + the user-installed PocketSign app (NOT an
  embedded SDK, NOT the デジタル認証アプリ).** Our client is a **PWA**, so it uses
  **PocketSign Stamp** (`pocketsign.stamp.v1.SessionService`): the backend
  `CreateSession` → the fan opens the returned `redirectUrl` in the **PocketSign
  app** (installed separately), reads their card and signs there → returns to the
  PWA → the backend `FinalizeSession` gets the result. Stamp **rides on PocketSign
  Verify** as its backend, so the person key (`User.id`), dedupe, and 現況確認 come
  from Verify. This replaces the earlier "Verify **SDK** embedded in our app +
  our own Nonce challenge–response" framing (that fits a native app we are not
  building). The government **デジタル認証アプリ** (`VerifyForDigitalIdentificationApp`)
  is a **separate, unused path** — do not treat it as ours.
- **MVP = JPKI-only; the 運転免許証 (Verify CardInfo) fallback is POST-MVP.** In the
  MVP a verification-required event admits only JPKI (card-holders). The 任意/平等
  fairness concern of excluding non-card-holders is a **legal-review (task 0.2)**
  item and is already the sanctioned per-event "JPKI-only" option below. The proto
  keeps `DRIVER_LICENCE`/`WEAK`/`VERIFIED_ANY` for forward-compat, but no
  `pocketsign.cardinfo` integration and no fallback UI ship in the MVP.
- **MVP stores only `User.id`; verified-name (基本4情報) binding is POST-MVP.** The
  MVP retains only the dedupe key and does **not** retrieve/verify 基本4情報 (氏名).
  The covered-ticket 本人確認 in the MVP is ④ lottery-application's **self-declared
  name+contact** (`ApplicantIdentity`), which already satisfies the 特定興行入場券
  requirement — **チケット不正転売禁止法 does not mandate JPKI-level name verification**
  (entry 本人確認 is largely 努力義務). Retrieving 基本4情報 via the JPKI **署名用証明書 +
  PocketSign ConsentService** to bind a *verified* name is a stronger post-MVP
  enhancement; its exact legal sufficiency is a task 0.2 item.

## Decisions

- **Vendor = Pocket Sign (PocketSign Verify); MVP client path = PocketSign Stamp +
  the PocketSign app (see the MVP-scope section above, which supersedes the
  embedded-SDK framing).** The backend calls `pocketsign.stamp.v1.SessionService`
  (CreateSession → redirect to the PocketSign app → FinalizeSession); Stamp rides on
  the PocketSign Verify API, which validates certificate authenticity and returns
  the person key. Raw certificate/response is **deleted promptly** after the call.
  Pocket Sign is a 公的個人認証法 **主務大臣認定プラットフォーム事業者** (since 2023), so we
  integrate as a **加盟事業者 with NO own 主務大臣認定**. Envs: mock → test → prod.
  Rejected: self-認定 (overkill); running our own native app just to embed the Verify
  SDK (Stamp lets a PWA delegate to the PocketSign app instead).
- **Never the 個人番号 → outside 番号法.** Use the 利用者証明用 (auth, PIN4) and/or
  署名用 (signature, PIN 6-16, carries 基本4情報) 電子証明書. The 個人番号 is heavily
  restricted (番号法, 法定事務限定) — collecting it would pull us into that regime, so
  it is **never received or stored**.
- **"Outside 番号法" ≠ light 個情法 footprint.** The provider identifier + any 基本4情報
  retained are full personal data (個情法 §17/§21/§23) → 利用目的 specification, minimal
  retention, deletion. Plus the **JPKI-framework 目的外利用禁止 + 失効情報確認** duties
  flow down from the 認定PF事業者 to us as an SP事業者.
- **Dedupe key = Pocket Sign `User.id` (tenant-scoped UUID).** Pocket Sign returns
  a **tenant-scoped** user id (same person → same id within our tenant; different
  across tenants = a service-scoped pairwise id), and crucially returns the **same
  `User.id` across card renewal, re-issue, cert generation, and cert type**. We
  store **only this UUID** (never the raw 発行番号/serial — avoiding the restricted
  serial-DB 目的外利用 concern entirely, and never the 個人番号). Enforce ≤1 active
  `IDENTITY_VERIFIED` account per `User.id`; a second maps to reject/recovery.
  **Limit:** tenant-scoped → **no cross-platform scalper detection** (accepted).
- **Re-issue/renewal continuity is solved by the vendor.** Because Pocket Sign's
  `User.id` is **stable across renewal/re-issue**, we do **not** need 基本4情報
  re-link logic — the earlier serial-rotation hole disappears. (Spike S1: confirm
  `User.id` is identical across both cert types + スマホJPKI on the live account.)
- **現況確認 for freshness.** Use Pocket Sign's 現況確認 (liveness) to detect
  revocation / 基本4情報 change / expiry and prompt re-verification (not a hard lock).
- **Per-person limit signal + honest mixed-population scope.** Where an event
  **requires** verification, ④'s "1 account / 1 application" is evaluated **per
  verified person** across accounts (via `User.id`). Where an event does **not**
  require verification, only **per-account** limits apply and bulk-account resistance
  is **not** guaranteed — stated explicitly, not marketed as per-person.
- **Lane + per-event requirement + fallback (with an honest dedupe caveat).**
  Default `UNVERIFIED`; events opt into requiring verification. Non-card fallback =
  Pocket Sign **運転免許証 IC (Verify CardInfo)**, **substantively non-disadvantaging**
  (equivalent odds — マイナンバーカード is 任意, so a materially-worse fallback = de-facto
  compulsion / 平等 concern). **But the licence path yields identity proofing WITHOUT
  an equivalent stable per-person dedupe key** (only a document number that can
  change), so a licence-fallback account has a **weaker 1-person guarantee**. Per
  event the organizer chooses: (a) allow the licence fallback (flag/limit those
  accounts), or (b) for the highest-demand shows **require JPKI** (no weaker
  fallback), accepting card-holder exclusion as a deliberate trade-off. Rejected:
  an attestation-only fallback with no dedupe (unlimited-account escape hatch).
- **Relationship to ④ 本人確認.** Where verification is required, the **verified
  identity is authoritative** for the covered ticket; ④'s apply-time 本人確認 name must
  be **consistent with the verified 基本4情報** (no conflicting name bound). Where not
  required, ④'s 本人確認 alone binds the covered ticket. Resolves the double-identity
  ambiguity (④'s spec is unchanged for non-requiring events).
- **Relationship to ④ 本人確認.** Where verification is required, the **verified
  identity is authoritative** for the covered ticket; ④'s apply-time 本人確認 name must
  be **consistent with the verified 基本4情報** (no conflicting name bound). Where not
  required, ④'s 本人確認 alone binds the covered ticket. Resolves the double-identity
  ambiguity (④'s spec is unchanged for non-requiring events).
- **Phone-embedded credential.** Support both the **physical card (NFC+PIN)** and the
  **スマホ用電子証明書** (Android 令和5年5月; iPhone 2025) — better completion, mitigates
  the ~81%-penetration/drop-off concern.
- **Anti-resale scope (corrected overclaim).** Account eKYC kills
  one-person-many-accounts, but does **NOT** stop a verified buyer reselling/lending
  a ticket — the PoC's zero-resale needed eKYC **+ gate 顔認証**. That entry layer is
  the separate `face-auth-entry` tier; do not claim eKYC alone delivers zero resale.
- **Entity `VerifiedIdentity`** — `account_ref`, `method` (JPKI / driver-licence),
  `pocket_sign_user_id` (the tenant-scoped UUID = the person key), a
  `dedupe_strength` flag (STRONG for JPKI / WEAK for licence), `verified_at`,
  `status`; plus account-level `verification_level` (`UNVERIFIED` /
  `IDENTITY_VERIFIED`). Store **no** 基本4情報 by default (only if a justified use
  case needs it). Follow proto conventions (type-safe IDs, enum, protovalidate).

## Risks / Trade-offs

- **Privacy/regulatory sensitivity is high.** マイナンバーカード handling is press- and
  PPC-sensitive. *→* Never touch 個人番号; store only `User.id`; delete raw cert data;
  counsel review of the Pocket Sign 利用規約 + data flow before launch.
- **Depends on Pocket Sign** (加盟契約, API/SDK, ¥300k init + per-verify fees, ~2-3mo
  Verify integration; free sandbox for PoC). *→* Long-lead: onboard early. Keep the
  provider behind our RPC in case of a future swap (accepting a swap re-issues the
  tenant-scoped `User.id`, i.e. a migration).
- **Licence fallback has weaker dedupe** (no stable per-person key). *→* Flag/limit
  licence-fallback accounts; let high-demand events require JPKI-only.
- **Authored ahead of ④/⑤ enforcement.** *→* This change owns verification + the
  per-person signal (`User.id` + verification_level); ④/⑤ consume it. Fold the
  enforcement hooks into ④/⑤ when this lands; keep the signal a stable contract.

## Migration Plan

New capability on the existing Zitadel account. Sequence: **onboard Pocket Sign**
(加盟契約, sandbox) → proto (`VerifiedIdentity` with `pocket_sign_user_id`,
verification level, per-event requirement flag, verify + 現況確認 RPCs) → BSR →
backend (Verify challenge–response integration, `User.id` dedupe uniqueness,
現況確認 re-check, per-person signal, delete-raw-cert + retention/deletion) →
frontend (Verify SDK card/スマホJPKI flow + status) → wire ④/⑤ enforcement +
per-event requirement. No 個人番号, no raw serial anywhere.

## Open Questions / Spikes (Pocket Sign docs unclear)

- **S1 — スマホJPKI cert support**: reconcile a stale `supported-certificate` doc page
  vs current "supported"; confirm both cert types + スマホJPKI return the same `User.id`.
- **S2 — data minimization**: confirm we can get `User.id` + a verification assertion
  **without** being forced to receive/persist 基本4情報.
- **S3 — 目的外利用 / purpose limits** in the Pocket Sign 利用規約 + J-LIS guidelines for
  anti-scalp identity use.
- **S4 — data residency (越境)**: confirm all processing is domestic.
- **S5 — licence-path dedupe**: confirm whether Verify CardInfo yields ANY stable
  per-person key; if not, lock the weaker-guarantee handling.
- **S6 — proto field mapping**: pull `pocketsign.verify.v2` field names from BSR to
  lock `User.id`/attribute mapping at implementation.
