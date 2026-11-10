## ADDED Requirements

### Requirement: Share token stored with the publish

PublishEvents SHALL take an optional share token. When one is given, PublishEvents SHALL make it the Series' share token together with the publish: both are stored or neither is. A share token SHALL be given only for an UNLISTED Series that has no share token yet: PublishEvents SHALL fail with FailedPrecondition, changing nothing, when the Series is not UNLISTED or already has one, and with AlreadyExists, changing nothing, when another Series holds the given token. When PublishEvents fails for any reason, the Series SHALL keep the share token it had before.

#### Scenario: Token stored with the first publish

- **WHEN** PublishEvents is given a DRAFT Event of an UNLISTED Series without a share token, and the token T
- **THEN** the Event is PUBLISHED and T opens the Series

#### Scenario: Blocked publish stores no token

- **WHEN** PublishEvents is given the token T for an UNLISTED Series without a share token and a given Event's slot is held by a CANCELLED Event
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT and the Series has no share token

#### Scenario: Token for a public series

- **WHEN** PublishEvents is given a share token for a PUBLIC Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Series already has a token

- **WHEN** PublishEvents is given a share token for an UNLISTED Series that already has the token T1
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT and T1 still opens the Series

#### Scenario: Token held by another series

- **WHEN** PublishEvents is given a share token that another Series holds
- **THEN** PublishEvents fails with AlreadyExists, every given Event stays DRAFT and the Series has no share token
