# Spec Delta

## REMOVED Requirements

### Requirement: Read a captured payment
**Reason**: The captured payment is the outcome of a card authorization, not an operation of the Order: the card authorization is now its own entity, and reading a Captured one gives the amount and card details an Order records.
**Migration**: Read the purchase's card authorization with `components/entity/card-authorization/get`; a card authorization that is not Captured returns no captured payment, where this operation failed with FailedPrecondition.
