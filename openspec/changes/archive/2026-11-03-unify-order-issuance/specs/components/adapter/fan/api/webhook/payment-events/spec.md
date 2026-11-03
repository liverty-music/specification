## MODIFIED Requirements

### Requirement: Other notices are acknowledged

Notices that a charge completed, that a refund was applied, that a payout was reversed, or that the platform's own bank payout succeeded or failed, and notices of any other kind than a dispute or a completed card authentication, SHALL be acknowledged without effect.

#### Scenario: Refund confirmation

- **WHEN** a notice confirms a refund the platform issued
- **THEN** it is acknowledged and nothing changes

#### Scenario: Completed charge

- **WHEN** a notice reports that the charge of a fan's checkout or of a won lottery entry completed
- **THEN** it is acknowledged and nothing changes, because OrderUseCase.Issue already made the Order Paid with Order.Issue, which announced it

## REMOVED Requirements

### Requirement: A completed charge is fulfilled
**Reason**: OrderUseCase.FulfillPayment is removed; OrderUseCase.Issue makes every Order Paid with Order.Issue, which announces it.
**Migration**: The notice falls under "Other notices are acknowledged".
