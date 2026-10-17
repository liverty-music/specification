# Spec Delta

## ADDED Requirements

### Requirement: Name, short name and owner email are well-formed

An Organizer's name SHALL be 1 to 200 characters long. Its short name SHALL be 3 to 32 characters of lowercase letters `a`-`z`, digits and hyphens, starting with a letter, and SHALL NOT be `admin` or `liverty-music`. Its owner email SHALL be an email address of at most 165 characters, so that the user name `<owner email> (<short name>)` of its owner identity stays within 200 characters.

#### Scenario: Empty name

- **WHEN** the name is empty
- **THEN** the Organizer is invalid

#### Scenario: Name too long

- **WHEN** the name is 201 characters long
- **THEN** the Organizer is invalid

#### Scenario: Valid short name

- **WHEN** the short name is `xx-records` or `band2026`
- **THEN** the short name is valid

#### Scenario: Malformed short name

- **WHEN** the short name is `XX Records`, `2band`, `ab` or 33 characters long
- **THEN** the Organizer is invalid

#### Scenario: Reserved short name

- **WHEN** the short name is `admin` or `liverty-music`
- **THEN** the Organizer is invalid

#### Scenario: Malformed owner email

- **WHEN** the owner email is not an email address
- **THEN** the Organizer is invalid

#### Scenario: Owner email too long

- **WHEN** the owner email is 166 characters long
- **THEN** the Organizer is invalid

## MODIFIED Requirements

### Requirement: Business details

An Organizer's business details, shown to fans as the 特商法 (Specified Commercial Transactions Act) 販売業者 disclosure, SHALL consist of its legal name of 1 to 200 characters, its representative name of 1 to 100 characters, its business address of 1 to 300 characters, its business phone number in E.164 form and its contact email, an email address of at most 165 characters. An Organizer SHALL have complete business details only when all five are present and valid.

#### Scenario: Corporation with all details

- **WHEN** an Organizer has a legal name, a representative name, a business address, the business phone number `+81312345678` and a contact email
- **THEN** its business details are complete

#### Scenario: Address missing

- **WHEN** an Organizer has no business address
- **THEN** its business details are not complete

#### Scenario: Contact email too long

- **WHEN** an Organizer's contact email is 166 characters long
- **THEN** its business details are not valid

## REMOVED Requirements

### Requirement: Name and operator email are well-formed

**Reason**: The attribute is renamed owner email (the person holds the owner role; "operator" is not a defined term), and the short name is added. The rule continues as "Name, short name and owner email are well-formed".
**Migration**: The `operator_email` column and the admin `CreateRequest.operator_email` field become `owner_email`; the existing Organizer gets a short name (design.md Migration Plan).
