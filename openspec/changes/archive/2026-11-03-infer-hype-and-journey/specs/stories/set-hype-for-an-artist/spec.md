## MODIFIED Requirements

### Requirement: The hype level decides highlights and pushes

A concert of the artist SHALL be highlighted on the Dashboard exactly when the fan's hype level matches the concert (Home matches home-area concerts, Nearby matches home-area and nearby ones, Away matches all, Watch matches none), and a newly added concert SHALL reach the fan by push under the same matching, as the story stories/get-notified-of-new-concerts describes.

#### Scenario: Raising the level to Away

- **WHEN** a signed-in fan with home JP-13 raises an artist from Home to Away and the artist has a concert in JP-40
- **THEN** the JP-40 concert is highlighted on the Dashboard, and a concert added later in JP-40 reaches the fan by push

#### Scenario: Watch

- **WHEN** a fan sets an artist to Watch
- **THEN** the artist's concerts still appear on the Dashboard, none is highlighted, and no push is sent for new ones

## ADDED Requirements

### Requirement: The app never changes a hype level the fan set

The app SHALL raise a hype level only when the fan did not set it, and SHALL never lower one; once the fan picks a level on My Artists, or undoes a raise, that level SHALL stay until the fan changes it. A guest's picked level SHALL count as the fan's own choice after sign-up.

#### Scenario: Picked level survives a distant journey

- **WHEN** a signed-in fan sets an artist to Home on My Artists and later saves Paid for the artist's concert in the away lane
- **THEN** My Artists still shows the artist at Home

#### Scenario: Undone raise stays

- **WHEN** the app raised an artist to Away after the fan's Applied and the fan pressed 「取り消す」
- **THEN** a later Applied for another distant concert of the artist leaves it at Nearby
