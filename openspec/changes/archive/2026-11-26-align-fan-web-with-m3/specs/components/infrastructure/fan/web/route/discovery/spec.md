## ADDED Requirements

### Requirement: The search results fade in and out

The search results SHALL fade in when search starts and fade out when it ends, over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. Under reduced motion they fade over at most 100 ms.

#### Scenario: Starting a search

- **WHEN** the fan starts a search
- **THEN** the results list fades in over 200 ms
- **AND** when the search ends it fades out and is then not rendered

### Requirement: The swap tile stays put while the view turns

While the swap tile switches the Discovery view, the tile SHALL stay where it is, as the control that does the switching, and SHALL NOT turn with the body of the view.

#### Scenario: Switching to the Concerts view

- **WHEN** the fan presses the swap tile and the view turns over
- **THEN** the swap tile is not part of the turning view; it keeps its place and size while the old view turns edge-on and the new one turns in

### Requirement: The search bar is 56 px tall

The search bar SHALL be 56 px tall on every phone, the M3 search bar's height (`md.comp.search-bar.container.height`), with its input's 48 px touch target inside it. It SHALL NOT shrink below its input on a small phone.

#### Scenario: The search bar is 56 px tall

- **WHEN** Discovery is shown on a 320 px wide phone
- **THEN** the search bar is 56 px tall
