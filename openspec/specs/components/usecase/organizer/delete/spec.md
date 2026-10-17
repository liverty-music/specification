# components/usecase/organizer/delete Specification

## Purpose
OrganizerUseCase.Delete permanently removes a deactivated Organizer at an admin's request, together with its series image files, its Organization and every record kept for it, so test Organizers can be cleaned up without leaving dependents behind.

## Requirements

### Requirement: Delete removes a deactivated Organizer with its files, Organization and records

Delete SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist, and SHALL fail with FailedPrecondition, removing nothing, unless its status is deactivated. It SHALL then, in this order:

1. remove the original and served sizes of every SeriesImage returned by SeriesImage.ListByOrganizer, through SeriesImage.DeleteOriginal and SeriesImage.DeleteVariants;
2. remove its Organization through Organization.Delete, when it has a provider organizer ID;
3. remove its records through Organizer.Delete.

Delete needs no confirmation beyond the deactivated status, which only Deactivate sets.

#### Scenario: Deactivated test Organizer

- **WHEN** Delete runs for a deactivated Organizer with a published Series, a cover SeriesImage and an Organization
- **THEN** the SeriesImage files are removed, then the Organization, then the Organizer's records, and Delete succeeds

#### Scenario: Active Organizer

- **WHEN** Delete runs for an active Organizer
- **THEN** it fails with FailedPrecondition, and no file, Organization or record is removed

#### Scenario: Organizer without an Organization

- **WHEN** a deactivated Organizer has no provider organizer ID
- **THEN** Organization.Delete is not called and its files and records are removed

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Delete fails with NotFound

### Requirement: Purchases block deletion before anything is removed

Before removing any file or the Organization, Delete SHALL check what Organizer.Delete would refuse: any of the Organizer's Events with an Order that is not Refunded or with a Settlement that is not Reversed, or a payout-account record. When one exists Delete SHALL fail with FailedPrecondition and remove nothing. A blocker that appears after the check SHALL still be refused by Organizer.Delete, leaving the Organizer's records in place.

#### Scenario: Paid order

- **WHEN** an Event of the deactivated Organizer has a Paid Order
- **THEN** Delete fails with FailedPrecondition and no file, Organization or record is removed

#### Scenario: Refunded order

- **WHEN** the only Order for its Events is Refunded
- **THEN** Delete removes the Organizer, the Order and its Ticket

### Requirement: A failed step can be retried

When removing a file, the Organization or the records fails, Delete SHALL fail with that error. Since files and Organizations already removed count as removed, calling Delete again for the same Organizer SHALL complete the deletion.

#### Scenario: Organization removal fails

- **WHEN** Organization.Delete fails after the SeriesImage files were removed
- **THEN** Delete fails, the Organizer's records remain, and a second call removes the Organization and the records
