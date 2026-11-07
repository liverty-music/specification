## ADDED Requirements

### Requirement: Material 3 type styles

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

### Requirement: Text styles are not set per screen

Body text SHALL use the body-large style unless a screen gives it another type style. A heading's look SHALL come from the type style it is given, independently of its heading level, and a screen SHALL NOT define a look of its own for text. The one exception is an artist name on a timetable card, which is sized to its lane.

#### Scenario: Same role, same look

- **WHEN** the step titles of the checkout, lottery entry and resale entry screens are compared
- **THEN** they use the same type style

#### Scenario: Heading level does not decide the look

- **WHEN** a sheet heading is an `h2` and a page section heading in the same style is an `h3`
- **THEN** the two look the same

### Requirement: Fan app typefaces

Display and headline styles SHALL use the brand typeface, Righteous, and SHALL fall back to Noto Sans JP for characters Righteous does not have. All other styles SHALL use Noto Sans JP. If a font cannot be loaded, text SHALL show in the device's Japanese system font. Weights a typeface does not have SHALL NOT be synthesized.

#### Scenario: Japanese text looks the same on every device

- **WHEN** the same screen with Japanese text is opened on an iPhone and on an Android phone with network access
- **THEN** the Japanese body text is drawn in Noto Sans JP on both

#### Scenario: Japanese in a headline

- **WHEN** a heading in the headline-small style reads 公演の詳細
- **THEN** its characters are drawn in Noto Sans JP, and any Latin letters or digits in it in Righteous

#### Scenario: Offline

- **WHEN** the app opens with no network access and the font is not cached
- **THEN** text shows in the device's Japanese system font and the layout is usable

### Requirement: A fixed spacing scale

Space between and inside elements SHALL come from one fixed scale: 4, 8, 12, 16, 24, 32, 48, 64 and 96 px. The values SHALL NOT change with the width of the window. Only a value the scale cannot express, such as an offset derived from another element's size, MAY differ.

#### Scenario: Same spacing on any width

- **WHEN** the same screen is rendered in a 360 px wide window and in a 1280 px wide window
- **THEN** the space between its elements is the same in both

### Requirement: Elevation levels

A shadow SHALL come from one of the Material 3 elevation levels: level 0 (none), and levels 1 to 5 at 1, 3, 6, 8 and 12 dp. A glow in a brand or artist colour is not elevation and MAY be used where a surface's own spec describes it.

#### Scenario: A floating surface at a named level

- **WHEN** a menu or a floating button casts a shadow
- **THEN** the shadow is the one defined for its elevation level, and two surfaces at the same level cast the same shadow

### Requirement: One keyboard focus ring

An element focused from the keyboard SHALL show one ring, the same in every screen: 3 px thick, 2 px outside the element, with a contrast ratio of at least 3:1 against the surface behind it. A pointer click SHALL NOT show the ring. Where a focused control sits inside a field that shows the focus for it, the field SHALL show the ring in place of the control.

#### Scenario: Tabbing through a screen

- **WHEN** a fan moves through a screen with the Tab key
- **THEN** each focused element shows the 3 px ring at a 2 px offset

#### Scenario: Pointer click

- **WHEN** a fan clicks a button with a pointer
- **THEN** the button shows no focus ring

### Requirement: Every control is at least 48 × 48 px to touch

Every button, link, tab, checkbox, radio, chip, menu item and navigation item in the fan app SHALL have a touch target of at least 48 × 48 px, even when its visible shape is smaller. Neighbouring targets SHALL NOT overlap.

#### Scenario: Compact button

- **WHEN** a snack bar shows a 36 px tall compact action button
- **THEN** the area that responds to a tap is at least 48 × 48 px

#### Scenario: Neighbouring controls

- **WHEN** a row holds several small controls side by side
- **THEN** a tap in the target of one never activates its neighbour

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

## MODIFIED Requirements

### Requirement: Shape roles including expressive steps

The token layer SHALL expose Material 3 shape **roles** at their Material 3 values: extra-small 4 px, small 8 px, medium 12 px, large 16 px, large-increased 20 px, extra-large 28 px, extra-large-increased 32 px, extra-extra-large 48 px and full. It SHALL use logical radius properties so shapes mirror correctly in RTL. Radius SHALL match component size.

#### Scenario: Radius matches component size

- **WHEN** a component picks a corner radius
- **THEN** it selects the shape role appropriate to its size (small controls small radius, sheets extra-large,
  pills/avatars full), and an emphasis element may step up to an `-increased` role

#### Scenario: Directional rounding is RTL-safe

- **WHEN** only some corners are rounded (e.g. a bottom sheet's top edge)
- **THEN** logical radius properties are used so the rounding mirrors under RTL

### Requirement: State and motion tokens are shared with the organizer console

The state-layer opacities, easing curves, durations, type styles, elevation levels, focus ring size and minimum touch target SHALL be defined once and used by both the fan app and the organizer console, so a change to one of them applies to both. The plain typeface, Noto Sans JP, is also shared. The breakpoints are the same numbers in both apps, but a query cannot read a shared value, so each app states them itself. Colors, shapes and the brand typeface are not shared: each app keeps its own values under the same role names.

#### Scenario: One edit applies to both apps

- **WHEN** the hover opacity is changed in the shared definition
- **THEN** the fan app and the organizer console both use the new value, with no other edit

#### Scenario: Colors stay per app

- **WHEN** the organizer console renders its light `surface`
- **THEN** the fan app's dark navy `surface` is unchanged

### Requirement: Status colors are named by meaning

A status SHALL be colored by its meaning, through one token per meaning: done or verified uses the success color, selected uses the primary role, a warning uses the warning color, and an error uses the error color. The same meaning SHALL use the same color on every screen, and every color a stylesheet references SHALL be a defined token. The success color SHALL stay green and SHALL be distinguishable from the brand accent and the stage colors: at least 0.1 apart in OKLab from each.

#### Scenario: Done looks the same everywhere

- **WHEN** a screen shows that something is done or verified (an email address verified, an identity verified, a ticket paid)
- **THEN** its status mark uses the success color

#### Scenario: Selected is not shown as done

- **WHEN** a list marks the item the fan has chosen (a followed artist in Discovery, the current language)
- **THEN** the mark uses the primary color, not the success color

#### Scenario: No undefined color

- **WHEN** the stylesheets are checked
- **THEN** every color they reference is defined by the tokens

#### Scenario: Success is not the brand accent

- **WHEN** the success color and the brand accent are compared
- **THEN** they are at least 0.1 apart in OKLab, and so are the success color and each stage color
