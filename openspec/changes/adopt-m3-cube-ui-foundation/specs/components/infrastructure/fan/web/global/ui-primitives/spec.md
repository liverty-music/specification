## ADDED Requirements

### Requirement: One list item

Every row of a list in the fan app that shows an icon, a label, an optional value and an optional caret, such as the rows of Settings and of the All Nearby filter sheet, SHALL be the same list item, in the Material 3 layout: at least 56 px tall, 16 px of space at both ends, a 24 px leading icon, the label in the body-large style, and the value in the label-small style. A row that does something on tap SHALL be a button or a link, with a state layer.

#### Scenario: Settings row and filter row match

- **WHEN** a Settings row with an icon, a value and a caret is compared with an All Nearby filter row
- **THEN** both have the same height, the same space at both ends and the same text styles

#### Scenario: Long value

- **WHEN** a row's value is too long to fit
- **THEN** the value is cut off with an ellipsis and the label keeps its full width

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
