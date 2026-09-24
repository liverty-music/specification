# TicketApplication.Create

## Purpose

Stores a new TicketApplication for a phase and returns it as stored.

## Requirements

### Requirement: One active application per account per phase

Create SHALL store the application and return it. It SHALL fail with AlreadyExists when the applicant already has an active application for the same phase, and with FailedPrecondition when the phase does not exist.

#### Scenario: First application

- **WHEN** Create is called for an applicant with no active application for the phase
- **THEN** the application is stored and returned

#### Scenario: Active application exists

- **WHEN** the applicant already has an Applied, Won or Lost application for the phase
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Re-application after withdrawal

- **WHEN** the applicant's only earlier application for the phase is Withdrawn
- **THEN** Create stores the new application alongside the withdrawn one

#### Scenario: Unknown phase

- **WHEN** the phase does not exist
- **THEN** Create fails with FailedPrecondition
