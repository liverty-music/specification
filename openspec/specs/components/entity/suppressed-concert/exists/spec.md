# SuppressedConcert.Exists

## Purpose

Tells whether a slot — Venue, local date and start time — is suppressed.

## Requirements

### Requirement: Slot lookup

Exists SHALL report true exactly when a SuppressedConcert matches the given Venue, date and start time, an unknown start time matching only an unknown start time.

#### Scenario: Suppressed unknown-start slot
- **WHEN** a SuppressedConcert holds V, 2026-07-01 with no start time and that slot is asked with no start time
- **THEN** Exists reports true

#### Scenario: Not suppressed
- **WHEN** no SuppressedConcert holds the slot
- **THEN** Exists reports false
