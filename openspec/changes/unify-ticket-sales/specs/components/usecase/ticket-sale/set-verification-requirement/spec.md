# Spec Delta

## Purpose

TicketSaleUseCase.SetVerificationRequirement lets an Organizer change whether fans taking part in one of its TicketSales must hold a verified identity.

## ADDED Requirements

### Requirement: Change the requirement at any time

SetVerificationRequirement SHALL set the sale's verification requirement with TicketSale.UpdateVerificationRequirement and return the updated sale, whether or not the window is open and whether or not the sale is drawn. It SHALL fail with InvalidArgument when no sale is given. Entries already made are not re-checked.

#### Scenario: Requirement tightened while open
- **WHEN** an Organizer sets JPKI-only on an open sale
- **THEN** the sale requires JPKI-only and later entries are checked against it

#### Scenario: After the draw
- **WHEN** an Organizer changes the requirement of a drawn sale
- **THEN** the requirement is changed

#### Scenario: Unknown sale
- **WHEN** the sale does not exist
- **THEN** SetVerificationRequirement fails with NotFound

### Requirement: Only the Series' Organizer changes the requirement

SetVerificationRequirement SHALL read the sale with TicketSale.Get and its Series with Series.GetAuthored, and SHALL fail with PermissionDenied when the calling Organizer does not own that Series.

#### Scenario: Another Organizer's sale
- **WHEN** an Organizer changes the requirement of a sale on a Series owned by a different Organizer
- **THEN** SetVerificationRequirement fails with PermissionDenied and nothing changes
