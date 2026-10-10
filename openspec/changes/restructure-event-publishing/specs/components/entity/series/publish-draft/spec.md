# Spec Delta

## REMOVED Requirements

### Requirement: Draft events become events

**Reason**: Series.PublishDraft is replaced by Series.PublishEvents, which publishes chosen DRAFT Events of a Series, including dates added to a published Series.
**Migration**: Use `components/entity/series/publish-events`; the claim rule is kept there.

### Requirement: Blocked slots fail the whole publish

**Reason**: Replaced together with PublishDraft.
**Migration**: Kept unchanged in `components/entity/series/publish-events`, "Blocked slots fail the whole publish".

### Requirement: Publish completes the draft

**Reason**: The Series no longer has a publish state to set, and there is no separate draft content to remove.
**Migration**: `components/entity/series/publish-events` sets each published Event PUBLISHED and removes the Series' StagedConcerts.
