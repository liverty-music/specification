## Purpose

Lets the current holder of an eligible, unused ticket list it for official resale at its fixed face value ahead of the event's resale deadline, rejecting tickets that are already listed, used, refunded, or otherwise ineligible for resale.

## ADDED Requirements

### Requirement: List a ticket for resale

The system SHALL allow the current **owner** of a ticket to list it for official
resale when the ticket is **PAID and unused**, its event is in the **future**,
resale is **enabled** for that event, and the **resale deadline has not passed**.
The listing price SHALL be **fixed to the ticket's face value** — defined as the
**ticket price (券面代金) only, excluding the original purchase-side booking/service
fee** — the seller MUST NOT be able to set any other price. A ticket that is
already listed, used, refunded, or belongs to a past/cancelled event MUST NOT be
listable.

#### Scenario: Owner lists an eligible ticket

- **WHEN** the owner of a PAID, unused ticket for a future resale-enabled event lists it before the deadline
- **THEN** a resale listing is created in state LISTED at the ticket's original face value, and the ticket becomes visible in the resale demand-matching pool

#### Scenario: Price is locked to face value

- **WHEN** a listing is created
- **THEN** its price equals the ticket's original purchase price and cannot be set above or below it

#### Scenario: Ineligible ticket is rejected

- **WHEN** the owner attempts to list a ticket that is used, already listed, refunded, or for a past or cancelled event
- **THEN** the system rejects the listing with a precondition failure and no listing is created
