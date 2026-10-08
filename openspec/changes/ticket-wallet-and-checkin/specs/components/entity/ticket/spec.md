# Spec Delta

## ADDED Requirements

### Requirement: A ticket is admissible only once and only while Issued

A Ticket SHALL be admissible exactly when its status is Issued and it has no admitted time. A Voided Ticket SHALL NOT be admissible, and a Ticket that has an admitted time SHALL NOT be admissible again. Voiding a Ticket SHALL keep its admitted time, so a refund after entry does not erase that the holder was admitted.

#### Scenario: Issued and not yet admitted

- **WHEN** a Ticket is Issued and has no admitted time
- **THEN** it is admissible

#### Scenario: Already admitted

- **WHEN** a Ticket is Issued and was admitted at 18:32
- **THEN** it is not admissible

#### Scenario: Voided

- **WHEN** a Ticket is Voided and has no admitted time
- **THEN** it is not admissible

#### Scenario: Voided after entry

- **WHEN** a Ticket admitted at 18:32 is Voided by a dispute refund
- **THEN** its status is Voided and its admitted time is still 18:32
