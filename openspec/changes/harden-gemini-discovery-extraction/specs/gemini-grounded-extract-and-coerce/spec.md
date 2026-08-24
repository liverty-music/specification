# gemini-grounded-extract-and-coerce Specification (delta)

## ADDED Requirements

### Requirement: Step 1 extracts every field in the source page's original language

Step 1 SHALL copy every extracted field — venue in particular — verbatim in the language it is written on the source page, and SHALL NOT translate, romanize, anglicize, or otherwise localize any value, even when the page offers an English or otherwise multilingual view. A Japanese venue name SHALL be emitted in Japanese.

#### Scenario: Multilingual tour page — Japanese venue retained
- **WHEN** Step 1 extracts an event whose venue is printed as `幕張メッセ 9・11ホール` on a page that also offers an English view rendering it "Makuhari Messe Halls 9 & 11"
- **THEN** the emitted `<venue>` SHALL be `幕張メッセ 9・11ホール`
- **AND** it SHALL NOT be romanized or translated to English

#### Scenario: Renamed venue kept verbatim, not semantically translated
- **WHEN** the source prints a venue such as `クロコくんホール（旧 日本ガイシホール）`
- **THEN** the emitted `<venue>` SHALL reproduce that Japanese string verbatim
- **AND** it SHALL NOT be rendered as an English gloss such as "Crocodile Hall"

### Requirement: Step 1 selects the tour-specific page as source_url

For each extracted tour or show, Step 1 SHALL set `source_url` to the artist's page dedicated to THAT specific tour/show — a tour special/feature page or the specific announcement article — in preference to the official-site top page or a generic news-list page, choosing the most detailed tour-specific candidate.

#### Scenario: Tour feature page preferred over the site top
- **WHEN** a tour has a dedicated feature page (e.g. a `/feature/<tour>` page) and the artist also has an official-site top page
- **THEN** `source_url` SHALL be the tour feature page, not the site top page

#### Scenario: No tour-specific page available
- **WHEN** no tour-specific page exists and only a general news-list or top page is available
- **THEN** Step 1 MAY use the most detailed available official page as `source_url`
