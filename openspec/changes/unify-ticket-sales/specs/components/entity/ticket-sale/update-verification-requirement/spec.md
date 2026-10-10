# Spec Delta

## Purpose

Sets the verification requirement of one TicketSale and returns the updated sale.

## ADDED Requirements

### Requirement: Update the requirement

UpdateVerificationRequirement SHALL set the sale's verification requirement, leave its other attributes and its TicketTypes unchanged and return the updated sale. It SHALL fail with InvalidArgument when no sale id is given and with NotFound when no sale has the id.

#### Scenario: Requirement changed
- **WHEN** a sale's requirement None is updated to JPKI-only
- **THEN** the returned sale requires JPKI-only and its window and TicketTypes are unchanged

#### Scenario: Unknown id
- **WHEN** no sale has the id
- **THEN** UpdateVerificationRequirement fails with NotFound
