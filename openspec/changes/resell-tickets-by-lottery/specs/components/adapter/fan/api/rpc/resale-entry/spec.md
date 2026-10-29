# Spec Delta

## Purpose

The fan-facing official resale entry service boundary (`ResaleEntryService`): how a signed-in fan's call becomes a ResaleEntryUseCase call for that fan's own entries.

## ADDED Requirements

### Requirement: Resale entry requests are validated at the boundary

Each call SHALL fail with InvalidArgument, before any usecase runs, when:
- AuthorizeCard names no TicketStock or its ticket count is not greater than 0;
- AuthorizeCard's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens);
- AuthorizeCard's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form;
- Confirm names no card authorization;
- Withdraw names no resale entry.

#### Scenario: Zero tickets
- **WHEN** AuthorizeCard is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Valid application
- **WHEN** AuthorizeCard is called with a TicketStock, a ticket count of 2, valid details and no referral code
- **THEN** the request passes the boundary and ResaleEntryUseCase.AuthorizeCard runs

### Requirement: Every resale entry call is made by the signed-in fan

Every resale entry call (AuthorizeCard, Confirm, List and Withdraw) SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByProviderUserID), failing with NotFound when the caller has no stored account, and pass that User to ResaleEntryUseCase.AuthorizeCard, Confirm, List or Withdraw; the request never names a user. AuthorizeCard SHALL return the card authorization's id and secret, Confirm the entry it makes, List the fan's entries, and Withdraw the withdrawn entry. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Guest
- **WHEN** a caller who is not signed in calls List
- **THEN** it fails with Unauthenticated

#### Scenario: Signed-in fan
- **WHEN** a signed-in fan calls List
- **THEN** ResaleEntryUseCase.List runs for that fan and their entries are returned

#### Scenario: Fan withdraws an entry
- **WHEN** a signed-in fan calls Withdraw for one of their entries
- **THEN** ResaleEntryUseCase.Withdraw runs for that fan and the Withdrawn entry is returned
