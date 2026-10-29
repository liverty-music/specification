## ADDED Requirements

### Requirement: An admission is announced with the change

When Admit reports Admitted, it SHALL announce the Ticket as admitted, carrying it with its admit time, together with the admit time and the Admission: all are stored or none is. When Admit reports AlreadyAdmitted or Voided, it SHALL announce nothing. When the announcement cannot be recorded, Admit SHALL fail with Unavailable, the Ticket SHALL keep no admit time and no Admission SHALL be stored.

#### Scenario: First admission announced

- **WHEN** an Issued Ticket with no admit time is admitted at 18:32
- **THEN** one admission is announced, carrying the Ticket with admit time 18:32

#### Scenario: Second admission

- **WHEN** a Ticket admitted at 18:32 is admitted again at 18:40
- **THEN** Admit reports AlreadyAdmitted and nothing is announced

#### Scenario: Voided ticket

- **WHEN** a Voided Ticket with no admit time is admitted
- **THEN** Admit reports Voided and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** an admissible Ticket is admitted and the announcement cannot be recorded
- **THEN** Admit fails with Unavailable, the Ticket has no admit time and no Admission is stored
