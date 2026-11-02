## ADDED Requirements

### Requirement: Publish returns the published series

After a successful publish, Publish SHALL return the Series with its Events and performers.

#### Scenario: Published series returned

- **WHEN** the owner publishes the one DRAFT Event of a Series
- **THEN** Publish returns the Series with that Event PUBLISHED and its performers

## REMOVED Requirements

### Requirement: Public series announces new events per performer
**Reason**: Series.PublishEvents announces the new concerts of a PUBLIC Series, once per performer, together with the publish (components/entity/series/publish-events), so Publish no longer announces.
**Migration**: Followers are told through the announcement of Series.PublishEvents, with the same rule: only Events added by this publish, none for claimed Events or an UNLISTED Series. A failure to announce now fails the publish and leaves every Event DRAFT, so the member can publish again.

### Requirement: Publish is always reported
**Reason**: The publish report has no receiver. A publish that adds no Event changes nothing, so it announces nothing. The return value moves to "Publish returns the published series".
**Migration**: None. The new concerts of a PUBLIC Series are still announced by Series.PublishEvents.
