## ADDED Requirements

### Requirement: Installed Noto is used before a download

On a device whose installed Noto Sans JP or Noto Sans CJK JP has every weight from 100 to 900, the fan app SHALL draw its plain text with the installed font and SHALL NOT download Noto Sans JP. Any other device, including one whose installed Noto has fewer weights, SHALL download Noto Sans JP as before, so every weight is drawn as designed and none is synthesized.

#### Scenario: Windows with Noto Sans JP installed

- **WHEN** the fan opens the app in Chrome on Windows 11 with Noto Sans JP installed
- **THEN** Japanese text is drawn in Noto Sans JP and no Noto Sans JP font file is downloaded

#### Scenario: Android

- **WHEN** the fan opens the app in Chrome on Android 15 or later, which ships Noto Sans CJK JP in every weight
- **THEN** Japanese text is drawn in Noto Sans CJK JP and no Noto Sans JP font file is downloaded

#### Scenario: Android with Regular only

- **WHEN** the fan opens the app on an Android version whose Noto Sans CJK JP has only the Regular weight, and a screen shows bold Japanese text
- **THEN** Noto Sans JP is downloaded and draws both the regular and the bold text

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
