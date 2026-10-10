# Spec Delta

## REMOVED Requirements

### Requirement: Get returns the link
**Reason**: The venue door's vocabulary is renamed: ReceptionLink becomes Scanner (one device's right to admit fans to one event, with its link token as a field), the reception window becomes the admission window, and the reception screens become the scanner screens. The rule itself is unchanged.
**Migration**: The same rule continues in `components/entity/scanner/get`; stored data moves with this change's rename migration.
