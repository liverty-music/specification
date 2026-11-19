## REMOVED Requirements

### Requirement: Suppressed slot is skipped
**Reason**: Suppression is retired: an admin deletes a Concert only to clean up test data of Artists that discovery never searches, so a deleted slot needs no protection, and a suppressed slot could hide a real concert.
**Migration**: A discovered event at a slot where a Concert was deleted is published or staged like any other.
