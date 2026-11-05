# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: A completed card authentication confirms the lottery entry`
- TO: `### Requirement: A completed card authentication confirms the entry`

## MODIFIED Requirements

### Requirement: A completed card authentication confirms the entry

On a notice that a card authorization became Authorized, the endpoint SHALL find the card authorization with CardAuthorization.GetByProviderCardAuthorizationID using the notice's provider card authorization ID, then call LotteryEntryUseCase.Confirm when it pays for a lottery entry, or ResaleEntryUseCase.Confirm when it pays for a resale entry, with that card authorization and no calling fan. A notice for a card authorization that pays for a Checkout, or that no CardAuthorization has (NotFound: the platform did not open it), SHALL be acknowledged without effect. A rejection by Confirm (PermissionDenied, FailedPrecondition, InvalidArgument, AlreadyExists) SHALL be acknowledged, since Confirm has already released what it rejected; any other failure, of the lookup or of Confirm, SHALL be answered with Internal, so the provider delivers the notice again.

#### Scenario: Fan closed the browser

- **WHEN** a notice reports a fan's lottery card authorization Authorized and the fan never called Confirm
- **THEN** LotteryEntryUseCase.Confirm runs and the entry is made

#### Scenario: Resale application, browser closed

- **WHEN** a notice reports a fan's resale card authorization Authorized and the fan never called Confirm
- **THEN** ResaleEntryUseCase.Confirm runs and the resale entry is made

#### Scenario: Entry already made

- **WHEN** the notice arrives after the fan's Confirm made the entry
- **THEN** it is acknowledged and nothing changes

#### Scenario: Card authorization the platform did not open

- **WHEN** a notice names a provider card authorization ID that no CardAuthorization has
- **THEN** it is acknowledged and nothing changes

#### Scenario: Payment provider unreachable

- **WHEN** Confirm fails with Unavailable
- **THEN** the endpoint answers with Internal and a redelivery handles the notice again
