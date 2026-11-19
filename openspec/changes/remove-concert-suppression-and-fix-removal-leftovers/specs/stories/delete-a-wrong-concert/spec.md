## REMOVED Requirements

### Requirement: A deleted slot stays deleted
**Reason**: An admin deletes a Concert only to clean up test data of Artists that an Organizer represents, and discovery never searches those Artists, so suppression protected nothing; a suppressed slot could hide a real concert at the same Venue and date.
**Migration**: An admin deletes test data through the story remove-a-cancelled-concert and the Organizers screen; a wrong discovered concert is not deleted by an admin.
