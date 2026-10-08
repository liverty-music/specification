# Spec Delta

## Purpose

Adds Rejected AdmissionRecords; nothing ever changes or removes a record. Admitted records are stored only by Ticket.Admit.

## ADDED Requirements

### Requirement: Append adds records and never alters existing ones

Append SHALL store the given Rejected AdmissionRecords, all of them or none, and return them with their ids. It SHALL fail with InvalidArgument and store nothing when any record is invalid or Admitted. No operation SHALL change or remove a stored AdmissionRecord.

#### Scenario: Group rejected

- **WHEN** 3 Rejected records for one scan are appended
- **THEN** all 3 are stored

#### Scenario: Invalid record in the batch

- **WHEN** 2 valid Rejected records and 1 Admitted record are appended
- **THEN** Append fails with InvalidArgument and none is stored
