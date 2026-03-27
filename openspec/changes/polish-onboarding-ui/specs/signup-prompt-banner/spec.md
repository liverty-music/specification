## MODIFIED Requirements

### Requirement: Shared Banner Component

The signup prompt banner SHALL be implemented as a shared component reusable across pages.

#### Scenario: Component renders consistently

- **WHEN** the signup-prompt-banner component is used on different pages
- **THEN** the visual style SHALL be consistent (same padding, typography, button style)
- **AND** the component SHALL accept a `message` attribute for page-specific copy
- **AND** the component SHALL be fixed-positioned above the bottom navigation bar

#### Scenario: Banner uses vertical stacked layout

- **WHEN** the signup-prompt-banner is rendered on a mobile viewport
- **THEN** the banner layout SHALL be vertical (column direction): message text on top, CTA button below
- **AND** the message text SHALL use the full available width
- **AND** the CTA button SHALL be content-width (not full-width), centered below the message text
- **AND** the dismiss button (×) SHALL be positioned at the top-right corner of the banner

#### Scenario: Banner has frosted glass background

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the banner background SHALL use a frosted glass surface (dark base at 85% opacity with backdrop blur)
- **AND** the top border SHALL display a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`
