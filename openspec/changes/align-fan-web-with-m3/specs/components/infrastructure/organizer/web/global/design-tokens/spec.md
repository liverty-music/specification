## MODIFIED Requirements

### Requirement: Material 3 type styles shared with the fan app

Text SHALL take its size, line height, weight and tracking from one of the Material 3 type styles below, or from that style's emphasized version, which is the same style one step heavier (400 becomes 500, 500 becomes 600). The sizes SHALL be fixed: they SHALL NOT change with the width of the window or of a container, and they SHALL scale with the text size the user sets in the browser. Sizes are stated at the browser's default text size of 16 px. The line heights in the table are the small language height, used for Latin text. Text in Japanese SHALL use the medium language height of its style, as in the fan app, whose design-tokens requirement "Material 3 type styles" lists the medium values.

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

#### Scenario: Japanese text takes the medium line height

- **WHEN** a heading in the display-large style is set in Japanese and another in Latin letters
- **THEN** the Latin one is on a 64 px line and the Japanese one on a 73 px line
