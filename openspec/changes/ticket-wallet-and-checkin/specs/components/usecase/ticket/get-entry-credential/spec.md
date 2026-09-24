## Purpose

Produces the entry credential a fan presents at the gate: an in-app dynamic QR encoding a server-signed, short-lived token that cannot be screenshotted for later reuse or forged without the signing secret, shown without any extra re-authentication.

## ADDED Requirements

### Requirement: Entry credential is an in-app dynamic QR from a signed short-TTL token

The entry credential SHALL be an **in-app dynamic QR** rendered live inside the
fan's **authenticated** wallet session, encoding a **server-signed, short-TTL
bearer token** (signed over a claims set: ticket id, event id, holder reference,
and a rotating epoch; TTL on the order of ~30 seconds; the signing secret lives
**server-side only**). It SHALL work **cross-platform** (no dependence on any OS
Wallet capability) and MUST NOT be a shareable OS pass. The system SHALL require
**no gate-time re-authentication** (no passkey step-up) to display it. The token
claims SHALL be a structured claims set (to preserve a future SD-JWT-VC / mdoc
migration path), not an opaque blob.

#### Scenario: Screenshot is stale after the TTL

- **WHEN** a QR is captured/screenshotted and the TTL elapses
- **THEN** the captured token no longer verifies (only a current-epoch signed token is accepted)

#### Scenario: A forged or leaked ticket id cannot mint a valid credential

- **WHEN** an attacker knows a ticket id but not the server signing secret
- **THEN** they cannot produce a token that passes signature verification, so no valid credential can be forged

#### Scenario: No gate-time re-auth to show the credential

- **WHEN** a fan opens their entry credential at the gate
- **THEN** no fresh passkey / step-up re-authentication is required to display it
