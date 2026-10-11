# components/usecase/organizer/update-seller-details Specification

## Purpose
OrganizerUseCase.UpdateSellerDetails lets an admin record an Organizer's 特商法 (Specified Commercial Transactions Act) seller details, checked during vetting, so its events can go on sale.

## Requirements

### Requirement: Admin records the seller details

UpdateSellerDetails SHALL take an Organizer and its seller details, store them with Organizer.SetSellerDetails and return the Organizer. Its failures SHALL be returned unchanged. It SHALL fail with FailedPrecondition when the Organizer, read with Organizer.Get, is deactivated.

#### Scenario: Details recorded at vetting

- **WHEN** an admin records complete seller details for an active Organizer
- **THEN** the Organizer has complete seller details and its events can go on sale

#### Scenario: Deactivated Organizer

- **WHEN** the Organizer is deactivated
- **THEN** UpdateSellerDetails fails with FailedPrecondition and nothing changes
