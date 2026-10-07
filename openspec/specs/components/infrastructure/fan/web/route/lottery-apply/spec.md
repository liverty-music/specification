# components/infrastructure/fan/web/route/lottery-apply Specification

## Purpose
The fan's lottery application screen, where a fan picks a ticket count, enters their 本人確認 (identity check) details and authorizes the card hold before applying to a LotterySalesPhase.

## Requirements

### Requirement: Phone number entry

The 本人確認 phone number field SHALL accept either a Japanese domestic number — 10 or 11 digits starting with 0 — or an E.164 number, in both cases with or without spaces, hyphens and parentheses. The screen SHALL send the number in E.164 form: a domestic number becomes `+81` followed by the digits without the leading 0, and an E.164 number is sent without its separators. While the entered number fits neither form, the screen SHALL keep the step's continue action disabled and show that the phone number is invalid.

#### Scenario: Domestic number with hyphens

- **WHEN** the fan enters `090-1234-5678` and applies
- **THEN** the application is sent with the phone number `+819012345678`

#### Scenario: Landline number

- **WHEN** the fan enters `03 1234 5678` and applies
- **THEN** the application is sent with the phone number `+81312345678`

#### Scenario: E.164 number with spaces

- **WHEN** the fan enters `+81 90 1234 5678` and applies
- **THEN** the application is sent with the phone number `+819012345678`

#### Scenario: Number fits neither form

- **WHEN** the fan enters `12345` or `9012345678`
- **THEN** the continue action stays disabled and the field shows that the phone number is invalid
