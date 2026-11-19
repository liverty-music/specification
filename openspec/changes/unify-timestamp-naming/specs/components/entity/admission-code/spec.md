# Spec Delta

## MODIFIED Requirements

### Requirement: A code is fresh for a short time around its signing

An AdmissionCode SHALL be fresh at a time when its sign time is at most 30 seconds before that time and at most 15 seconds after it. The second bound allows for a device clock that runs slightly fast.

#### Scenario: Just shown

- **WHEN** a code signed at 18:30:00 is checked at 18:30:10
- **THEN** it is fresh

#### Scenario: Screenshot shown later

- **WHEN** a code signed at 18:30:00 is checked at 18:30:31
- **THEN** it is not fresh

#### Scenario: Device clock slightly fast

- **WHEN** a code signed at 18:30:10 by the device's clock is checked at 18:30:00
- **THEN** it is fresh

#### Scenario: Device clock far ahead

- **WHEN** a code signed at 18:31:00 by the device's clock is checked at 18:30:00
- **THEN** it is not fresh
