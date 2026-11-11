## MODIFIED Requirements

### Requirement: Unlisted series gets a share token

When the Series is UNLISTED and has no share token yet, Publish SHALL give it a new random share token together with the publish (Series.PublishEvents with that token). A Series that already has a share token SHALL keep it, and Publish SHALL give it no new token. When the publish fails, the Series SHALL have no share token, so a repeated Publish gives it one together with its Events.

#### Scenario: Unlisted publish
- **WHEN** an UNLISTED draft is published
- **THEN** the Series has a PUBLISHED Event and a share token and appears on no fan list

#### Scenario: New date keeps the share link
- **WHEN** a new date of an UNLISTED Series that already has a share token is published
- **THEN** the share token is unchanged

#### Scenario: Failed publish leaves no token
- **WHEN** Publish of an UNLISTED draft fails because Series.PublishEvents fails
- **THEN** every Event stays DRAFT and the Series has no share token

#### Scenario: Repeated publish after a failure
- **WHEN** Publish of an UNLISTED draft failed once and the owner publishes it again
- **THEN** the Series has a PUBLISHED Event and a share token
