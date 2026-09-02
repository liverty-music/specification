## Purpose

Identity eKYC binds an account to a **verified real person** — via マイナンバーカード
公的個人認証 (JPKI) using **Pocket Sign (PocketSign Verify)** — so bulk/industrial
scalping (many accounts per person, bot armies) is structurally resisted. It is a
high-assurance **lane**, not a universal mandate, and it feeds the platform's
per-person application/purchase limits. It is a **business anti-scalp measure that
complements — it is not required by — チケット不正転売禁止法**, and it alone does not
stop a verified buyer reselling/lending a ticket (that is the separate per-event
`face-auth-entry` tier).

## ADDED Requirements

### Requirement: JPKI account verification via Pocket Sign Verify

The system SHALL let an authenticated fan verify their identity with their
**マイナンバーカード 公的個人認証 (JPKI)** using **Pocket Sign Stamp** (the fan reads and
signs their card in the separately-installed **PocketSign app**; our PWA opens a
Stamp session — `CreateSession` → the app via the returned `redirectUrl` → callback
→ our backend `FinalizeSession` — which rides on Pocket Sign's Verify API to
validate certificate authenticity and return the person key). Verification SHALL
accept both a **physical card (NFC + PIN)** and the **スマホJPKI (phone-embedded
credential)**.
<!-- Corrected 2026-09-02: a PWA uses Stamp + the PocketSign app, not an embedded
     Verify SDK in our own app, and not the government デジタル認証アプリ path. -->
 The system SHALL use
**only JPKI verification data — never the 個人番号 (My Number)**, and SHALL **delete
the raw certificate/response promptly** after the Verify API call (retaining only
the result — see the dedupe + privacy requirements). On success the account's
`verification_level` SHALL become `IDENTITY_VERIFIED`; on failure/abandonment it
SHALL remain `UNVERIFIED`. Pocket Sign is a 公的個人認証法 **認定プラットフォーム事業者**,
so the platform integrates as a 加盟事業者 **without its own 主務大臣認定**.

#### Scenario: Verify via physical card or スマホJPKI

- **WHEN** a fan completes the Pocket Sign challenge–response using either a physical マイナンバーカード (NFC+PIN) or the スマホJPKI credential, and the Verify API validates it
- **THEN** the account becomes `IDENTITY_VERIFIED` and a `VerifiedIdentity` is created

#### Scenario: My Number is never used and raw cert data is deleted

- **WHEN** verification runs
- **THEN** the flow uses only JPKI verification (never the 個人番号), and the raw certificate/response is deleted promptly after the Verify API call

#### Scenario: Failed verification leaves the account unverified

- **WHEN** verification fails or is abandoned
- **THEN** the account stays `UNVERIFIED` and no `VerifiedIdentity` is created

### Requirement: Verified-person dedupe via Pocket Sign `User.id`

The system SHALL identify the verified person by the **Pocket Sign `User.id`** — a
**tenant-scoped UUID** that is the same for the same person within our tenant and
**different across tenants** (a service-scoped pairwise identifier), and that Pocket
Sign returns as the **same value across card renewal, re-issue, certificate
generation, and certificate type**. The system SHALL store **only this `User.id`**
as the person key (never the certificate 発行番号/serial, never the 個人番号) and SHALL
enforce **at most one active `IDENTITY_VERIFIED` account per `User.id`**. A second
verification mapping to an existing `User.id` SHALL be **rejected or routed to
account recovery** (never silently creating a second verified identity). Because
`User.id` is tenant-scoped it does **not** enable cross-platform scalper detection —
an accepted limitation.

#### Scenario: Second account for the same person is rejected

- **WHEN** a person who already has an `IDENTITY_VERIFIED` account verifies again and Pocket Sign returns the same `User.id`
- **THEN** the system rejects the second verification (or offers account recovery), so one person maps to one verified account

#### Scenario: Renewal keeps the same person key (no duplicate on re-issue)

- **WHEN** a fan re-verifies after a card renewal / re-issue / cert-type change
- **THEN** Pocket Sign returns the same `User.id`, so the person re-links to their existing verified account rather than creating a second one

### Requirement: 現況確認 (revocation / attribute-change re-check)

The system SHALL periodically use Pocket Sign's **現況確認 (liveness/現況)** check to
detect certificate **revocation or 基本4情報 change (move/name change) / expiry**. On
a revoked/changed result the system SHALL prompt **re-verification** (not a hard
lock), keeping the verified identity fresh without full re-proofing.

#### Scenario: Revoked/changed identity prompts re-verification

- **WHEN** a 現況確認 check reports the certificate is revoked or the 基本4情報 changed
- **THEN** the system flags the account for re-verification (it is not silently kept as verified, and not hard-locked)

### Requirement: Per-person limit signal and mixed populations

The system SHALL expose the verified person (`User.id`) behind an account so ④
`lottery-application` and ⑤ `ticket-purchase-and-issuance` can enforce **per-person
limits across accounts sharing the same `User.id`**. The per-person guarantee holds
**only among verified persons**: for an event that **requires** verification the
limit is per-person; for an event that does **not** require verification only
**per-account** limits apply and bulk-account resistance is **not** guaranteed — the
platform SHALL state this scope explicitly (do not claim per-person anti-scalp on
non-requiring events).

#### Scenario: Per-person limit spans accounts of the same verified person

- **WHEN** an event requires verification and enforces one application per person, and a verified person applies from a second account
- **THEN** the limit is evaluated against the `User.id`, so the second account cannot exceed it

#### Scenario: Non-requiring event is only per-account

- **WHEN** an event does not require verification
- **THEN** limits are per-account and the system does not represent this as per-person bulk-scalp resistance

### Requirement: Verification lane, per-event requirement, and fallback

Verification SHALL be **optional by default** (`UNVERIFIED`). An
Organizer/administrator MAY mark an **event or lottery phase as requiring a verified
identity**. **MVP scope (2026-09-02): verification-required events are JPKI-only** —
only JPKI-verified (strong-dedupe) fans may apply, and non-card-holders are excluded
by design (the 任意/平等 fairness of this is a legal-review item). Unverified fans
SHALL be **clearly informed** of the requirement and how to satisfy it (JPKI).

**POST-MVP:** a **運転免許証 IC fallback** (Pocket Sign's separate **Verify CardInfo**
product) for non-card fans, which would be **substantively non-disadvantaging**.
**Honest limitation (why it is deferred, not free):** the driver's licence path
proves identity but **does not yield an equivalent stable per-person dedupe key**
(only a document number, which can change) — so a licence-fallback account has a
**weaker 1-person guarantee** and does not advance the anti-scalp core. When added,
each organizer would choose per event to accept the fallback (flag/limit such
accounts) or require JPKI-only. The proto keeps the `DRIVER_LICENCE`/`WEAK`/
`VERIFIED_ANY` values for this forward-compat.

#### Scenario: A verification-required event is JPKI-only (MVP)

- **WHEN** an organizer marks a phase as requiring verification
- **THEN** only JPKI-verified (strong-dedupe) fans may apply, and no weaker fallback is offered (MVP is JPKI-only)

#### Scenario: Licence fallback is offered with a weaker-dedupe flag (POST-MVP)

- **WHEN** (post-MVP) an event allows the 運転免許証 fallback and a non-card fan uses it
- **THEN** they gain verified standing for that event without material disadvantage, and the account is flagged as having a weaker (document-scoped) dedupe

#### Scenario: Unverified fan is clearly informed

- **WHEN** an `UNVERIFIED` fan encounters an event that requires verification
- **THEN** the system clearly informs them of the requirement and how to complete JPKI verification before applying

### Requirement: Relationship to the ④ covered-ticket identity

**MVP:** the covered ticket is bound by ④ lottery-application's apply-time **本人確認
(self-declared name + contact)** (`ApplicantIdentity`); the verified identity supplies
the **per-person dedupe key (`User.id`)** but **not a verified name** in the MVP. This
satisfies the 特定興行入場券 requirement (チケット不正転売禁止法 does not mandate JPKI-level
name verification).

**POST-MVP:** where an event requires verification, the **verified 基本4情報 name**
(retrieved via the JPKI 署名用証明書 + Pocket Sign ConsentService) becomes authoritative
and ④'s self-declared name MUST be **consistent** with it (no conflicting name bound).
Its exact legal sufficiency is a legal-review item.

#### Scenario: Covered ticket is bound by ④'s self-declared identity (MVP)

- **WHEN** a verified person applies to a verification-required event
- **THEN** the covered ticket is bound by ④'s captured self-declared 本人確認 (name + contact), and the verified identity contributes the per-person dedupe key (`User.id`); verified-`基本4情報`-name consistency is a post-MVP enhancement

### Requirement: Privacy — data minimization and deletion

Being "outside 番号法" does NOT reduce 個人情報保護法 duties. The system SHALL: specify
a **利用目的** (identity verification + anti-scalp dedupe), notify on acquisition,
apply security controls, and **store only the `User.id`** by default — retrieving/
retaining **基本4情報 only when a specific use case (e.g. an age gate) justifies it**,
never the 個人番号 or raw serial, and deleting the raw certificate/response
immediately after the Verify API call. It SHALL honor the JPKI-framework
**目的外利用禁止** and the fact that **every Pocket Sign check is logged/reported to
J-LIS** (`check_purpose`), and provide a **deletion** path on purpose-end or valid
request.

#### Scenario: Only the User.id is retained by default

- **WHEN** verification completes for anti-scalp dedupe
- **THEN** the system stores the `User.id` and nothing more (no 基本4情報 unless a specific justified use case requires it, never the 個人番号 or raw serial)

#### Scenario: Verified data is deletable

- **WHEN** the retention purpose ends or the fan makes a valid deletion request
- **THEN** the system deletes the stored identity data (subject to any lawful retention obligation)
