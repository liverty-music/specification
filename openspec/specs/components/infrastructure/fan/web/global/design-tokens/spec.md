# Design Tokens

## Purpose

Establishes the Material 3 semantic token layer for the frontend — color roles with guaranteed `on-*`
pairings, state-layer opacities, spatial/effects motion, shape roles, and tonal surface tiers — expressed in
the project's oklch + CUBE CSS idiom so every component consumes M3 tokens instead of ad-hoc values.

## Requirements

### Requirement: Color roles with guaranteed on-color pairing

The token layer SHALL expose Material 3 color **roles** (`primary`, `secondary`, `tertiary`, their
`*-container` variants, `surface`, `surface-container-*` tiers, `outline`, `error`) where every fill role
has a paired `on-*` role. Components SHALL reference roles, not raw palette values, and any text/icon placed
on a fill SHALL use that fill's matching `on-*` role. Roles SHALL be expressed in oklch as aliases over the
existing brand/surface tokens; no hex or hsl literals are introduced.

#### Scenario: Fill and text use a matched role pair

- **WHEN** a component renders content on a `primary` (or `*-container`) fill
- **THEN** its text/icon color is the matching `on-primary` (or `on-*-container`) role, and the pair meets
  the contrast target (4.5:1 body text, 3:1 large text / UI boundaries)

#### Scenario: Dynamic-hue surfaces guarantee contrast

- **WHEN** a surface color is derived from a variable hue (e.g. an artist-hue card)
- **THEN** the on-color is chosen from the role system such that legibility holds across the full hue range,
  rather than assuming a fixed white/black overlay

#### Scenario: No raw palette leakage

- **WHEN** the stylesheet is audited for color usage
- **THEN** interactive component colors resolve through M3 role tokens (or their host aliases), and there are
  zero hard-coded hex/hsl color literals

### Requirement: State-layer opacity scale

The token layer SHALL define a single set of state-layer opacity tokens — hover 8%, focus 10%, pressed 10%, dragged 16%, selected 12% — applied by overlaying the component's `on-*` role at that opacity. Interaction
feedback SHALL use these tokens rather than per-component one-off opacities or color swaps.

#### Scenario: Hover applies the shared 8% overlay

- **WHEN** a pointer hovers an interactive element
- **THEN** an 8% `on-*` state layer is composited over its base fill using the shared token, not a bespoke
  opacity value

#### Scenario: Keyboard focus uses focus-visible

- **WHEN** an element receives focus from the keyboard
- **THEN** the 10% focus state layer shows via `:focus-visible` (not bare `:focus`), so mouse clicks do not
  leave a stuck state layer

#### Scenario: Selected state persists and stacks

- **WHEN** an element is in a selected/activated state and is also hovered
- **THEN** the 12% selected layer persists and the hover layer stacks on top of it

#### Scenario: Press applies the shared 10% overlay

- **WHEN** a pointer presses an interactive element
- **THEN** a 10% `on-*` state layer is composited over its base fill

### Requirement: Motion tokens split by property class

The token layer SHALL define motion tokens as standard and emphasized **easing** curves, a **duration**
scale, and **spring** approximations partitioned into **spatial** (with visible overshoot, for
transform/size/radius) and **effects** (no overshoot, for color/opacity). Components SHALL select a token by
the property being animated: spatial for movement/scale/shape, effects/standard for color/opacity.

#### Scenario: Positional change uses a spatial spring

- **WHEN** an element animates position, scale, or corner radius
- **THEN** it uses a spatial spring/emphasized token that may overshoot

#### Scenario: Opacity/color change uses a non-bouncy token

- **WHEN** an element animates color or opacity
- **THEN** it uses an effects/standard token with no overshoot

#### Scenario: Scattered raw timings are consolidated

- **WHEN** a transition or animation specifies timing
- **THEN** it references a motion duration/easing token rather than an inline raw millisecond value or an
  ad-hoc cubic-bezier

### Requirement: Shape roles including expressive steps

The token layer SHALL expose Material 3 shape **roles** at their Material 3 values: extra-small 4 px, small 8 px, medium 12 px, large 16 px, large-increased 20 px, extra-large 28 px, extra-large-increased 32 px, extra-extra-large 48 px and full. It SHALL use logical radius properties so shapes mirror correctly in RTL. Radius SHALL match component size.

#### Scenario: Radius matches component size

- **WHEN** a component picks a corner radius
- **THEN** it selects the shape role appropriate to its size (small controls small radius, sheets extra-large,
  pills/avatars full), and an emphasis element may step up to an `-increased` role

#### Scenario: Directional rounding is RTL-safe

- **WHEN** only some corners are rounded (e.g. a bottom sheet's top edge)
- **THEN** logical radius properties are used so the rounding mirrors under RTL

### Requirement: Tonal surface-container tiers

The token layer SHALL provide at least five tonal surface tiers (`surface-container-lowest` through
`-highest`) so depth can be expressed by surface tier rather than shadow alone. Shadow SHALL be reserved for
genuinely floating overlays and, where used, SHALL be themeable (brand-tinted or via a shadow role), never a
hard-coded black shadow that disappears under `forced-colors`.

#### Scenario: Resting depth uses a tonal tier

- **WHEN** a resting (non-floating) surface needs to read as raised
- **THEN** it uses a higher surface-container tier rather than a cast shadow

#### Scenario: Surfaces survive forced-colors

- **WHEN** the UI renders under `forced-colors: active` / high-contrast
- **THEN** surfaces remain distinguishable via their tonal tier, not by shadow alone

### Requirement: Easing curves and durations match Material 3

The motion tokens SHALL use the Material 3 values: easing standard `cubic-bezier(0.2, 0, 0, 1)`, standard-decelerate `cubic-bezier(0, 0, 0, 1)`, standard-accelerate `cubic-bezier(0.3, 0, 1, 1)`, emphasized-decelerate `cubic-bezier(0.05, 0.7, 0.1, 1)` and emphasized-accelerate `cubic-bezier(0.3, 0, 0.8, 0.15)`; durations short 50/100/150/200 ms, medium 250/300/350/400 ms, long 450/500/550/600 ms and extra-long 700/800/900/1000 ms.

#### Scenario: Leaving element accelerates

- **WHEN** an element leaves the screen with the emphasized-accelerate token
- **THEN** its timing curve is `cubic-bezier(0.3, 0, 0.8, 0.15)`: slow at first and fastest at the end

### Requirement: State and motion tokens are shared with the organizer console

The state-layer opacities, easing curves, durations, type styles, elevation levels, focus ring size and minimum touch target SHALL be defined once and used by both the fan app and the organizer console, so a change to one of them applies to both. The plain typeface, Noto Sans JP, is also shared. The breakpoints are the same numbers in both apps. Colors, shapes and the brand typeface are not shared: each app keeps its own values under the same role names.

#### Scenario: One edit applies to both apps

- **WHEN** the hover opacity is changed in the shared definition
- **THEN** the fan app and the organizer console both use the new value, with no other edit

#### Scenario: Colors stay per app

- **WHEN** the organizer console renders its light `surface`
- **THEN** the fan app's dark navy `surface` is unchanged

### Requirement: Primary role takes a white label at every size

The `primary` colour role SHALL keep brand-primary's hue and chroma at a lightness where its paired `on-primary` role, white, measures at least 4.5:1, so that text on a primary fill passes at every size and does not depend on WCAG's large-text minimum. The brand colour itself (`--color-brand-primary`) SHALL stay unchanged for surfaces that carry no text on it: the FAB's gradient, brand lines and glows.

#### Scenario: Primary role takes a white label at every size
- **WHEN** white `on-primary` text of any size is placed on the `primary` fill
- **THEN** the pair SHALL measure at least 4.5:1
- **AND** the `primary` fill SHALL have brand-primary's hue and chroma

#### Scenario: The brand colour stays for surfaces without text
- **WHEN** the FAB, a brand-gradient line or a brand glow is rendered
- **THEN** it SHALL use the brand colour, not the darker `primary` role

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

### Requirement: Installed Noto is used before a download

On Windows 10 or 11 with Noto Sans JP installed, and on Android 15 or later, the fan app SHALL draw its plain text with the installed Noto Sans JP (every weight from 100 to 900) or Noto Sans CJK JP (every weight from 400 to 900, the lightest the app uses), and SHALL NOT download Noto Sans JP. Every other device, including Android 14 or earlier, whose Noto Sans CJK JP has only the Regular weight, SHALL download Noto Sans JP as before. On Windows and Android, with the Noto that comes with the operating system, bold text SHALL NOT be drawn at the regular weight or in a synthesized bold. A Noto Sans JP or Noto Sans CJK JP in separate files per weight, whether the fan installed it or a Linux distribution ships it, is outside this guarantee and may draw bold at the regular weight.

#### Scenario: Windows with Noto Sans JP installed

- **WHEN** the fan opens the app in Chrome on Windows 11 with Noto Sans JP installed
- **THEN** Japanese text is drawn in Noto Sans JP and no Noto Sans JP font file is downloaded

#### Scenario: Android 15 or later

- **WHEN** the fan opens the app in Chrome on Android 15 and a screen shows regular and bold Japanese text
- **THEN** both are drawn in the installed Noto Sans CJK JP at their own weights, and no Noto Sans JP font file is downloaded

#### Scenario: Android 14 or earlier

- **WHEN** the fan opens the app in Chrome on Android 14 and a screen shows regular and bold Japanese text
- **THEN** Noto Sans JP is downloaded and draws both at their own weights

#### Scenario: iPhone

- **WHEN** the fan opens the app in Safari on an iPhone, which has no Noto font
- **THEN** Noto Sans JP is downloaded and used

### Requirement: Japanese text is set for reading

All text in the fan app SHALL be set with proportional widths for Japanese characters and punctuation, SHALL put a small space between Japanese and Latin letters or digits where the browser can, SHALL apply strict Japanese line-break rules, and SHALL break Japanese lines between phrases rather than inside a word where the browser can. Headings SHALL balance their lines. Text set in a type style SHALL keep these settings.

#### Scenario: Mixed Japanese and Latin text

- **WHEN** a line reads 「Zepp Tokyo公演」 in a browser that can space mixed text
- **THEN** a space narrower than a full space appears between "Tokyo" and "公演"

#### Scenario: A phrase is not split

- **WHEN** a Japanese sentence wraps in a browser that can break between phrases
- **THEN** the line ends between two phrases, not inside one

#### Scenario: Small kana at the start of a line

- **WHEN** a line would start with a small kana such as 「ッ」 or a prolonged sound mark
- **THEN** the break moves so the line does not start with it

#### Scenario: Text in a type style

- **WHEN** a line is set in one of the Material 3 type styles
- **THEN** its Japanese characters and punctuation keep their proportional widths

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

An element focused from the keyboard SHALL show one ring, the same in every screen: 3 px thick, 2 px outside the element, with a contrast ratio of at least 3:1 against the surface behind it. A pointer click SHALL NOT show the ring. Where a focused control sits inside a field that shows the focus for it, the field SHALL show the ring in place of the control. An element that spans its container from edge to edge (a list row, a menu item, a scrolling region) SHALL draw the ring just inside its edge instead, where a neighbour or the container's clipping would cover a ring drawn outside.

#### Scenario: Tabbing through a screen

- **WHEN** a fan moves through a screen with the Tab key
- **THEN** each focused element shows the 3 px ring at a 2 px offset

#### Scenario: Pointer click

- **WHEN** a fan clicks a button with a pointer
- **THEN** the button shows no focus ring

### Requirement: Every control is at least 48 × 48 px to touch

Every button, link, tab, checkbox, radio, chip, menu item and navigation item in the fan app SHALL have a touch target of at least 48 × 48 px, even when its visible shape is smaller. Neighbouring targets SHALL NOT overlap. A link inside a sentence of body text is exempt, as in WCAG 2.5.8: its size is set by the line it sits on.

#### Scenario: Compact button

- **WHEN** a snack bar shows a 32 px tall compact action button
- **THEN** the area that responds to a tap is at least 48 × 48 px

#### Scenario: Neighbouring controls

- **WHEN** a row holds several small controls side by side
- **THEN** a tap in the target of one never activates its neighbour

### Requirement: Layout breakpoints

A layout that changes with the width of the window SHALL change at the Material 3 breakpoints: compact below 600 px, medium from 600 px, expanded from 840 px, large from 1200 px and extra-large from 1600 px. A component that adapts to its own container MAY use other widths. A rule that tightens spacing on a short window (a height query) MAY add a width bound to tell a small phone from a larger window, because it changes no layout, only the space between items.

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
