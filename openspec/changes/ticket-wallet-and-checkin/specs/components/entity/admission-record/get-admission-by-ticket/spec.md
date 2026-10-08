# Spec Delta

## Purpose

Finds the record of the scan that admitted a Ticket, to tell staff when and through which link it was already used.

## ADDED Requirements

### Requirement: The admitting record of a ticket

GetAdmissionByTicket SHALL return the Admitted AdmissionRecord of the given Ticket together with the name of its ReceptionLink, and SHALL fail with NotFound when the Ticket has no Admitted record.

#### Scenario: Admitted ticket

- **WHEN** the Ticket was admitted at 18:32 through `受付A`
- **THEN** the record with 18:32 and the link name `受付A` is returned

#### Scenario: Ticket not admitted

- **WHEN** the Ticket has only Rejected records
- **THEN** GetAdmissionByTicket fails with NotFound
