## MODIFIED Requirements

### Requirement: Material 3 type styles

Text SHALL take its size, line height, weight and tracking from one of the Material 3 type styles below, or from that style's emphasized version, which is the same style one step heavier (400 becomes 500, 500 becomes 600). The sizes SHALL be fixed, apart from the exceptions named under "Text styles are not set per screen": they SHALL NOT change with the width of the window or of a container, and they SHALL scale with the text size the user sets in the browser. Sizes are stated at the browser's default text size of 16 px. The line heights in the "Size / line height" column are the small language height, used for Latin text. While the app's language is Japanese, text SHALL use the medium language height of its style, given in the "Medium line height" column, which is taller than the small value, so that Japanese characters, which fill the full height of the line, do not touch the line above and below. The values are the Material 3 `md.ref.typeface.<style>.line-height` tokens for the Medium language height (Web).

| Style | Size / line height (px) | Medium line height (px) | Weight | Tracking (px) |
|---|---|---|---|---|
| display-large | 57 / 64 | 73 | 400 | -0.25 |
| display-medium | 45 / 52 | 56 | 400 | 0 |
| display-small | 36 / 44 | 47 | 400 | 0 |
| headline-large | 32 / 40 | 42 | 400 | 0 |
| headline-medium | 28 / 36 | 38 | 400 | 0 |
| headline-small | 24 / 32 | 35 | 400 | 0 |
| title-large | 22 / 28 | 31 | 400 | 0 |
| title-medium | 16 / 24 | 27 | 500 | 0.15 |
| title-small | 14 / 20 | 23 | 500 | 0.1 |
| body-large | 16 / 24 | 27 | 400 | 0.5 |
| body-medium | 14 / 20 | 23 | 400 | 0.25 |
| body-small | 12 / 16 | 18 | 400 | 0.4 |
| label-large | 14 / 20 | 23 | 500 | 0.1 |
| label-medium | 12 / 16 | 18 | 500 | 0.5 |
| label-small | 11 / 16 | 18 | 500 | 0.5 |

#### Scenario: Title at any window width

- **WHEN** a heading in the title-large style is rendered in a 360 px wide window and in a 1280 px wide window
- **THEN** it is 22 px on a 28 px line in both

#### Scenario: Emphasized style is one step heavier

- **WHEN** a label in the emphasized label-large style is rendered next to one in the label-large style
- **THEN** the two have the same size and line height, and the emphasized one has weight 600 where the other has 500

#### Scenario: Larger browser text size

- **WHEN** the user sets the browser's default text size to 20 px
- **THEN** text in the body-large style is 20 px

#### Scenario: Japanese text takes the medium line height

- **WHEN** a heading in the display-large style is shown with the app language set to Japanese, and again with it set to English
- **THEN** it is on a 73 px line in Japanese and on a 64 px line in English
- **AND** the two have the same size, weight and tracking

## ADDED Requirements

### Requirement: Reduced motion keeps a short fade

Under `prefers-reduced-motion: reduce` the app SHALL replace every movement (a slide, a growth, a turn, a scale) with a fade of at most 100 ms (`md.sys.motion.duration.short2`) and no movement, and SHALL stop decorative loops and effects (a shimmer, a pulse, a parallax, a flare, an ambient background). A section the fan opens to read more (a disclosure), an in-place edit of a list, a long scroll the app makes for the fan (the month jump), a bottom sheet's close and the welcome demonstration SHALL still change at once. A progress indicator keeps moving, since a still one reads as a frozen app, and the drawing of the artist bubble field is outside this requirement. The duration tokens that drive movement SHALL be 0 ms under reduced motion; the effects spring's duration, which drives opacity only, SHALL be 100 ms.

#### Scenario: A surface appears under reduced motion

- **WHEN** a surface that normally slides, grows or turns in appears while `prefers-reduced-motion: reduce` is active
- **THEN** it fades in over at most 100 ms and does not move

#### Scenario: A decorative loop under reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** no shimmer, pulse, parallax, flare or ambient background animation plays

### Requirement: Control boundaries reach 3:1

An edge that is the only thing showing a control's shape or extent SHALL measure at least 3:1 against what is painted behind it: a text field's border (the `outline` role, opaque, on every surface tier) and the edge of the onboarding progress track, which marks its full length. An outlined chip or button, which its label already identifies, keeps the `outline-variant` border.

#### Scenario: Control boundaries reach 3:1

- **WHEN** a text field rests on any surface tier, or the onboarding progress track is empty
- **THEN** the field's border and the track's edge each measure at least 3:1 against the surface behind them
