## ADDED Requirements

### Requirement: Date rows deal their concerts in as they come into view

When a date row comes into view from either the bottom or the top edge of the timetable, its concert cards SHALL be dealt in: each card flies in from the right and from behind, turning towards the fan in depth, and settles with a slight overshoot. Only the cards SHALL move; the lanes' frames and the mark of an empty lane SHALL stay in place. The cards SHALL be dealt in lane by lane in the order HOME, NEAR, AWAY, and within a lane from the top card down, whichever edge the row comes in from. In a browser that can start an animation when an element comes into view, the animation SHALL start once 60% of the row is in view, SHALL run for 800 ms on each card whatever the scroll speed, and each card SHALL start 100 ms after the card above it in its lane, with each lane starting 100 ms after the lane before it. In a browser that cannot, the same motion SHALL follow the scroll position while the row enters, so its pace follows the scroll; in such a browser a row SHALL also deal out as it leaves through the top edge, once 40% of it has left, so that scrolling back up deals it in from the top. A row that has fully left the view SHALL be dealt in again the next time it comes into view. Under reduced motion the rows SHALL appear in place with no movement.

#### Scenario: Scrolling down

- **WHEN** the fan scrolls down and a row comes in at the bottom edge
- **THEN** its concert cards are dealt in, HOME first, then NEAR, then AWAY
- **AND** in a browser that can start an animation when an element comes into view, the first NEAR card starts 100 ms and the first AWAY card 200 ms after the first HOME card
- **AND** the lanes' frames and an empty lane's mark do not move

#### Scenario: Cards in one lane

- **WHEN** a row comes into view with two concerts in its HOME lane, in a browser that can start an animation when an element comes into view
- **THEN** the lower card starts 100 ms after the upper one

#### Scenario: Scrolling up after a month jump

- **WHEN** the fan has jumped to a month and scrolls up, and a row comes in at the top edge
- **THEN** its cards are dealt in the same way, each lane from the top card down

#### Scenario: Fast scroll

- **WHEN** the fan flings the timetable so that a row crosses into view within 100 ms, in a browser that can start an animation when an element comes into view
- **THEN** the row's deal-in still runs for 800 ms after it starts

#### Scenario: A row comes back

- **WHEN** a row has been dealt in, the fan scrolls it fully out of view, then back
- **THEN** it is dealt in again

#### Scenario: Leaving through the top without entry-triggered animations

- **WHEN** in a browser that cannot start an animation when an element comes into view, the fan scrolls down until 40% of a row has left through the top edge, then scrolls back up
- **THEN** the row's cards deal out while it continues to leave, and deal in again as it comes back from the top

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion
- **THEN** rows appear in place with no movement or delay
