<!-- spec: gemini-grounded-extract-and-coerce | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Discovered concert fields preserve the source page's original language -->

### Requirement: Discovered concert fields preserve the source page's original language

Step 1 SHALL copy every extracted field — venue in particular — verbatim in the language it is written on the source page, and SHALL NOT translate, romanize, anglicize, or otherwise localize any value, even when the page offers an English or otherwise multilingual view. A Japanese venue name SHALL be emitted in Japanese.

#### Scenario: Multilingual tour page — Japanese venue retained

- **WHEN** Step 1 extracts an event whose venue is printed as `幕張メッセ 9・11ホール` on a page that also offers an English view rendering it "Makuhari Messe Halls 9 & 11"
- **THEN** the emitted `<venue>` SHALL be `幕張メッセ 9・11ホール`
- **AND** it SHALL NOT be romanized or translated to English

#### Scenario: Renamed venue kept verbatim, not semantically translated

- **WHEN** the source prints a venue such as `クロコくんホール（旧 日本ガイシホール）`
- **THEN** the emitted `<venue>` SHALL reproduce that Japanese string verbatim
- **AND** it SHALL NOT be rendered as an English gloss such as "Crocodile Hall"
