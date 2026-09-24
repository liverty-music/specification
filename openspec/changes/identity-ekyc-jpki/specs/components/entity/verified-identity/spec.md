## Purpose

A verified identity links an account to one real person confirmed through public personal identification, keyed by a stable per-tenant person identifier so a single person cannot hold more than one verified account. It stores only the minimum data that dedupe guarantee requires and stays deletable once its purpose ends or on a valid request.

## ADDED Requirements

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
