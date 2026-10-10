# Spec Delta

## REMOVED Requirements

### Requirement: Only the owner

**Reason**: ConcertAuthoringUseCase.UpdateDraft is replaced by ConcertAuthoringUseCase.Update, which also corrects a concert that has published Events.
**Migration**: The same owner rule is in `components/usecase/series/update`, "Only the owner".

### Requirement: Only a draft

**Reason**: A published concert can now be corrected within what the Series and Event specs fix after publish.
**Migration**: `components/usecase/series/update`, "Corrections keep what publish fixed".

### Requirement: Same validation as a new draft

**Reason**: Replaced together with UpdateDraft.
**Migration**: `components/usecase/series/update`, "Same validation as a new draft".

### Requirement: Content replaced

**Reason**: Replaced together with UpdateDraft.
**Migration**: `components/usecase/series/update`, "Edit applied".
