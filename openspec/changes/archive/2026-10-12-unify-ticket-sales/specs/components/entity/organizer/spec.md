# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Seller details`
- TO: `### Requirement: Business details`

## MODIFIED Requirements

### Requirement: Business details

An Organizer's business details, shown to fans as the 特商法 (Specified Commercial Transactions Act) 販売業者 disclosure, SHALL consist of its legal name of 1 to 200 characters, its representative name of 1 to 100 characters, its business address of 1 to 300 characters, its business phone number in E.164 form and its contact email, an email address. An Organizer SHALL have complete business details only when all five are present and valid.

#### Scenario: Corporation with all details

- **WHEN** an Organizer has a legal name, a representative name, a business address, the business phone number `+81312345678` and a contact email
- **THEN** its business details are complete

#### Scenario: Address missing

- **WHEN** an Organizer has no business address
- **THEN** its business details are not complete
