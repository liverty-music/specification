## Purpose

Excludes 反社会的勢力 (antisocial forces) from the platform's Organizer
relationships, as expected of a money-handling marketplace under the 暴力団
排除条例: an onboarding exclusion clause, an admin 反社チェック gate before an
Organizer is activated, and deactivation on later discovery.

## ADDED Requirements

### Requirement: Organizer onboarding agreement includes an antisocial-forces exclusion clause

The onboarding agreement each Organizer accepts SHALL include a 暴排条項:
(a) a **representation and warranty** that the Organizer and its principals
are **not** 反社会的勢力 (暴力団・暴力団員・準構成員・関係企業・総会屋・
社会運動標ぼうゴロ・特殊知能暴力集団 等) and have no relationship providing
them funds or convenience; and (b) the platform's right to **terminate the
relationship and deactivate the Organizer immediately, without liability**, on
breach.

#### Scenario: Onboarding requires accepting the 暴排条項

- **WHEN** an Organizer is onboarded
- **THEN** acceptance of the 暴排条項 (antisocial-forces exclusion clause)
  SHALL be a condition of the onboarding agreement

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

### Requirement: Post-onboarding antisocial discovery triggers deactivation

If a 反社 relationship is discovered **after** onboarding, an operator holding
the platform `admin` role SHALL **deactivate** the Organizer (reusing the
existing deactivation hook), and the breach of the 暴排条項 SHALL be a
documented ground for termination.

#### Scenario: Later discovery deactivates the organizer

- **WHEN** a 反社 relationship is discovered for an already-onboarded Organizer
- **THEN** an admin SHALL deactivate the Organizer
- **AND** the deactivation SHALL reject the Organizer's subsequent operations
  (per the existing deactivation behavior)
