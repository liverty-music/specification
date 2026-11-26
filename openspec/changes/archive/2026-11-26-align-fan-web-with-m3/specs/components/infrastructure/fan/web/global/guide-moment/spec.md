## ADDED Requirements

### Requirement: The guide line fades in and out

The guide line SHALL fade in when it opens and fade out when it closes, over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. Under reduced motion it fades over at most 100 ms.

#### Scenario: The guide line closes with a fade

- **WHEN** the guide line is showing and its moment ends
- **THEN** the line fades out over 200 ms and is then no longer rendered

### Requirement: The line stays on screen at an edge

When the guide line's target is near the left or right edge of the screen, the line SHALL stay inside the screen with at least 8 px to either edge (M3 tooltips keep 8 dp from the screen's edges).

#### Scenario: The line stays on screen at an edge

- **WHEN** the guide line points at a target at the end of a 320 px phone's row
- **THEN** the line is at least 8 px from both edges of the screen
