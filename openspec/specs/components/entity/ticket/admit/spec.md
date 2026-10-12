# components/entity/ticket/admit Specification

## Purpose
Admits one Ticket through a Scanner at a given time, at most once, together with its Admission, and reports why when it cannot.

## Requirements

### Requirement: Admit sets the admit time once

Admit SHALL take a Ticket, a ReceptionLink and a time. When the Ticket is admissible, Admit SHALL set its admit time to the given time, store an Admission naming the Ticket, the link and the time, and report Admitted; the admit time and the Admission SHALL be stored together or not at all, so an admitted Ticket always has its Admission. When the Ticket already has an admit time, Admit SHALL change nothing and report AlreadyAdmitted with the existing admit time. When the Ticket is Voided and has no admit time, Admit SHALL change nothing and report Voided. Checking, setting and recording SHALL be one indivisible step, so that of any number of concurrent Admit calls for the same Ticket exactly one reports Admitted. Admit SHALL fail with NotFound when no Ticket has the id.

#### Scenario: First admission

- **WHEN** an Issued Ticket with no admit time is admitted through `受付1` at 18:32
- **THEN** its admit time is 18:32, an Admission with `受付1` and 18:32 is stored, and Admit reports Admitted

#### Scenario: Second admission

- **WHEN** a Ticket admitted at 18:32 is admitted again at 18:40
- **THEN** its admit time stays 18:32 and Admit reports AlreadyAdmitted with 18:32

#### Scenario: Concurrent admissions

- **WHEN** two Admit calls for the same admissible Ticket run at the same time
- **THEN** exactly one reports Admitted and the other reports AlreadyAdmitted

#### Scenario: Voided ticket

- **WHEN** a Voided Ticket with no admit time is admitted
- **THEN** nothing changes and Admit reports Voided

#### Scenario: Unknown ticket

- **WHEN** no Ticket has the id
- **THEN** Admit fails with NotFound
