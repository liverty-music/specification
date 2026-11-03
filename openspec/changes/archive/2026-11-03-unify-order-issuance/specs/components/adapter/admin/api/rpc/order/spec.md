## MODIFIED Requirements

### Requirement: Admins read an order with its settlement

Get SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; both checks come before anything is read. Get SHALL fail with InvalidArgument when no Order is given, and with NotFound when the Order does not exist. Otherwise it SHALL run OrderUseCase.GetWithSettlement and return the Order together with its Settlement and the Settlement's splits, or the Order alone when it was never paid (Pending or Void). Errors from the usecase SHALL be returned unchanged.

#### Scenario: Paid order of a first-party concert

- **WHEN** an admin calls Get for a Paid Order whose payout is Held
- **THEN** the Order is returned with its Held Settlement and its splits

#### Scenario: Order without a settlement

- **WHEN** an admin calls Get for a Void Order
- **THEN** the Order is returned without a Settlement

#### Scenario: Unknown order

- **WHEN** an admin calls Get for an Order that does not exist
- **THEN** it fails with NotFound

#### Scenario: Non-admin reads an order

- **WHEN** a signed-in caller without the admin role calls Get
- **THEN** the call fails with PermissionDenied and nothing is returned

#### Scenario: Paid order without its settlement

- **WHEN** an admin calls Get for a Paid Order whose Settlement cannot be read
- **THEN** it fails with Internal
