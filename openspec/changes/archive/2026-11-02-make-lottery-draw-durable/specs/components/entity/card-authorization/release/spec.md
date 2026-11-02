## MODIFIED Requirements

### Requirement: Release a card authorization

CardAuthorization.Release SHALL give back a Pending or Authorized CardAuthorization without charging and make it Released. Repeating it for the same CardAuthorization, or calling it for one that has lapsed on the card, SHALL succeed without a further effect. It SHALL fail with FailedPrecondition when the CardAuthorization is Captured, with NotFound when no CardAuthorization has the id, and with Unavailable when the payment provider cannot be reached. The outcome SHALL follow the CardAuthorization's status at the call; a failure an earlier call received SHALL never be returned again for a later call.

#### Scenario: Card authorization released
- **WHEN** CardAuthorization.Release is called for an Authorized card authorization
- **THEN** it is Released and nothing is charged

#### Scenario: Repeated release
- **WHEN** CardAuthorization.Release is called again for the same card authorization
- **THEN** it succeeds and nothing changes

#### Scenario: Captured card authorization
- **WHEN** the card authorization has already been captured
- **THEN** CardAuthorization.Release fails with FailedPrecondition and nothing changes

#### Scenario: Unknown id
- **WHEN** no card authorization has the id
- **THEN** CardAuthorization.Release fails with NotFound

#### Scenario: Payment provider error, then recovered
- **WHEN** a release fails with Unavailable because the payment provider answered with a server error and left the card authorization Authorized, and Release is called again 1 minute later while the provider works
- **THEN** it is Released and nothing is charged
