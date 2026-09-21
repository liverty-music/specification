## ADDED Requirements

### Requirement: Entity directory structure
The frontend SHALL have a `src/entities/` directory containing domain type definitions. Each file SHALL be named to match the corresponding Go backend entity file in `internal/entity/`.

#### Scenario: Entity files exist with Go-aligned names
- **WHEN** a developer looks for the frontend equivalent of a Go entity type
- **THEN** they find it at `src/entities/{same_filename}.ts` (e.g., `artist.go` → `artist.ts`, `follow.go` → `follow.ts`, `concert.go` → `concert.ts`)

### Requirement: Grid view removal
The My Artists route SHALL display artists in list view only. The grid toggle button, grid layout, context menu dialog, and all grid-specific interaction handlers SHALL be removed.

#### Scenario: My Artists page loads
- **WHEN** a user navigates to My Artists
- **THEN** artists are displayed in list view with no toggle button to switch views

#### Scenario: No grid-related CSS
- **WHEN** the My Artists stylesheet is loaded
- **THEN** it SHALL NOT contain `.artist-grid`, `.grid-tile`, or related grid layout rules
