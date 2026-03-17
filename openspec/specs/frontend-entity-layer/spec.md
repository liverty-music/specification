## ADDED Requirements

### Requirement: Entity directory structure
The frontend SHALL have a `src/entities/` directory containing domain type definitions. Each file SHALL be named to match the corresponding Go backend entity file in `internal/entity/`.

#### Scenario: Entity files exist with Go-aligned names
- **WHEN** a developer looks for the frontend equivalent of a Go entity type
- **THEN** they find it at `src/entities/{same_filename}.ts` (e.g., `artist.go` → `artist.ts`, `follow.go` → `follow.ts`, `concert.go` → `concert.ts`)

### Requirement: Artist entity
The `src/entities/artist.ts` file SHALL export an `Artist` interface with fields: `id` (string), `name` (string), `mbid` (string), `fanart` (optional `Fanart`). The `Fanart` interface SHALL export fields for image URLs: `artistThumb`, `artistBackground`, `hdMusicLogo`, `musicLogo`, `musicBanner` (all optional strings).

#### Scenario: Artist with full fanart
- **WHEN** a service maps a proto `Artist` message that has all fanart fields populated
- **THEN** the resulting `Artist` entity SHALL have a `fanart` object with all URL strings set

#### Scenario: Artist without fanart
- **WHEN** a service maps a proto `Artist` message with no fanart
- **THEN** the resulting `Artist` entity SHALL have `fanart` as `undefined`

### Requirement: FollowedArtist entity
The `src/entities/follow.ts` file SHALL export a `FollowedArtist` interface with flattened artist fields (`id`, `name`) and a `Hype` value. The `Hype` type SHALL be a string union aligned with Go's `Hype` constants: `'watch'`, `'home'`, `'nearby'`, `'away'`. Optional fanart URLs (`logoUrl`, `backgroundUrl`) SHALL be included for UI consumption.

#### Scenario: FollowedArtist from ListFollowed RPC
- **WHEN** the follow service client receives a ListFollowed response
- **THEN** it SHALL map each proto `FollowedArtist` to an entity `FollowedArtist` with flattened artist fields and a string `Hype` value

### Requirement: Concert entity
The `src/entities/concert.ts` file SHALL export a `Concert` interface (replacing the former `LiveEvent` interface) with the same fields. It SHALL also export `DateGroup`, `HypeLevel`, and `LaneType` types.

#### Scenario: Backward compatibility via re-export
- **WHEN** existing components import `LiveEvent` from the old path (`components/live-highway/live-event.ts`)
- **THEN** they SHALL receive the `Concert` type via a re-export alias (`export type { Concert as LiveEvent }`)

#### Scenario: Concert type used in templates
- **WHEN** a template iterates over concerts
- **THEN** the bound properties SHALL match the `Concert` interface fields

### Requirement: Single mapping point
Proto-to-entity mapping SHALL occur exclusively in service client classes. No route, component, or other consumer SHALL directly access proto wrapper types (e.g., `ArtistId.value`, `Url.value`).

#### Scenario: Service returns entity types
- **WHEN** `FollowServiceClient.listFollowed()` is called
- **THEN** it SHALL return `FollowedArtist[]` (entity type), not proto classes or intermediate interfaces

#### Scenario: Dashboard service uses entity types
- **WHEN** `DashboardService` builds `DateGroup[]`
- **THEN** it SHALL consume `FollowedArtist` entities from the follow service, not define its own inline type

### Requirement: Grid view removal
The My Artists route SHALL display artists in list view only. The grid toggle button, grid layout, context menu dialog, and all grid-specific interaction handlers SHALL be removed.

#### Scenario: My Artists page loads
- **WHEN** a user navigates to My Artists
- **THEN** artists are displayed in list view with no toggle button to switch views

#### Scenario: No grid-related CSS
- **WHEN** the My Artists stylesheet is loaded
- **THEN** it SHALL NOT contain `.artist-grid`, `.grid-tile`, or related grid layout rules
