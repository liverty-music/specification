# LotteryUseCase.Apply

## Purpose

LotteryUseCase.Apply records a fan's TicketApplication to an open LotterySalesPhase after checking the requested count, the applicant's 本人確認 (identity check), the phase's verification requirement, that the fan has no active application, and that the fan's hold matches the amount.

## Requirements

### Requirement: Apply with an authenticated hold

Apply SHALL take a phase, the calling fan as applicant, a requested ticket count, the applicant's full name and phone number, and the reference of a hold opened by CreateAuthorization. In this order it SHALL: read the phase with LotterySalesPhase.Get, failing with NotFound when it does not exist; fail with InvalidArgument when the count breaks the TicketApplication count rule; fail with InvalidArgument when the name or phone is missing; fail with FailedPrecondition when the window is not open at the current time; apply the verification gate; fail with FailedPrecondition when TicketApplication.GetByPhaseAndApplicant finds an active application of the fan for the phase; and verify the hold with TicketApplication.VerifyAuthorization for the phase's amount for the count, returning its failure unchanged. It SHALL then store the application with TicketApplication.Create and return it. No money is captured at application.

#### Scenario: Fan applies within the window

- **WHEN** a fan with no active application applies for 2 tickets on an open phase with an authenticated 16000 yen hold, giving a name and a phone number
- **THEN** a TicketApplication is stored in state Applied with the hold's reference, and nothing is charged

#### Scenario: Window closed

- **WHEN** the fan applies at or after the close time
- **THEN** Apply fails with FailedPrecondition and stores nothing

#### Scenario: Count over the limit

- **WHEN** the fan requests more tickets than the phase allows per application
- **THEN** Apply fails with InvalidArgument

#### Scenario: Missing identity

- **WHEN** the full name or the phone number is empty
- **THEN** Apply fails with InvalidArgument

#### Scenario: Second application

- **WHEN** the fan already has an Applied, Won or Lost application for the phase
- **THEN** Apply fails with FailedPrecondition and stores nothing

#### Scenario: Hold does not verify

- **WHEN** TicketApplication.VerifyAuthorization fails, for example because the card is American Express or the amount differs
- **THEN** Apply fails with the same error and stores nothing

#### Scenario: Re-application after withdrawal

- **WHEN** the fan's only earlier application for the phase is Withdrawn and the window is open
- **THEN** Apply stores a new application

### Requirement: Verification gate

When the phase requires verification, Apply SHALL require the applicant to hold a verified identity whose status is Active, read with VerifiedIdentity.GetByUserID, and SHALL fail with FailedPrecondition otherwise. When the phase's requirement is None, no verified identity is needed.

#### Scenario: No verified identity

- **WHEN** the phase requires JPKI-only and the fan has never verified
- **THEN** Apply fails with FailedPrecondition and stores nothing

#### Scenario: Verification not active

- **WHEN** the phase requires verification and the fan's verified identity needs re-verification
- **THEN** Apply fails with FailedPrecondition

#### Scenario: Active verification

- **WHEN** the phase requires verification and the fan's verified identity is Active
- **THEN** Apply continues with the other checks
