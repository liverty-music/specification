## RENAMED Requirements

- FROM: `### Requirement: Concerts the fan's hype level covers are highlighted`
- TO: `### Requirement: Concerts the fan's hype level matches are highlighted`

## MODIFIED Requirements

### Requirement: Concerts the fan's hype level matches are highlighted

A concert card SHALL be highlighted when the fan's hype level for its artist matches the concert, by the lane the concert is in: Home matches the home lane, Nearby the home and nearby lanes, Away every lane, Watch none. Other cards SHALL be shown without the highlight. The hype level does not change which concerts are shown or their order.

#### Scenario: Nearby artist with a distant concert

- **WHEN** the fan follows an artist at Nearby and the artist has one concert in the nearby lane and one in the away lane
- **THEN** the nearby concert's card is highlighted and the away concert's card is not

#### Scenario: Watch artist

- **WHEN** the fan follows an artist at Watch
- **THEN** the artist's concerts are shown and none is highlighted
