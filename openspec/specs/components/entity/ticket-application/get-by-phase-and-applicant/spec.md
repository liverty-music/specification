# TicketApplication.GetByPhaseAndApplicant

## Purpose

Returns an applicant's active TicketApplication for one phase.

## Requirements

### Requirement: Active application of an applicant

GetByPhaseAndApplicant SHALL return the applicant's active application for the phase and SHALL fail with NotFound when the applicant has none; Withdrawn applications are never returned.

#### Scenario: Active application exists

- **WHEN** the applicant has an Applied, Won or Lost application for the phase
- **THEN** that application is returned

#### Scenario: Only withdrawn applications

- **WHEN** every application of the applicant for the phase is Withdrawn
- **THEN** GetByPhaseAndApplicant fails with NotFound

#### Scenario: Never applied

- **WHEN** the applicant has no application for the phase
- **THEN** GetByPhaseAndApplicant fails with NotFound
