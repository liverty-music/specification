## Purpose

Returns an unsold ticket to its original holder once the resale deadline passes, sweeping expired listings on a schedule so a listing is never left dangling and the holder can still attend at no extra cost.

## ADDED Requirements

### Requirement: Unsold listing returns to the holder

The system SHALL return an **unsold** ticket to its holder at the deadline so the
holder may still attend, charging **no fee**. A **scheduled sweep** (not a lazy
on-access check) SHALL transition unsold `LISTED` listings to `EXPIRED` at the
deadline so no listing is left dangling. Resale SHALL be presented as **not
guaranteed**, disclosed **before** listing.

#### Scenario: Unsold ticket is returned

- **WHEN** the resale deadline passes with the listing unmatched
- **THEN** the scheduled sweep moves the listing to EXPIRED, the ticket returns to the holder as valid for entry, and no fee is charged
