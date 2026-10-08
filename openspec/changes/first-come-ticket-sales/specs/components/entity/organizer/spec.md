# Spec Delta

## ADDED Requirements

### Requirement: Seller details

An Organizer's seller details, shown to fans as the 特商法 (Specified Commercial Transactions Act) 販売業者 (seller) disclosure, SHALL consist of a legal name of 1 to 200 characters, a representative or responsible person of 1 to 100 characters, an address of 1 to 300 characters, a phone number in E.164 form and a contact email address. An Organizer SHALL have complete seller details only when all five are present and valid.

#### Scenario: Corporation with all details

- **WHEN** an Organizer has a legal name, a representative, an address, the phone `+81312345678` and a contact email
- **THEN** its seller details are complete

#### Scenario: Address missing

- **WHEN** an Organizer's seller details have no address
- **THEN** its seller details are not complete

### Requirement: Platform fee rate

An Organizer's platform fee rate SHALL be 0 to 30% in hundredths of a percent, and a new Organizer's rate SHALL be 8%.

#### Scenario: New Organizer

- **WHEN** an Organizer is created
- **THEN** its platform fee rate is 8%

#### Scenario: Rate over the bound

- **WHEN** an Organizer's rate is set to 31%
- **THEN** the rate is invalid
