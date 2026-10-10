# Spec Delta

## REMOVED Requirements

### Requirement: Replace the draft whole

**Reason**: Series.UpdateDraft is replaced by Series.Update, which also corrects a Series that has published Events.
**Migration**: Use `components/entity/series/update`.

### Requirement: Only a draft can be updated

**Reason**: A Series with PUBLISHED Events can now be corrected; what may change is stated in the Series and Event specs ("What can change after publish").
**Migration**: Use `components/entity/series/update`.
