# Spec Delta

## REMOVED Requirements

### Requirement: GetByZitadelOrgID returns the Organizer linked to the tenant

**Reason**: OrganizerUseCase.GetByZitadelOrgID has no caller left. Every organizer-facing boundary now resolves the caller's own Organizer, and its status, through OrganizerUseCase.ResolveCaller, and the method is deleted from the usecase interface.

**Migration**: Callers use OrganizerUseCase.ResolveCaller. The entity operation Organizer.GetByZitadelOrgID is unchanged and is what ResolveCaller reads.
