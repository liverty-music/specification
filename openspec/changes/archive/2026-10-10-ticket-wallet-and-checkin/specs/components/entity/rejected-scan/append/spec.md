# Spec Delta

## Purpose

Adds RejectedScans; nothing ever changes or removes one.

## ADDED Requirements

### Requirement: Append adds RejectedScans and never alters existing ones

Append SHALL store the given RejectedScans, all of them or none. It SHALL fail with InvalidArgument and store nothing when any of them is invalid. No operation SHALL change or remove a stored RejectedScan.

#### Scenario: Group rejected

- **WHEN** 3 RejectedScans for one scan are appended
- **THEN** all 3 are stored

#### Scenario: Invalid one in the batch

- **WHEN** 2 valid RejectedScans and 1 with reason Forged naming a Ticket are appended
- **THEN** Append fails with InvalidArgument and none is stored
