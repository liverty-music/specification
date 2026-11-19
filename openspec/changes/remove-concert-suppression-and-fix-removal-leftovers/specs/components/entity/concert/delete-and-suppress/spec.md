## REMOVED Requirements

### Requirement: Delete is idempotent
**Reason**: Concert.DeleteAndSuppress is replaced by Concert.Delete, which removes the same records without suppressing the slot.
**Migration**: See components/entity/concert/delete, requirement "Delete is idempotent".

### Requirement: Paid records and purchases in progress block the delete
**Reason**: Concert.DeleteAndSuppress is replaced by Concert.Delete, which has the same refusals.
**Migration**: See components/entity/concert/delete, requirement "Paid records and purchases in progress block the delete".

### Requirement: Delete and suppress an event with its records
**Reason**: Concert.DeleteAndSuppress is replaced by Concert.Delete, which removes the same records and records no SuppressedConcert.
**Migration**: See components/entity/concert/delete, requirement "Delete an event with its records".
