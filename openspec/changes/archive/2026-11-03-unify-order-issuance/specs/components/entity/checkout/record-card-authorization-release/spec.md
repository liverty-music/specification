## REMOVED Requirements

### Requirement: Release recorded once
**Reason**: A card authorization is released by its own OrderUseCase.ReleaseCardAuthorization workflow, whose stored state records whether it finished, as for a lottery entry; the Checkout no longer keeps a release time.
**Migration**: The release time column is dropped; the CardAuthorization's status at the payment provider is the fact.
