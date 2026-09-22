## Purpose

Validates a scanned entry credential's signature and freshness and then admits its ticket through an atomic check that guarantees exactly one admission per ticket, supporting partial group entry and rejecting a voided, stale, or already-used ticket.

## ADDED Requirements

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
