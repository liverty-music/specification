## Purpose

A resale listing represents one ticket its holder has offered back to the platform for a sanctioned face-value resale, tracking its price, deadline, and lifecycle from listed through matched, withdrawn, or expired, so no seat changes hands off-platform or above face value.

## ADDED Requirements

### Requirement: Resale deadline

The system SHALL stop accepting new listings and stop matching at a **resale
deadline of one hour before the event start time (`start_time − 1h`)**. An
Organizer MAY configure an **earlier** cutoff for their event but MUST NOT set a
later one.

#### Scenario: Listing after the deadline is rejected

- **WHEN** the owner attempts to list a ticket at or after `start_time − 1h` (or the organizer's earlier cutoff)
- **THEN** the system rejects the listing because the resale window has closed

#### Scenario: Organizer sets an earlier cutoff

- **WHEN** an Organizer configures a resale cutoff earlier than `start_time − 1h`
- **THEN** listing and matching stop at that earlier time for that event

### Requirement: Resale is enabled by default with structural exclusions only

The system SHALL treat official resale as **enabled by default on every standard
paid event** (consent obtained as a blanket, standing grant in the vetted
Organizer's platform agreement). It SHALL provide **no organizer self-serve
off-switch**. A ticket SHALL be **non-resellable only** when an automatic
**structural exclusion** applies — the ticket is **free (¥0)**, a **comp/invite**,
**bundled with physical goods**, or a **name-locked special ticket** (a ticket
type flagged as non-transferable by design — e.g. an FC-restricted or
named-holder-only ticket — which is distinct from the ordinary 本人確認 binding
that every covered ticket, including reissued resale tickets, carries) — or when an
**administrator** grants a documented exception for the event. These exclusion
flags are ticket-type metadata defined by ⑤/⑥ (see design.md dependency).

#### Scenario: Standard paid event is resale-enabled without organizer action

- **WHEN** a vetted Organizer publishes a standard paid event
- **THEN** official resale is enabled for that event by default with no per-event opt-in step

#### Scenario: Structurally excluded ticket cannot be listed

- **WHEN** the owner attempts to list a free, comp, goods-bundled, or name-locked ticket
- **THEN** the system rejects the listing because the ticket is structurally excluded from resale

#### Scenario: Administrator excludes an event by exception

- **WHEN** an administrator records a documented resale exception for a specific event
- **THEN** listing is disabled for that event, LISTED listings are withdrawn, and any in-flight OFFERED offer is voided with no charge (admin action overrides the OFFERED lock, which only blocks the *seller*'s own withdrawal); already-SOLD resales are unaffected

### Requirement: Event cancellation or postponement while listed

When an event is **cancelled** while a ticket is in `LISTED` or `OFFERED` state
(fresh-sale leg not yet completed), the system SHALL cancel the listing/offer and
route the ticket to the **normal cancellation-refund path** — the resale
fresh-sale leg MUST NOT execute. When an event is **postponed**, existing `LISTED`
listings SHALL remain valid and any **in-flight `OFFERED` offer SHALL continue**
against the **recomputed** resale **deadline** (new `start_time − 1h`), and any
already-completed resale SHALL be unaffected (the reissued ticket stays valid for
the new date). Because the seller refund is keyed
on resale completion (not the event), postponement does not change settled refunds.

#### Scenario: Cancellation supersedes a live listing

- **WHEN** an event is cancelled while a ticket is in LISTED or OFFERED state
- **THEN** the listing/offer is cancelled and the holder receives the standard cancellation refund, not a resale outcome

#### Scenario: Postponement recomputes the deadline and preserves settled resales

- **WHEN** an event is postponed
- **THEN** open listings stay valid with the deadline recomputed to the new start time, and any completed resale and its settled refund are unaffected

### Requirement: Anonymity and no person-to-person contact

The system SHALL keep sellers and buyers **anonymous to each other**: they MUST
NOT exchange personal information and money MUST NOT move person-to-person. All
matching happens through the platform pool.

#### Scenario: No personal information is exchanged

- **WHEN** a resale match completes
- **THEN** neither party learns the other's identity or contact details, and no direct payment occurred between them
