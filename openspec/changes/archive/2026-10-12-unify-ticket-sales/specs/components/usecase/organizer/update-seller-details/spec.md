# Spec Delta

## REMOVED Requirements

### Requirement: Admin records the seller details
**Reason**: The seller details become plain Organizer fields, and a one-attribute-group write is named Set (RPC naming rule).
**Migration**: The behavior continues in `components/usecase/organizer/set-business-details`, called by the admin `OrganizerService.SetBusinessDetails`.
