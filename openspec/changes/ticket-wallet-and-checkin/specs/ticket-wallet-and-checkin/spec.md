## Purpose

This capability lets a fan hold and use an issued ticket: a wallet to view it, a
tamper-resistant server-signed rotating QR (gated by a Passkey re-auth) to enter,
same-time companion group entry, and a web-camera reception PWA that validates
the QR and admits attendees — with double-entry prevention.

## ADDED Requirements

### Requirement: Ticket wallet

The system SHALL let an authenticated fan view the **tickets issued to their
account** (from ⑤), including event details and each ticket's **entry status**
(not-yet-entered / entered).

#### Scenario: Fan views their tickets

- **WHEN** an authenticated fan opens their wallet
- **THEN** they see the tickets issued to their account with event details and each ticket's entry status

### Requirement: Server-signed rotating QR entry credential

The entry credential SHALL be a **server-signed, short-lived token that rotates**
on an interval, bound to the specific ticket and holder. Validity SHALL be
determined **server-side**; a captured/screenshotted code SHALL become invalid
once it rotates. The raw credential MUST NOT be forgeable client-side. The
**rotation interval SHALL be short enough that a shared screenshot is unusable
in practice** (target on the order of ~30 seconds — a tunable operational
parameter with a small server-side validation skew window; it MUST NOT be so
long that a captured code stays valid for minutes).

#### Scenario: QR rotates and stale codes are rejected

- **WHEN** a QR code is captured and then the rotation interval elapses
- **THEN** the captured code no longer validates and only the current server-signed code is accepted

#### Scenario: Credential is server-validated

- **WHEN** a QR is presented at the gate
- **THEN** the server verifies its signature, ticket binding, and freshness before admitting

### Requirement: Passkey re-auth to reveal the entry QR

The system SHALL require a **fresh Passkey re-authentication (a WebAuthn step-up
assertion)** before revealing/opening a ticket's entry QR, so a shared screen or a
handed-off device cannot be used to enter. **Dependency:** the shipped
identity-management surface currently specs Passkey only as a *login* policy and
re-auth only as the 90-day refresh expiry — there is **no per-action step-up
primitive yet**. This capability therefore **requires a new WebAuthn step-up /
fresh-assertion capability** in identity-management (a prerequisite delta, tracked
in tasks §0); it MUST NOT be silently downgraded to an ordinary session check
(which would not deliver the shared-screen-cannot-enter guarantee).

#### Scenario: QR requires a fresh Passkey step-up

- **WHEN** a fan opens the entry QR for a ticket
- **THEN** the system requires a fresh WebAuthn step-up assertion before showing the current code (not merely an existing session)

### Requirement: Same-time companion group entry

For a multi-ticket order, the system SHALL support **same-time group entry**: the
**lead holds all N tickets on their own device** and the lead + companions enter
**together**. The system SHALL NOT provide any **distribution URL** or per-
companion transferable code (deliberately rejected as a scalping loophole). The
lead MAY admit a **subset (M of N)** in one scan when only part of the group has
arrived; the **remaining N−M stay valid (not-yet-entered)** for a later scan on
the same lead device, and each ticket is marked entered **only when actually
admitted** (so a subset scan never burns an absent companion's ticket, and the
no-double-entry rule applies per-ticket).

#### Scenario: Lead admits the whole group together

- **WHEN** the lead presents their device holding N companion tickets and all N are being admitted
- **THEN** the N tickets are admitted together in one same-time entry

#### Scenario: Partial group arrival admits only those present

- **WHEN** only M of N companions are present and the lead admits M
- **THEN** exactly M tickets are marked entered and the remaining N−M stay valid for a later scan (no companion ticket is burned while absent)

#### Scenario: No companion distribution mechanism

- **WHEN** a lead wants to hand a companion ticket to another person off-platform
- **THEN** the system offers no distribution URL or transferable per-companion code (the sanctioned hand-off is ⑦ official resale)

### Requirement: Reception check-in PWA (web camera)

The system SHALL provide a **reception PWA** that scans the rotating QR using the
**web camera (`getUserMedia`)** — no native app. On a scan the server SHALL
validate signature + freshness + ticket binding + **not-already-used**, and admit
or reject accordingly.

#### Scenario: Staff scans and admits a valid ticket

- **WHEN** staff scan a valid current QR with the reception PWA
- **THEN** the server validates it and the ticket is admitted

#### Scenario: Reception runs in the browser

- **WHEN** reception is opened
- **THEN** it captures the camera via getUserMedia in a PWA with no native app install

### Requirement: Real-time entry status and no double-entry

On a successful scan the system SHALL mark the ticket **entered** in real time. A
subsequent scan of an **already-entered** ticket SHALL be **rejected** (no double
entry).

#### Scenario: Entry status updates on admit

- **WHEN** a ticket is admitted
- **THEN** its status becomes entered in real time and is visible in the wallet and reception

#### Scenario: Re-scan is rejected

- **WHEN** an already-entered ticket is scanned again
- **THEN** the scan is rejected as already used

### Requirement: Void invalidates the entry credential

When a ticket is **voided** (e.g. ⑦ official-resale reissues the seat to a new
buyer, or an admin action), the system SHALL immediately **invalidate its
rotating QR** so the voided ticket can no longer enter.

#### Scenario: Voided ticket cannot enter

- **WHEN** a ticket is voided
- **THEN** its rotating QR stops validating and it cannot be admitted at the gate
