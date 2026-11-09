## ADDED Requirements

### Requirement: Date rows deal their concerts in as they come into view

When a date row comes into view from either the bottom or the top edge of the timetable, its three lanes SHALL be dealt in: each lane's content flies in from the right and from behind, turning towards the fan in depth, and settles with a slight overshoot. The HOME, NEAR and AWAY lanes SHALL be dealt in in that order. In a browser that can start an animation when an element comes into view, the animation SHALL start once 60% of the row is in view, SHALL run for 800 ms whatever the scroll speed, and SHALL start the lanes 100 ms apart. In a browser that cannot, the same motion SHALL follow the scroll position while the row enters, so its pace follows the scroll. A row that has fully left the view SHALL be dealt in again the next time it comes into view. Under reduced motion the rows SHALL appear in place with no movement.

#### Scenario: Scrolling down

- **WHEN** the fan scrolls down and a row comes in at the bottom edge
- **THEN** its lanes are dealt in, HOME first, then NEAR, then AWAY
- **AND** in a browser that can start an animation when an element comes into view, NEAR starts 100 ms and AWAY 200 ms after HOME

#### Scenario: Scrolling up after a month jump

- **WHEN** the fan has jumped to a month and scrolls up, and a row comes in at the top edge
- **THEN** its lanes are dealt in the same way

#### Scenario: Fast scroll

- **WHEN** the fan flings the timetable so that a row crosses into view within 100 ms, in a browser that can start an animation when an element comes into view
- **THEN** the row's deal-in still runs for 800 ms after it starts

#### Scenario: A row comes back

- **WHEN** a row has been dealt in, the fan scrolls it fully out of view, then back
- **THEN** it is dealt in again

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion
- **THEN** rows appear in place with no movement or delay
