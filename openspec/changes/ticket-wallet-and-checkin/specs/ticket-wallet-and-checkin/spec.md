## Purpose

This capability lets a fan hold and use an issued ticket: an in-app wallet that
renders the ticket (incl. its covered-ticket face) and an **entry credential = an
in-app dynamic QR backed by a server-signed, short-TTL token**, validated by
**signature + freshness verification and then an online atomic
duplicate-check** at admit, scanned by a web-camera **reception PWA**. Anti-scalp
is NOT enforced by a gate-time re-authentication; it rests on the platform's
tiered model (see design). OS Wallet passes are a deferred convenience tier.

## ADDED Requirements

### Requirement: Ticket wallet renders the ticket and its covered-ticket face

The system SHALL let an authenticated fan view the **tickets issued to their
account** (from ⑤): event details, each ticket's **entry status** (not-yet-entered
/ entered), and the **covered-ticket (特定興行入場券) face conditions** defined by ⑤
— (i) the resale-without-organizer-consent-prohibited statement, (ii) date/venue +
seat-or-eligible-person, (iii) the 本人確認 (name) — rendered on the presented
credential so the ticket satisfies the "stated on its face" test where the holder
actually presents it. ⑤ owns the face **content**; ⑥ owns **rendering** it.

#### Scenario: Fan views their ticket with the covered-ticket face

- **WHEN** an authenticated fan opens a ticket in their wallet
- **THEN** they see event details, entry status, and the covered-ticket face conditions (resale-prohibited notice + date/venue/seat-or-eligible-person + 本人確認) rendered on the presented credential

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

### Requirement: Validate signature + freshness, then atomic duplicate-check at admit

On each scan the reception SHALL send the token to the **server**, which SHALL
**(1) verify the signature and TTL/epoch freshness** (rejecting forged or stale
tokens) and **(2) perform an atomic check-and-set** on the ticket's entry state
(conditional update / unique constraint / row lock, keyed **per ticket** — never a
table-level lock), returning **allow or deny BEFORE the attendee is admitted**.
Signature+freshness is the forgery/screenshot control; the atomic check-and-set
resolves the 1:1 concurrency race. Two concurrent scans of the same ticket — at
the same or different gates — MUST result in **exactly one admit**. If the server
is unreachable the reception SHALL **fail closed** (show a retry), not admit
blindly.

#### Scenario: First scan wins, duplicate is denied

- **WHEN** the same ticket is scanned twice (same or different gates), even simultaneously
- **THEN** the server verifies the token then admits exactly one (the atomic check-and-set succeeds once) and denies the other as already-entered

#### Scenario: Stale or forged token is rejected before dedup

- **WHEN** a token fails signature or freshness verification
- **THEN** it is rejected without consuming the ticket's entry state

#### Scenario: Server unreachable fails closed

- **WHEN** the reception cannot reach the server
- **THEN** it shows a retry and does not admit (no blind offline admit in MVP)

### Requirement: Reception check-in PWA (web camera)

The system SHALL provide a **reception PWA** that scans the QR using the **web
camera (`getUserMedia`)** — no native app, no NFC reader hardware — and performs
the server validation + atomic duplicate-check above.

#### Scenario: Reception runs in the browser

- **WHEN** reception is opened
- **THEN** it captures the camera via getUserMedia in a PWA with no native app install and no NFC reader hardware

### Requirement: Same-time companion group entry

For a multi-ticket order, the fan's authenticated wallet session SHALL present the
group's credentials together for **same-time group entry**, and the system SHALL
build **no first-party distribution URL** or transferable per-companion code (the
sanctioned hand-off is ⑦ official resale). Admitting a **subset (M of N)** SHALL
mark entered **only the M actually scanned**; the remaining N−M stay valid for a
later scan (per-ticket atomic dedup applies). Because the credentials live only in
the lead's authenticated in-app session (not OS-shareable passes), the group is
not an off-platform distribution vector.

#### Scenario: Partial group arrival admits only those present

- **WHEN** only M of N companions are present and M credentials are scanned
- **THEN** exactly M tickets are marked entered and the remaining N−M stay valid for a later scan

#### Scenario: No first-party distribution mechanism

- **WHEN** a holder wants to hand a ticket to another person
- **THEN** the system offers no first-party distribution URL or transferable per-companion code (the sanctioned path is ⑦ official resale)

### Requirement: Entry status and no double-entry

On a successful admit the system SHALL mark the ticket **entered** and surface the
status in the wallet and reception. A subsequent scan of an **already-entered**
ticket SHALL be **rejected**.

#### Scenario: Re-scan is rejected

- **WHEN** an already-entered ticket is scanned again
- **THEN** the scan is rejected as already used

### Requirement: Void invalidates the entry credential

When a ticket is **voided** (e.g. ⑦ official-resale reissues the seat to a new
buyer, or an admin action), the **server-side validation SHALL reject** the voided
ticket's token at admit (regardless of what the device still renders), so the
voided ticket can no longer be admitted.

#### Scenario: Voided ticket cannot enter

- **WHEN** a ticket is voided
- **THEN** its token no longer validates at admission and it cannot be admitted at the gate
