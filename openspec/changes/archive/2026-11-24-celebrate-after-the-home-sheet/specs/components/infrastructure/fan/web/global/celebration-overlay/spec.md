# Delta for celebration-overlay

## ADDED Requirements

### Requirement: The celebration opens once no sheet is on screen

The system SHALL open a celebration overlay only when no bottom sheet is on screen, so that its animation is seen. When the Timetable becomes real while a sheet is still open (the home-area sheet closes only after the fan's choice is saved, and the Timetable loads behind it), the system SHALL wait until the last sheet has closed and then decide whether to celebrate and whether the onboarding completion latch applies, in that order. When the fan leaves the Timetable first, the system SHALL decide nothing.

#### Scenario: Celebration plays after the home-area sheet closes

- **WHEN** a guest in onboarding who follows 3 artists chooses a home area in the home-area sheet on arrival at the Timetable, and the Timetable's data loads while the sheet is still closing
- **THEN** the celebration overlay is not active while the sheet is on screen
- **AND** the overlay opens, with its entrance animation, once the sheet has closed
