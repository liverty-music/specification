## Purpose

Verifies an authenticated fan's real-world identity using their national ID card, accepting either a physical card or a phone-embedded credential, and marks the account as identity-verified on success while discarding the raw certificate data it briefly examined.

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
