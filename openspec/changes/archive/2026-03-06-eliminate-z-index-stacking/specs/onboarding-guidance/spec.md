### Requirement: No z-index stacking in discovery page CSS

The discovery page SHALL NOT use `z-index` for visual stacking. All layer ordering SHALL be achieved through DOM source order.

#### Scenario: Overlay elements paint above canvas
- **WHEN** the discovery page renders
- **THEN** the onboarding HUD, orb label, and complete button SHALL paint above the canvas
- **AND** no CSS `z-index` property SHALL be present in the discovery page CSS

#### Scenario: Starfield pseudo-element paints behind content
- **WHEN** the discovery page renders
- **THEN** the `.container::before` starfield SHALL paint behind all content elements
- **AND** the starfield SHALL use `pointer-events: none` without `z-index`

#### Scenario: Search bar and genre chips paint above canvas
- **WHEN** the discovery page renders
- **THEN** the search bar and genre filter chips SHALL paint above the bubble canvas area
- **AND** stacking SHALL be achieved via DOM source order (search bar and genre chips appear after the canvas in DOM), not `z-index`

#### Scenario: Search results paint above bubble area
- **WHEN** the user enters a search query and results are displayed
- **THEN** the search results list SHALL paint above the bubble area
- **AND** stacking SHALL be achieved via DOM source order, not `z-index`
