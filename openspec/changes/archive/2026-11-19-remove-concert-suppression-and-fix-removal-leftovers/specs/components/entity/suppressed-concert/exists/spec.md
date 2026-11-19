## REMOVED Requirements

### Requirement: Slot lookup
**Reason**: An admin deletes a Concert only to clean up test data of Artists that an Organizer represents, and discovery never searches those Artists, so suppression protected nothing; a suppressed slot could hide a real concert at the same Venue and date.
**Migration**: The stored suppression records are dropped. Discovery handles every slot like any new discovery.
