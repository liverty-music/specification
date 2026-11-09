## ADDED Requirements

### Requirement: Installed Noto is used before a download

The fan app SHALL draw its plain text with an installed Noto Sans JP or Noto Sans CJK JP, without downloading Noto Sans JP, on a device where the browser can address the installed font by a name that only a font with every weight from 100 to 900 answers to. Every other device SHALL download Noto Sans JP as before. On no device SHALL bold text be drawn at the regular weight or in a synthesized bold.

#### Scenario: Windows with Noto Sans JP installed

- **WHEN** the fan opens the app in Chrome on Windows 11 with Noto Sans JP installed
- **THEN** Japanese text is drawn in Noto Sans JP and no Noto Sans JP font file is downloaded

#### Scenario: Bold text on Android

- **WHEN** the fan opens the app in Chrome on any Android version and a screen shows bold Japanese text
- **THEN** the bold text is drawn at its bold weight, from the installed Noto Sans CJK JP when it has every weight and can be told apart from a Regular-only one, otherwise from the downloaded Noto Sans JP

#### Scenario: iPhone

- **WHEN** the fan opens the app in Safari on an iPhone, which has no Noto font
- **THEN** Noto Sans JP is downloaded and used

### Requirement: Japanese text is set for reading

All text in the fan app SHALL be set with proportional widths for Japanese characters and punctuation, SHALL put a small space between Japanese and Latin letters or digits where the browser can, SHALL apply strict Japanese line-break rules, and SHALL break Japanese lines between phrases rather than inside a word where the browser can. Headings SHALL balance their lines.

#### Scenario: Mixed Japanese and Latin text

- **WHEN** a line reads 「Zepp Tokyo公演」 in a browser that can space mixed text
- **THEN** a space narrower than a full space appears between "Tokyo" and "公演"

#### Scenario: A phrase is not split

- **WHEN** a Japanese sentence wraps in a browser that can break between phrases
- **THEN** the line ends between two phrases, not inside one

#### Scenario: Small kana at the start of a line

- **WHEN** a line would start with a small kana such as 「ッ」 or a prolonged sound mark
- **THEN** the break moves so the line does not start with it

### Requirement: Labels sit in the vertical centre of their controls

The text of buttons and chips SHALL be centred vertically on the height of its letters, not on the font's line height, where the browser can trim the line box.

#### Scenario: Button label

- **WHEN** a button with a Latin label is shown in a browser that can trim the line box
- **THEN** the space above the capital letters equals the space below the baseline within 1 px
