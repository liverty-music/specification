# Spec Delta

## Purpose

OrganizerUseCase.SetBusinessDetails lets an admin record an Organizer's business details for the 特商法 (Specified Commercial Transactions Act) disclosure, checked during vetting, so its events can go on sale.

## ADDED Requirements

### Requirement: Admin records the business details

SetBusinessDetails SHALL take an Organizer and its legal name, representative name, business address, business phone number and contact email, store them with Organizer.SetBusinessDetails and return the Organizer. Its failures SHALL be returned unchanged. It SHALL fail with FailedPrecondition, changing nothing, when the Organizer, read with Organizer.Get, is deactivated.

#### Scenario: Details recorded at vetting

- **WHEN** an admin records all five business details for an active Organizer
- **THEN** the Organizer has complete business details and its events can go on sale

#### Scenario: Deactivated Organizer

- **WHEN** the Organizer is deactivated
- **THEN** SetBusinessDetails fails with FailedPrecondition and nothing changes
