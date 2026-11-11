## ADDED Requirements

### Requirement: One list item

Every row of a list in the fan app that shows an icon, a label, an optional value and an optional caret, such as the rows of Settings and of the All Nearby filter sheet, SHALL be the same list item, in the Material 3 layout: at least 56 px tall, 16 px of space at both ends, a 24 px leading icon, the label in the body-large style, and the value in the label-small style. A row that does something on tap SHALL be a button or a link, with a state layer.

#### Scenario: Settings row and filter row match

- **WHEN** a Settings row with an icon, a value and a caret is compared with an All Nearby filter row
- **THEN** both have the same height, the same space at both ends and the same text styles

#### Scenario: Long value

- **WHEN** a row's value is too long to fit
- **THEN** the value is cut off with an ellipsis and the label keeps its full width

#### Scenario: Long label

- **WHEN** a row's label, such as the fan's own name, is longer than the row and the row also has a value
- **THEN** the label wraps onto more lines and the value stays visible, cut off with an ellipsis when it does not fit

#### Scenario: Row with two lines

- **WHEN** a row also has a line of supporting text in the body-medium style
- **THEN** the row grows to fit it and stays a single target

## MODIFIED Requirements

### Requirement: SVG Icon Component
The system SHALL provide a centralized `<svg-icon>` custom element as the single source of truth for all SVG icon definitions, eliminating inline SVG duplication across templates.

#### Scenario: Icon rendering by name
- **WHEN** `<svg-icon name="home">` is rendered
- **THEN** the component SHALL display the SVG icon matching the given name
- **AND** only the matched icon SHALL be present in the DOM (via Aurelia `switch.bind`)
- **AND** unrecognized names SHALL render nothing (default-case fallback)

#### Scenario: Default size follows the text
- **WHEN** `<svg-icon>` is rendered with no `size` attribute and no size from a stylesheet
- **THEN** it SHALL be as wide and as tall as the font size of the text around it (`1em`)

#### Scenario: Size variants
- **WHEN** `<svg-icon>` is rendered with a `size` attribute
- **THEN** the host element SHALL set `data-size` to the given value
- **AND** the component SHALL support sizes: sm (16 px), md (20 px), lg (24 px), xl (40 px)
- **AND** an icon that stands on its own, such as in a list item, a navigation bar or a floating button, SHALL use lg

#### Scenario: Size from a stylesheet
- **WHEN** a stylesheet gives an `<svg-icon>` element a size
- **THEN** the drawn icon SHALL take that size

#### Scenario: Icon set coverage
- **WHEN** the icon component is registered
- **THEN** it SHALL include at minimum these icons: home, search, discovery, music, my-artists, ticket, settings, check, alert-triangle, warning, info, x-circle, x, chevron-right, arrow-left, trash, plus, map-pin, calendar, link, clock, globe, bell, lock, mail, qr-code, list, grid

#### Scenario: Color inheritance
- **WHEN** `<svg-icon>` is placed inside a colored container
- **THEN** stroke-based icons SHALL use `stroke="currentColor"` to inherit the parent's text color
- **AND** fill-based icons (warning, x-circle) SHALL use `fill="currentColor"`

### Requirement: One button style in four variants

Every text button in the fan app SHALL use one shared button style, in one of four variants. All four SHALL share the same corner radius (12px), padding and label weight, so that any text button reads as a button from its shape alone. The one exception is the action on a snack bar or a bottom banner, which SHALL use the compact size, Material 3's extra-small button (32px tall, 12px from its edge to the label, the `label-large` type style), with the same radius and weight, so the message keeps the width of its row. A compact button SHALL still be at least 48 × 48 px to touch. Every variant with a fill SHALL keep its label at 4.5:1 or more at every size, so that a compact label does not depend on WCAG's large-text minimum. Icon-only buttons are not covered by this requirement.

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
- **THEN** the action SHALL be the compact size: 32px tall, with the `label-large` type style
- **AND** it SHALL keep the shared 12px corner radius and label weight, and a touch target of at least 48 × 48 px

#### Scenario: Compact filled button on a bottom banner
- **WHEN** the install banner or the signup prompt shows its action
- **THEN** the action SHALL be the filled variant at the compact size, 32px tall, with the `label-large` type style
- **AND** it SHALL keep the shared 12px corner radius and label weight, and a touch target of at least 48 × 48 px

#### Scenario: Catalog matches the specification
- **WHEN** the button catalog shows all four variants side by side
- **THEN** each variant SHALL render as described above, and any change to their look SHALL be detected by comparing the catalog with its approved screenshot
