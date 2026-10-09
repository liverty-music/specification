## Context

See proposal.md. The behavior already ships in liverty-music/backend#565. This change only records it in the specs.

## Decisions

- **No new Organizer status.** Deactivated is the existing terminal status that ReconcileProvisioning ignores, so a permanently failing Organizer is deactivated rather than given a new status. An admin removes it with Delete.
- **The reconciler never deletes.** Create discards on a permanent failure because the admin is still waiting for the result. The background sweep only deactivates, so nothing an admin created disappears without an admin action.
- **The tenant is found by name, not by domain.** The tenant name is `org-<Organizer id>`. The earlier lookup by generated domain fails in prod because the domain carries a suffix.

## Risks / Trade-offs

- Whether the provisioner can read users of other tenants (the instance admin org) has not been verified against prod Zitadel. If it cannot, the early email check passes. ProvisionTenant still reports AlreadyExists, and Create then discards the Organizer and the tenant it created.
