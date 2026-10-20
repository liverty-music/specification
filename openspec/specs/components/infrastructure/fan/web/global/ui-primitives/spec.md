# UI Primitives

## Purpose

The small shared building blocks every screen uses: the loading spinner, icons, and the placeholder shown for empty, loading and error states.

## Requirements

### Requirement: SVG Icon Component
The system SHALL provide a centralized `<svg-icon>` custom element as the single source of truth for all SVG icon definitions, eliminating inline SVG duplication across templates.

#### Scenario: Icon rendering by name
- **WHEN** `<svg-icon name="home">` is rendered
- **THEN** the component SHALL display the SVG icon matching the given name
- **AND** only the matched icon SHALL be present in the DOM (via Aurelia `switch.bind`)
- **AND** unrecognized names SHALL render nothing (default-case fallback)

#### Scenario: Size variants
- **WHEN** `<svg-icon>` is rendered with a `size` attribute
- **THEN** the host element SHALL set `data-size` to the given value
- **AND** the component SHALL support sizes: xs (0.75rem), sm (1rem), md (1.25rem), lg (1.5rem), xl (2.5rem)
- **AND** the default size SHALL be md when no size is specified

#### Scenario: Icon set coverage
- **WHEN** the icon component is registered
- **THEN** it SHALL include at minimum these icons: home, search, discover, music, my-artists, ticket, tickets, settings, check, alert-triangle, warning, info, x-circle, x, chevron-right, arrow-left, trash, plus, map-pin, calendar, link, clock, globe, bell, lock, qr-code, list, grid

#### Scenario: Color inheritance
- **WHEN** `<svg-icon>` is placed inside a colored container
- **THEN** stroke-based icons SHALL use `stroke="currentColor"` to inherit the parent's text color
- **AND** fill-based icons (warning, x-circle) SHALL use `fill="currentColor"`

---

### Requirement: State Placeholder Component
The system SHALL provide a `<state-placeholder>` custom element for displaying empty, error, and informational states with a consistent centered layout.

#### Scenario: Rendering with icon only
- **WHEN** `<state-placeholder icon="music">` is rendered with slotted content
- **THEN** the component SHALL display an xl-sized svg-icon
- **AND** the slotted content SHALL be projected via `<au-slot>` below the icon
- **AND** the content SHALL be vertically and horizontally centered

#### Scenario: No icon
- **WHEN** `<state-placeholder>` is rendered without an `icon` attribute
- **THEN** no svg-icon SHALL be rendered
- **AND** only the slotted content SHALL be displayed

#### Scenario: Custom content via slot
- **WHEN** child content is placed inside `<state-placeholder>`
- **THEN** the content SHALL be projected via `<au-slot>`
- **AND** this SHALL allow pages to provide titles, descriptions, buttons, links, or `<circular-progress>` elements

### Requirement: Circular Progress Indicator

The system SHALL provide a `<circular-progress>` custom element, shared by the fan app and the organizer console, that shows an indeterminate Material 3 circular progress indicator: an arc that grows, shrinks and rotates on a circular track. It SHALL come in two sizes, 48 px (default) and 24 px for use inside a button, with a 4 px stroke at 48 px and a 3 px stroke at 24 px. The arc SHALL use the `primary` color role of the surrounding app unless the parent sets another color. It SHALL expose `role="progressbar"` with an accessible name that defaults to the localized word for loading and can be set by the page, and SHALL carry no value while indeterminate. Under `prefers-reduced-motion: reduce` it SHALL stop growing and shrinking and rotate at most once every 2 seconds.

#### Scenario: Default rendering

- **WHEN** `<circular-progress>` is rendered without attributes
- **THEN** a 48 px indeterminate circular indicator with a 4 px arc in the `primary` color is shown, exposed as a progressbar named for loading

#### Scenario: Inside a button

- **WHEN** `<circular-progress size="small">` is placed inside a pending button
- **THEN** a 24 px indicator with a 3 px arc in the button's content color is shown, and the button keeps its size

#### Scenario: Reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the arc keeps a fixed length and turns at most once every 2 seconds

#### Scenario: Identity verification in progress

- **WHEN** the fan app's identity verification callback screen waits for the result
- **THEN** it shows `<circular-progress>` with the waiting message

### Requirement: One button style in four variants

Every text button in the fan app SHALL use one shared button style, in one of four variants. All four SHALL share the same corner radius (12px), padding and label weight, so that any text button reads as a button from its shape alone. The one exception is the action on a snack bar or a bottom banner, which SHALL use a compact size (a smaller label and padding, 36px tall) with the same radius and weight, so the message keeps the width of its row. On a bottom banner the compact button's label SHALL take the banner's own text size, the same as the message. Every variant with a fill SHALL keep its label at 4.5:1 or more at every size, so that a compact label does not depend on WCAG's large-text minimum. Icon-only buttons are not covered by this requirement.

- **filled** (the default): a solid fill in the `primary` colour role (brand-primary's hue and chroma) with its white `on-primary` label, for the main action on a screen and the action on a bottom banner.
- **outlined**: a transparent fill with a visible border, for secondary and dismissive actions (cancel, later, back).
- **danger**: a solid red fill with white text, for destructive actions.
- **on-container**: a translucent white fill with a white border, for a button placed on a coloured surface such as a snack bar.

A text button SHALL NOT be rendered as plain text without a fill or a border.

#### Scenario: Default variant
- **WHEN** a text button is rendered without a variant
- **THEN** it SHALL have the `primary` role's fill with its white `on-primary` label at 4.5:1 or more, and a 12px corner radius

#### Scenario: Secondary and dismissive actions are outlined
- **WHEN** a screen offers a cancel, later or back action next to its main action
- **THEN** that action SHALL be rendered in the outlined variant with a visible border

#### Scenario: Destructive action
- **WHEN** a button cancels an entry or deletes data
- **THEN** it SHALL be rendered in the danger variant

#### Scenario: Button on a coloured surface
- **WHEN** a button is placed on a snack bar with a coloured or gradient fill
- **THEN** it SHALL be rendered in the on-container variant with a translucent white fill and a white border at least 1.5px wide

#### Scenario: Compact button on a snack bar
- **WHEN** a snack bar shows an action
- **THEN** the action SHALL be 36px tall with a label smaller than the default button's
- **AND** it SHALL keep the shared 12px corner radius and the bold label weight

#### Scenario: Compact filled button on a bottom banner
- **WHEN** the install banner or the signup prompt shows its action
- **THEN** the action SHALL be the filled variant, 36px tall
- **AND** its label SHALL have the same text size as the banner's message
- **AND** it SHALL keep the shared 12px corner radius and the bold label weight

#### Scenario: Catalog matches the specification
- **WHEN** the button catalog shows all four variants side by side
- **THEN** each variant SHALL render as described above, and any change to their look SHALL be detected by comparing the catalog with its approved screenshot
