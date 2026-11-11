## ADDED Requirements

### Requirement: Material 3 type styles shared with the fan app

Text SHALL take its size, line height, weight and tracking from one of the Material 3 type styles below, or from that style's emphasized version, which is the same style one step heavier (400 becomes 500, 500 becomes 600). The sizes SHALL be fixed: they SHALL NOT change with the width of the window or of a container, and they SHALL scale with the text size the user sets in the browser. Sizes are stated at the browser's default text size of 16 px.

| Style | Size / line height (px) | Weight | Tracking (px) |
|---|---|---|---|
| display-large | 57 / 64 | 400 | -0.25 |
| display-medium | 45 / 52 | 400 | 0 |
| display-small | 36 / 44 | 400 | 0 |
| headline-large | 32 / 40 | 400 | 0 |
| headline-medium | 28 / 36 | 400 | 0 |
| headline-small | 24 / 32 | 400 | 0 |
| title-large | 22 / 28 | 400 | 0 |
| title-medium | 16 / 24 | 500 | 0.15 |
| title-small | 14 / 20 | 500 | 0.1 |
| body-large | 16 / 24 | 400 | 0.5 |
| body-medium | 14 / 20 | 400 | 0.25 |
| body-small | 12 / 16 | 400 | 0.4 |
| label-large | 14 / 20 | 500 | 0.1 |
| label-medium | 12 / 16 | 500 | 0.5 |
| label-small | 11 / 16 | 500 | 0.5 |

#### Scenario: Title at any window width

- **WHEN** a heading in the title-large style is rendered in a 360 px wide window and in a 1280 px wide window
- **THEN** it is 22 px on a 28 px line in both

#### Scenario: Emphasized style is one step heavier

- **WHEN** a label in the emphasized label-large style is rendered next to one in the label-large style
- **THEN** the two have the same size and line height, and the emphasized one has weight 600 where the other has 500

#### Scenario: Larger browser text size

- **WHEN** the user sets the browser's default text size to 20 px
- **THEN** text in the body-large style is 20 px

### Requirement: A fixed spacing scale

Space between and inside elements SHALL come from one fixed scale: 4, 8, 12, 16, 24, 32 and 48 px. The values SHALL NOT change with the width of the window. Only a value the scale cannot express, such as an offset derived from another element's size, MAY differ.

#### Scenario: Same spacing on any width

- **WHEN** the same console screen is rendered in a 360 px wide window and in a 1280 px wide window
- **THEN** the space between its elements is the same in both

### Requirement: Elevation levels

A shadow SHALL come from one of the Material 3 elevation levels: level 0 (none), and levels 1 to 5 at 1, 3, 6, 8 and 12 dp. A glow in a brand or artist colour is not elevation and MAY be used where a surface's own spec describes it.

#### Scenario: A floating surface at a named level

- **WHEN** a menu or a floating button casts a shadow
- **THEN** the shadow is the one defined for its elevation level, and two surfaces at the same level cast the same shadow

### Requirement: One keyboard focus ring

An element focused from the keyboard SHALL show one ring, the same in every console screen: 3 px thick, 2 px outside the element, with a contrast ratio of at least 3:1 against the surface behind it. A pointer click SHALL NOT show the ring. Where a focused control sits inside a field that shows the focus for it, the field SHALL show the ring in place of the control. An element that spans its container from edge to edge (a list row, a menu item, a scrolling region) SHALL draw the ring just inside its edge instead, where a neighbour or the container's clipping would cover a ring drawn outside.

#### Scenario: Tabbing through a console screen

- **WHEN** a member moves through a console screen with the Tab key
- **THEN** each focused element shows the 3 px ring at a 2 px offset

#### Scenario: Pointer click

- **WHEN** a member clicks a button with a pointer
- **THEN** the button shows no focus ring

### Requirement: Layout breakpoints

A layout that changes with the width of the window SHALL change at the Material 3 breakpoints: compact below 600 px, medium from 600 px, expanded from 840 px, large from 1200 px and extra-large from 1600 px. A component that adapts to its own container MAY use other widths.

#### Scenario: Window width crosses a breakpoint

- **WHEN** a window narrows from 900 px to 700 px wide and a screen's layout changes on the way
- **THEN** the change happens when the width passes 840 px

### Requirement: Higher contrast when the system asks for it

When the operating system asks for more contrast, body text SHALL have a contrast ratio of at least 7:1 against its background, and control boundaries and icons SHALL have at least 4.5:1.

#### Scenario: Secondary text with more contrast

- **WHEN** a screen with secondary text is opened on a device set to increase contrast
- **THEN** that text has a contrast ratio of at least 7:1 against its background

#### Scenario: Regular contrast is unchanged

- **WHEN** the same screen is opened on a device with the default contrast setting
- **THEN** the colours are the regular ones

## RENAMED Requirements

- FROM: `### Requirement: A fixed type scale with Japanese system fonts`
- TO: `### Requirement: A fixed type scale in Noto Sans JP`

## MODIFIED Requirements

### Requirement: A fixed type scale in Noto Sans JP

Text SHALL use the fixed Material 3 type styles shared with the fan app, which do not grow or shrink with the window: body-medium (14 px on a 20 px line) by default, label-large for buttons and tabs, and headline-small (24 px on a 32 px line) for page titles. Sizes are stated at the browser's default text size of 16 px and SHALL scale with the text size the user sets in the browser. Every type style SHALL use Noto Sans JP, the fan app's text typeface, so that the console looks the same on every device. If the font cannot be loaded, text SHALL show in the device's Japanese system font (Hiragino Sans or Yu Gothic UI, falling back to the system UI font). Numbers in counts, prices, dates and times SHALL use tabular (equal-width) figures so columns of numbers line up.

#### Scenario: Same size on PC and phone

- **WHEN** the same event page is opened on a 1440 px wide PC window and on a 390 px wide phone
- **THEN** the body text is 14 px and the page title is 24 px on both

#### Scenario: Counts line up

- **WHEN** a sales table shows 412 entries in one row and 1,380 requested tickets in another
- **THEN** the digits of both numbers have equal widths and line up at the right edge

#### Scenario: Same typeface on Windows and on a Mac

- **WHEN** the same console screen is opened on a Windows PC and on a Mac with network access
- **THEN** its Japanese and Latin text is drawn in Noto Sans JP on both, including page titles

#### Scenario: Font cannot be loaded

- **WHEN** a console screen opens and the font cannot be loaded
- **THEN** text shows in the device's Japanese system font and the layout is usable
