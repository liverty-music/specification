## MODIFIED Requirements

### Requirement: Container Queries for component-level responsive design
Components that render in variable-width containers SHALL use CSS Container Queries instead of viewport-based media queries for layout adaptation. Containers that host variable-content children SHALL declare `container-type: inline-size` to enable descendant `@container` rules.

#### Scenario: Event card adapts to lane width
- **WHEN** an `event-card` renders inside a `live-highway` lane
- **THEN** the lane element SHALL declare `container-type: inline-size`
- **AND** the card layout SHALL adapt using `@container` rules based on the lane's available width

#### Scenario: Container query fallback
- **WHEN** a browser does not support Container Queries
- **THEN** the component SHALL fall back to a reasonable default layout
- **AND** the `@supports (container-type: inline-size)` feature query SHALL gate container-specific rules

#### Scenario: Discover search results container
- **WHEN** the discover page displays search results
- **THEN** the `.search-results` element SHALL declare `container-type: inline-size`
- **AND** child components SHALL be able to use `@container` rules for layout adaptation

#### Scenario: Discover bubble area container
- **WHEN** the discover page displays the bubble UI
- **THEN** the `.bubble-area` element SHALL declare `container-type: inline-size`
- **AND** overlay elements within the bubble area SHALL be able to use `@container` rules for responsive positioning

## ADDED Requirements

### Requirement: CSS Grid and Subgrid for page-level layouts
Route-level page layouts SHALL use CSS Grid with explicit row/column tracks instead of flexbox column layouts. Nested list components with aligned columns SHALL use CSS Subgrid.

#### Scenario: Discover page uses grid row tracks
- **WHEN** the discover page renders its layout
- **THEN** `.discover-layout` SHALL use `display: grid` with explicit `grid-template-rows`
- **AND** the search bar and genre chips SHALL occupy `auto`-sized rows
- **AND** the bubble area or search results SHALL occupy the remaining `1fr` row
- **AND** `flex-shrink: 0` SHALL NOT be used on any grid child

#### Scenario: Search result items use subgrid for column alignment
- **WHEN** search results are displayed as a list
- **THEN** `.results-list` SHALL use `display: grid` with `grid-template-columns` defining avatar, name, and action column tracks
- **AND** each `.result-item` SHALL use `display: grid; grid-template-columns: subgrid` spanning all columns
- **AND** avatar widths and action button widths SHALL align across all result items without per-item sizing

#### Scenario: Loading sequence page uses grid centering
- **WHEN** the loading sequence page renders
- **THEN** `.loading-layout` SHALL use `display: grid` with `place-items: center`
- **AND** `flex-direction: column`, `align-items: center`, and `justify-content: center` SHALL NOT be used
