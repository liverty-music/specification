## MODIFIED Requirements

### Requirement: Listed venue name normalization

A listed venue name SHALL be normalized by folding full-width and half-width forms to one form, collapsing runs of whitespace to a single space and trimming the ends, removing a leading "〈city〉公演 ＠" prefix, and then removing a leading "〈prefecture〉・" prefix where the prefecture is one of Japan's 47 prefectures, with or without its 都/道/府/県 suffix. A name that is blank after normalization SHALL be treated as missing. A name that only says the venue is not yet announced SHALL normalize to an empty name, and so is also treated as missing: compared ignoring whitespace, punctuation and Latin letter case, it is one of "TBA", "TBD", "to be announced", "coming soon", "stay tuned", "未定", "後日発表", "private" or "private event", or one of "未定" and "後日発表" with "会場" before it, "予定" after it, or both (as in "会場未定" and "会場後日発表予定"), or it contains "某所" (an undisclosed place, as in "横浜某所"). "private" and "private event" are the listing's own word for a show at a place it does not disclose to the public. Normalizing an already-normalized name SHALL leave it unchanged. This is the only normalization of a venue name: every comparison of venue names (an Event's listed venue name, a ConcertCandidate's, and the events Concert.Search returns) starts from it.

#### Scenario: Prefecture prefix removed
- **WHEN** the listed venue name is "大阪・フェスティバルホール"
- **THEN** the normalized name is "フェスティバルホール"

#### Scenario: Performance-city prefix removed
- **WHEN** the listed venue name is "大阪公演 ＠フェスティバルホール"
- **THEN** the normalized name is "フェスティバルホール"

#### Scenario: Middle dot after a non-prefecture word is kept
- **WHEN** the listed venue name is "東京文化会館・大ホール"
- **THEN** the normalized name is "東京文化会館・大ホール"

#### Scenario: Whitespace-only name is missing
- **WHEN** the listed venue name is "　 "
- **THEN** the normalized name is empty and the name is treated as missing

#### Scenario: Venue not yet announced is missing
- **WHEN** the listed venue name is "TBA", "-STAY TUNED-", "未定", "横浜某所", "PRIVATE" or "Private Event"
- **THEN** the normalized name is empty and the name is treated as missing

#### Scenario: Venue to be announced later is missing
- **WHEN** the listed venue name is "会場後日発表予定", "会場未定" or "後日発表予定"
- **THEN** the normalized name is empty and the name is treated as missing

#### Scenario: A real name containing a marker word is kept
- **WHEN** the listed venue name is "TBA Hall Osaka"
- **THEN** the normalized name is "TBA Hall Osaka"

#### Scenario: Already normalized name is unchanged
- **WHEN** the listed venue name is "日本武道館"
- **THEN** the normalized name is "日本武道館"

