## MODIFIED Requirements

### Requirement: Artist List Row

Each artist row in the My Artists list view SHALL be a horizontal scroll-snap container with the artist content and a dismiss trigger.

#### Scenario: Artist row layout

- **WHEN** an artist row is rendered in list view
- **THEN** the row SHALL be a horizontal scroll container with `scroll-snap-type: x mandatory` and hidden scrollbar
- **AND** the row content SHALL display the artist name (left) and inline dot slider (right) using `grid-template-areas: "name watch home nearby away"`
- **AND** the artist name SHALL truncate with ellipsis if it exceeds available space
- **AND** a dismiss trigger element SHALL be placed after the content as the scroll-snap end target

#### Scenario: Hype track line containing block

- **WHEN** the hype dot track line is rendered as a `::before` pseudo-element
- **THEN** the pseudo-element SHALL be placed on `.hype-col:first-of-type .hype-label::before` (the flex container inside the first hype `<td>`)
- **AND** the pseudo-element SHALL NOT be placed directly on `.hype-col` (`<td>`) because `display: table-cell` elements cannot serve as a containing block for `position: absolute` children in most browsers
- **AND** the containing element (`.hype-label`) SHALL have `position: relative; display: flex` to establish a reliable containing block
- **AND** the track line SHALL use `inline-size: calc(3 * 100%)` to span from the first dot center to the last dot center
- **AND** `pointer-events: none` SHALL be set on the pseudo-element to avoid blocking tap targets

## ADDED Requirements

### Requirement: Unauthenticated user loading guard

The My Artists `loading()` lifecycle hook SHALL skip RPC calls for unauthenticated users since the `ListFollowed` RPC requires an authenticated session.

#### Scenario: Unauthenticated user visits My Artists

- **WHEN** an unauthenticated user navigates to the My Artists page
- **THEN** `loading()` SHALL NOT call `ListFollowed` RPC
- **AND** `loading()` SHALL set `isLoading` to `false` immediately
- **AND** if the user is at onboarding Step `'my-artists'`, the spotlight SHALL still be activated on `[data-artist-rows]`

#### Scenario: Authenticated user visits My Artists

- **WHEN** an authenticated user navigates to the My Artists page
- **THEN** `loading()` SHALL call `ListFollowed` RPC as normal
- **AND** the response SHALL populate the artist list
