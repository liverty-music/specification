## ADDED Requirements

### Requirement: Same tour title

Two Series titles SHALL be the same tour title when they are equal once full-width and half-width forms are folded to one form, Latin letter case is ignored, and every character that is neither a letter nor a digit (spaces, punctuation, quotation marks, symbols) is removed. No other rule, such as a year or a word that differs, SHALL make two titles the same.

#### Scenario: Quotation marks and case differ

- **WHEN** one title is "2026 LE SSERAFIM TOUR 'PUREFLOW'" and the other is "2026 LE SSERAFIM TOUR “PUREFLOW”"
- **THEN** they are the same tour title

#### Scenario: Full-width letters

- **WHEN** one title is "ＡＲＥＮＡ ＴＯＵＲ ２０２６" and the other is "Arena Tour 2026"
- **THEN** they are the same tour title

#### Scenario: Different year

- **WHEN** one title is "ARENA TOUR 2026" and the other is "ARENA TOUR 2027"
- **THEN** they are not the same tour title
