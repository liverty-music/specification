## Purpose

Verifies an authenticated fan's real-world identity using their national ID card, accepting either a physical card or a phone-embedded credential, and creates an Active IdentityVerification on success while discarding the raw certificate data it briefly examined.

## ADDED Requirements

### Requirement: JPKI account verification via the verification provider

The system SHALL let an authenticated fan verify their identity with their
**マイナンバーカード 公的個人認証 (JPKI)** through the **verification provider** (the fan
reads and signs their card in the provider's separately-installed app; our PWA opens a
verification session at the provider, hands the fan to the app, and on the callback
the backend completes the session, which has the provider validate certificate
authenticity and return the provider user ID). Verification SHALL
accept both a **physical card (NFC + PIN)** and the **スマホJPKI (phone-embedded
credential)**.
<!-- Corrected 2026-09-02: a PWA uses the provider's session + the provider's app, not an
     embedded verification SDK in our own app, and not the government デジタル認証アプリ path. -->
 The system SHALL use
**only JPKI verification data — never the 個人番号 (My Number)**, and SHALL **delete
the raw certificate/response promptly** after the provider's verification call (retaining only
the result — see the dedupe + privacy requirements). On success the system SHALL create an
Active IdentityVerification for the User; on failure/abandonment it SHALL create none,
and the fan stays unverified. The verification provider is a 公的個人認証法 **認定プラットフォーム事業者**,
so the platform integrates as a 加盟事業者 **without its own 主務大臣認定**.

#### Scenario: Verify via physical card or スマホJPKI

- **WHEN** a fan completes the verification provider's challenge–response using either a physical マイナンバーカード (NFC+PIN) or the スマホJPKI credential, and the provider validates it
- **THEN** an Active IdentityVerification is created for the fan

#### Scenario: My Number is never used and raw cert data is deleted

- **WHEN** verification runs
- **THEN** the flow uses only JPKI verification (never the 個人番号), and the raw certificate/response is deleted promptly after the provider's verification call

#### Scenario: Failed verification leaves the account unverified

- **WHEN** verification fails or is abandoned
- **THEN** no IdentityVerification is created and the fan stays unverified

### Requirement: Each verification outcome is reported for product analytics

Every call of Create that reaches the verification provider SHALL send one "identity verification finished" signal for product analytics for the fan, carrying the outcome and, when verified, the method and whether it renewed an earlier verification of the same person. The outcomes SHALL be: verified; the person is already verified on another account (AlreadyExists); the fan has not finished the session (FailedPrecondition); and failed for any other reason, named by its error code. The signal SHALL carry no provider user ID, name or other personal data. A failure to send it SHALL NOT change the outcome or fail Create.

#### Scenario: Verified with a physical card

- **WHEN** a fan verifies for the first time with a physical card
- **THEN** one signal is sent with the outcome verified, the JPKI method and not a renewal

#### Scenario: Person already verified on another account

- **WHEN** Create fails with AlreadyExists because the provider user ID belongs to another account
- **THEN** one signal is sent with that outcome and no provider user ID

#### Scenario: Session not finished

- **WHEN** the fan returns to the app before finishing the session in the provider's app
- **THEN** one signal is sent with the outcome not finished
