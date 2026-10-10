# Spec Delta

## Purpose

The organizer console's visual foundation: color roles with light and dark values, the fixed type scale and fonts, and where the brand color may appear, so that the console reads as a calm work tool on a PC and on a phone.

## ADDED Requirements

### Requirement: Light by default, dark when the system is dark

The console SHALL render with light colors, and SHALL render with dark colors when the operating system asks for a dark appearance. It SHALL switch between the two without a reload when the system setting changes. Every color the console shows SHALL come from a named color role (the same role names the fan app uses, such as `surface`, `on-surface`, `primary`, `on-primary`, `outline`, `error`), each with a light and a dark value; the console's values are its own and do not change the fan app's colors.

#### Scenario: Office PC in light mode

- **WHEN** an operator opens the console on a PC whose system appearance is light
- **THEN** the console shows a light surface with dark text

#### Scenario: Phone in dark mode

- **WHEN** an operator opens the console on a phone whose system appearance is dark
- **THEN** the console shows a dark surface with light text, and form controls and scrollbars are dark too

#### Scenario: System switches while the console is open

- **WHEN** the system appearance changes from light to dark while a console page is open
- **THEN** the page changes to dark colors without reloading

### Requirement: Text and controls meet contrast targets

In both light and dark, body text SHALL have a contrast ratio of at least 4.5:1 against its background, and text of at least 24 px, icons and control boundaries SHALL have at least 3:1.

#### Scenario: Secondary text on a card

- **WHEN** a card shows a secondary line such as a venue name
- **THEN** that text has a contrast ratio of at least 4.5:1 against the card in light and in dark

### Requirement: The brand color marks only the primary action, focus and the logo

The brand magenta SHALL be used only for the primary action of a page, the keyboard focus indicator and the logo. Status (published, draft, on sale, error) SHALL never be shown by color alone: every status color SHALL be accompanied by its text label.

#### Scenario: One primary action

- **WHEN** the Concerts page offers 公演をつくる (create a concert) as its main action and each concert row offers 開く (open)
- **THEN** only 公演をつくる uses the brand color

#### Scenario: Status with label

- **WHEN** an event is published
- **THEN** its badge shows the text 公開中 together with its color

### Requirement: A fixed type scale with Japanese system fonts

Text SHALL use a fixed scale that does not grow or shrink with the window: body 14 px on a 20 px line by default, body-large 16/24, label 14/20 for buttons and tabs, title-medium 16/24, title-large 22/28 and headline-small 24/32 for page titles. Text SHALL use the device's Japanese system font (Hiragino Sans, Noto Sans JP or Yu Gothic UI, falling back to the system UI font). Numbers in counts, prices, dates and times SHALL use tabular (equal-width) figures so columns of numbers line up.

#### Scenario: Same size on PC and phone

- **WHEN** the same event page is opened on a 1440 px wide PC window and on a 390 px wide phone
- **THEN** the body text is 14 px and the page title is 24 px on both

#### Scenario: Counts line up

- **WHEN** a sales table shows 412 entries in one row and 1,380 requested tickets in another
- **THEN** the digits of both numbers have equal widths and line up at the right edge
