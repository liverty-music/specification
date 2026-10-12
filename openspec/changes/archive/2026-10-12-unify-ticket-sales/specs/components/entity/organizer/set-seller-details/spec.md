# Spec Delta

## REMOVED Requirements

### Requirement: Seller details replaced as a whole
**Reason**: The seller details become plain Organizer fields (legal name, representative name, business address, business phone number, contact email); "seller" is not an entity.
**Migration**: The behavior continues in `components/entity/organizer/set-business-details`; the stored values move to the new fields in this change's migration.
