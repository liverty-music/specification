# Spec Delta

## ADDED Requirements

### Requirement: Method is the only classification

A sales phase SHALL be classified only by its method, which SHALL be `LOTTERY` or `FIRST_COME`. A phase without a method or with any other value SHALL be invalid.

#### Scenario: Fan-club lottery

- **WHEN** a fan club runs a lottery presale for a tour
- **THEN** the phase's method is `LOTTERY`

#### Scenario: No method

- **WHEN** a phase has no method
- **THEN** the phase is invalid

### Requirement: When an application has ended

A sales phase's application SHALL have ended at its apply end time. A `FIRST_COME` phase without an apply end time SHALL count as ended at its apply start time.

#### Scenario: Lottery before its close

- **WHEN** a `LOTTERY` phase closes on 22 October 23:59 and the current time is 20 October
- **THEN** its application has not ended

#### Scenario: First-come sale until sold out

- **WHEN** a `FIRST_COME` phase has no apply end time and opened at 18:30 today
- **THEN** its application has ended since 18:30

### Requirement: Required milestones depend on the method

A sales phase SHALL always have a known apply start time. A `LOTTERY` phase SHALL also have an apply end time; a `FIRST_COME` phase's apply end time SHALL be optional, and an absent value SHALL mean the sale ends when tickets run out. A lottery result time SHALL be optional and SHALL appear only on a `LOTTERY` phase. An apply end time SHALL be after the apply start time, and a lottery result time SHALL NOT be before the apply end time.

#### Scenario: First-come sale until sold out

- **WHEN** a `FIRST_COME` phase has an apply start time and no apply end time
- **THEN** the phase is valid

#### Scenario: Lottery without a close

- **WHEN** a `LOTTERY` phase has no apply end time
- **THEN** the phase is invalid

#### Scenario: No start time

- **WHEN** a phase has no apply start time
- **THEN** the phase is invalid

#### Scenario: Close before open

- **WHEN** a phase's apply end time is before its apply start time
- **THEN** the phase is invalid

#### Scenario: Result before close

- **WHEN** a `LOTTERY` phase's lottery result time is before its apply end time
- **THEN** the phase is invalid

#### Scenario: Result on a first-come sale

- **WHEN** a `FIRST_COME` phase has a lottery result time
- **THEN** the phase is invalid

## REMOVED Requirements

### Requirement: Method and channel are orthogonal classifications

**Reason**: Channel, provider name and sequence are removed. No notification uses them, and channel classification was the most frequent extraction error.
**Migration**: The columns are dropped and every stored phase is deleted. Many stored phases break the new rules (method `UNSPECIFIED`, a lottery without a close), no reminder was ever sent for any of them, and discovery finds the sales that are still upcoming again; see design.md.

### Requirement: Only the apply start time is required

**Reason**: The required milestones now depend on the method, and the payment deadline and the provider-name and sequence limits are gone.
**Migration**: Replaced by "Required milestones depend on the method".
