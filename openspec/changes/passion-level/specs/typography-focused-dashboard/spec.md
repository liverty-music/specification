# Typography-Focused Dashboard (Delta)

## New Requirements

### Requirement: Visual Mutation UI for Must Go Artists
The system SHALL render expanded, visually striking cards for Must Go (🔥🔥) artists when their events appear in Lane 2 or Lane 3.

#### Scenario: Mutation card rendering in Lane 2
- **WHEN** a Must Go artist has an event in the user's region (Lane 2)
- **THEN** the card SHALL expand to Lane 1 card height (or larger)
- **AND** the card SHALL use a vivid accent color or stripe pattern background
- **AND** the artist name SHALL use extra-bold, mega-typography style
- **AND** a "🔥 遠征チャンス (Must Go)" badge SHALL appear at the top of the card

#### Scenario: Mutation card rendering in Lane 3
- **WHEN** a Must Go artist has an event outside the user's region (Lane 3)
- **THEN** the same Visual Mutation rendering rules as Lane 2 SHALL apply
- **AND** the card SHALL break out of the compact text-only format normally used in Lane 3

#### Scenario: Non-Must Go artists unaffected
- **WHEN** an artist has Local Only (🔥) or Keep an Eye (👀) passion level
- **THEN** their event cards SHALL render using the standard lane-specific format
- **AND** no Visual Mutation SHALL be applied

#### Scenario: Multiple mutated cards on same date
- **WHEN** multiple Must Go artists have events on the same date in Lane 2 or Lane 3
- **THEN** each SHALL render as a mutated card independently
- **AND** the lane layout SHALL accommodate multiple expanded cards without horizontal overflow
