# components/usecase/organizer/set-platform-fee-rate Specification

## Purpose
OrganizerUseCase.SetPlatformFeeRate lets an admin set the platform fee rate applied to an Organizer's future Orders, for example a pilot rate.

## Requirements

### Requirement: Admin sets the rate for future orders

SetPlatformFeeRate SHALL take an Organizer and a rate, store it with Organizer.SetPlatformFeeRate and return the Organizer. Its failures SHALL be returned unchanged. Orders already issued keep the rate of their Settlement.

#### Scenario: Pilot Organizer

- **WHEN** an admin sets the pilot Organizer's rate to 5%
- **THEN** its next Orders are settled at 5% and earlier Orders are unchanged
