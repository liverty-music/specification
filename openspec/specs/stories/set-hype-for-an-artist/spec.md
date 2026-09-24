# Set hype for an artist

## Purpose

A fan tells the app how far they will travel for an artist by choosing a hype level on My Artists; the choice shows at once, is kept across sessions, and decides which of the artist's concerts are highlighted on the Dashboard and which new concerts reach the fan by push.

## Requirements

### Requirement: A signed-in fan's hype level is saved to their account

When a signed-in fan picks a hype level for a followed artist on My Artists, the new level SHALL show at once and FollowUseCase.SetHype SHALL store it on the fan's Follow of the artist. When saving fails twice in a row, My Artists SHALL show the previous level again and tell the fan the change failed.

#### Scenario: Hype level survives a restart

- **WHEN** a signed-in fan sets an artist to Away and reopens the app later
- **THEN** My Artists still shows the artist at Away

#### Scenario: Saving fails

- **WHEN** a signed-in fan sets an artist from Nearby to Home and saving fails on the first try and on the retry
- **THEN** My Artists shows the artist at Nearby again and a message says the change failed

### Requirement: A guest's hype level stays on the device

When a guest picks a hype level, it SHALL be kept on the device only, nothing SHALL be sent to the server, and My Artists SHALL show the signup prompt banner. The level is carried into the account when the guest signs up, as the story stories/merge-guest-data-on-signup describes.

#### Scenario: Guest changes a hype level

- **WHEN** a guest sets a followed artist to Away
- **THEN** My Artists shows Away, no request reaches the server, and the signup prompt banner is shown

### Requirement: The hype level decides highlights and pushes

A concert of the artist SHALL be highlighted on the Dashboard exactly when the fan's hype level covers the concert's lane (Home covers home-area concerts, Nearby covers home-area and nearby ones, Away covers all, Watch covers none), and a newly added concert SHALL reach the fan by push under the same matching, as the story stories/get-notified-of-new-concerts describes.

#### Scenario: Raising the level to Away

- **WHEN** a signed-in fan with home JP-13 raises an artist from Home to Away and the artist has a concert in JP-40
- **THEN** the JP-40 concert is highlighted on the Dashboard, and a concert added later in JP-40 reaches the fan by push

#### Scenario: Watch

- **WHEN** a fan sets an artist to Watch
- **THEN** the artist's concerts still appear on the Dashboard, none is highlighted, and no push is sent for new ones
