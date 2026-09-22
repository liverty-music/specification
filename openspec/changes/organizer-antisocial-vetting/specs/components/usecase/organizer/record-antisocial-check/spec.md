## Purpose

Lets an administrator record the outcome of an antisocial-forces background check performed on an organizer before that organizer is activated, blocking activation on a hit and retaining the reviewer, timestamp, and result for later audit.

## ADDED Requirements

### Requirement: Admin antisocial-forces check gates Organizer activation

Before an Organizer is provisioned/activated, an operator holding the platform
`admin` role SHALL perform a **反社チェック** (name screening of the Organizer
and its principals) and record the outcome — **reviewer, timestamp, and result
(pass / hit)**. A **positive hit SHALL block** the Organizer's creation /
activation. The check record SHALL be retained for audit.

#### Scenario: A passing check allows activation

- **WHEN** an admin records a **passing** 反社チェック for an Organizer
- **THEN** the Organizer MAY be created / activated
- **AND** the check result, reviewer, and timestamp SHALL be recorded

#### Scenario: A hit blocks activation

- **WHEN** the 反社チェック returns a **hit** (or no passing check has been
  recorded)
- **THEN** the system SHALL block the Organizer's creation / activation

#### Scenario: The check record is retained for audit

- **WHEN** a 反社チェック outcome is recorded
- **THEN** it SHALL be retained (reviewer, timestamp, result) for later audit
