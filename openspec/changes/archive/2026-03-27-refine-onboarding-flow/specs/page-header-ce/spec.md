## ADDED Requirements

### Requirement: All routes using page-header SHALL define grid-template-areas

Every route that renders `<page-header>` SHALL define `grid-template-areas` including a `"header"` area in its route-level CSS, so that the page-header's `grid-area: header` declaration resolves correctly.

#### Scenario: Dashboard route defines header grid area

- **WHEN** the dashboard-route renders `<page-header>`
- **THEN** the dashboard-route CSS SHALL include `grid-template-areas: "header" "content"`
- **AND** the page-header SHALL stretch to fill the full width of the grid container
- **AND** content elements (concert-highway, loading, error, empty) SHALL be placed in the `"content"` area

#### Scenario: Page header width matches viewport

- **WHEN** the dashboard is rendered on any viewport width
- **THEN** the page-header inner `<header>` element SHALL have the same inline-size as the grid container
- **AND** the header SHALL NOT shrink to fit its content width
