## MODIFIED Requirements

### Requirement: Artist List Row

Each artist row in the My Artists list view SHALL display the artist's name and an inline hype dot slider on the same row.

#### Scenario: Artist row layout

- **WHEN** an artist row is rendered in list view
- **THEN** the row SHALL display the artist name (left) and inline dot slider (right) on the same horizontal line
- **AND** the artist name SHALL truncate with ellipsis if it exceeds available space
- **AND** the row SHALL have a minimum height of 44px

#### Scenario: Hype slider replaces passion icon

- **WHEN** the My Artists list view renders
- **THEN** the system SHALL display the inline dot slider (from `hype-inline-slider` capability) instead of the passion level icon
- **AND** the bottom sheet selector SHALL NOT be used for hype changes in list view

## REMOVED Requirements

### Requirement: Tapping passion icon opens selector

**Reason**: Replaced by inline dot slider that enables 1-tap hype changes directly in the list row. The bottom sheet selector required 2 taps and interrupted the scanning flow.
**Migration**: Remove bottom sheet component usage from My Artists list view. Hype changes are handled by the inline dot slider component. The bottom sheet MAY be retained for Grid (Festival) view's long-press context menu.

### Requirement: Selecting a passion level

**Reason**: The bottom sheet selection flow is replaced by inline dot slider interaction. Optimistic update and RPC call behavior moves to the slider component.
**Migration**: Optimistic update and SetHype RPC logic moves to the `hype-inline-slider` component's authenticated tap handler.
