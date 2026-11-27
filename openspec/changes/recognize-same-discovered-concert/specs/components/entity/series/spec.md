## ADDED Requirements

### Requirement: Same tour title

Two Series titles SHALL be the same tour title when they are equal once full-width and half-width forms are folded to one form (a half-width katakana with a voicing mark becoming the one voiced katakana), the case of Latin-script letters is ignored, and every character that is neither a letter nor a number (spaces, punctuation, quotation marks, symbols) is removed. Numbers of every form, such as Roman or circled numerals, SHALL be kept as they are. No other rule, such as a year, a numeral or a word that differs, SHALL make two titles the same.

#### Scenario: Quotation marks and case differ

- **WHEN** one title is "2026 LE SSERAFIM TOUR 'PUREFLOW'" and the other is "2026 LE SSERAFIM TOUR “PUREFLOW”"
- **THEN** they are the same tour title

#### Scenario: Full-width letters

- **WHEN** one title is "ＡＲＥＮＡ ＴＯＵＲ ２０２６" and the other is "Arena Tour 2026"
- **THEN** they are the same tour title

#### Scenario: Half-width voiced katakana

- **WHEN** one title is "ｶﾞｰﾃﾞﾝ TOUR" and the other is "ガーデン TOUR"
- **THEN** they are the same tour title

#### Scenario: Accented Latin letters in another case

- **WHEN** one title is "CAFÉ TOUR" and the other is "café tour"
- **THEN** they are the same tour title

#### Scenario: Sequel numbered with a Roman numeral

- **WHEN** one title is "ARENA TOUR Ⅰ" and the other is "ARENA TOUR Ⅱ"
- **THEN** they are not the same tour title

#### Scenario: Roman numeral is not the same as its letters

- **WHEN** one title is "TOUR Ⅱ" and the other is "TOUR II"
- **THEN** they are not the same tour title

#### Scenario: Circled numerals differ

- **WHEN** one title is "VOL.①" and the other is "VOL.②"
- **THEN** they are not the same tour title

#### Scenario: Different year

- **WHEN** one title is "ARENA TOUR 2026" and the other is "ARENA TOUR 2027"
- **THEN** they are not the same tour title
