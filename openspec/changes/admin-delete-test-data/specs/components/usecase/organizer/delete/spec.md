# Spec Delta

## Purpose

OrganizerUseCase.Delete permanently removes a deactivated Organizer at an admin's request, together with its media files, its sign-in tenant and every record kept for it, so test Organizers can be cleaned up without leaving dependents behind.

## ADDED Requirements

### Requirement: Delete removes a deactivated Organizer with its files, tenant and records

Delete SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist, and SHALL fail with FailedPrecondition, removing nothing, unless its status is deactivated. It SHALL then, in this order:

1. remove the original and served sizes of every Media returned by Media.ListByOrganizer, through Media.DeleteOriginal and Media.DeleteVariants;
2. remove its tenant through Organizer.DeleteTenant, when it has a tenant link;
3. remove its records through Organizer.Delete.

Delete needs no confirmation beyond the deactivated status, which only Deactivate sets.

#### Scenario: Deactivated test Organizer

- **WHEN** Delete runs for a deactivated Organizer with a published Series, a cover Media and a tenant
- **THEN** the Media files are removed, then the tenant, then the Organizer's records, and Delete succeeds

#### Scenario: Active Organizer

- **WHEN** Delete runs for an active Organizer
- **THEN** it fails with FailedPrecondition, and no file, tenant or record is removed

#### Scenario: Organizer without a tenant

- **WHEN** a deactivated Organizer has no tenant link
- **THEN** Organizer.DeleteTenant is not called and its files and records are removed

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Delete fails with NotFound

### Requirement: Purchases block deletion before anything is removed

Before removing any file or the tenant, Delete SHALL check what Organizer.Delete would refuse: any of the Organizer's Events with an Order that is not Refunded or with a Settlement, or a payout-account record. When one exists Delete SHALL fail with FailedPrecondition and remove nothing. A blocker that appears after the check SHALL still be refused by Organizer.Delete, leaving the Organizer's records in place.

#### Scenario: Paid order

- **WHEN** an Event of the deactivated Organizer has a Paid Order
- **THEN** Delete fails with FailedPrecondition and no file, tenant or record is removed

#### Scenario: Refunded order

- **WHEN** the only Order for its Events is Refunded
- **THEN** Delete removes the Organizer, the Order and its Ticket

### Requirement: A failed step can be retried

When removing a file, the tenant or the records fails, Delete SHALL fail with that error. Since files and tenants already removed count as removed, calling Delete again for the same Organizer SHALL complete the deletion.

#### Scenario: Tenant removal fails

- **WHEN** Organizer.DeleteTenant fails after the Media files were removed
- **THEN** Delete fails, the Organizer's records remain, and a second call removes the tenant and the records
