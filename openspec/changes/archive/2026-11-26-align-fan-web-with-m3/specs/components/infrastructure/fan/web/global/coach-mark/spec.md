## ADDED Requirements

### Requirement: The coach mark fades in and out

The coach mark's dim layer, spotlight and tip SHALL fade in together when it appears and fade out together when it goes, over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. The overlay SHALL stay in the DOM while it fades out, inert and without taking a tap, and SHALL stop being rendered when the fade ends. The target keeps its anchor until then, so the spotlight keeps its cut-out while it fades. Under reduced motion the overlay fades in and out over at most 100 ms.

#### Scenario: A tap outside dismisses the coach mark with a fade

- **WHEN** the coach mark is showing and the fan taps outside it
- **THEN** the overlay is inert at once and fades out over 200 ms, with the spotlight's cut-out still around the target
- **AND** the overlay is not rendered once the fade ends

### Requirement: Escape closes the coach mark

While the coach mark is shown, pressing Escape SHALL close it as a tap outside it does (the dismissal is reported, and the overlay goes), so a keyboard or switch user, who has no tap outside, can close it.

#### Scenario: Escape closes the coach mark

- **WHEN** the coach mark is shown and the fan presses Escape
- **THEN** the coach mark closes and its dismissal is reported

### Requirement: The tip stays on screen at an edge

When the coach mark's target is at the left or right edge of the screen, its tip SHALL stay inside the screen with at least 8 px to either edge (M3 tooltips keep 8 dp from the screen's edges), instead of touching or running past the edge.

#### Scenario: The tip stays on screen at an edge

- **WHEN** the coach mark points at a target at the left or the right edge of a 320 px phone
- **THEN** its tip is at least 8 px from both edges of the screen

### Requirement: A screen reader reads the tip at the target

While the coach mark is shown, its target SHALL name the tip's text as its accessible description, so a screen reader reads the tip when it reaches the target (the tooltip pattern); any description the target had stays, and the tip's is taken away when the coach mark has gone.

#### Scenario: A screen reader reads the tip at the target

- **WHEN** the coach mark is shown and a screen reader reaches its target
- **THEN** the target's description is the tip's text
