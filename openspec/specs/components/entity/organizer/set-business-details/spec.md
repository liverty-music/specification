# components/entity/organizer/set-business-details Specification

## Purpose
Stores an Organizer's business details for the 特商法 (Specified Commercial Transactions Act) disclosure as a whole: legal name, representative name, business address, business phone number and contact email.

## Requirements

### Requirement: Business details replaced as a whole

SetBusinessDetails SHALL replace the Organizer's legal name, representative name, business address, business phone number and contact email with the given ones, leave its other attributes unchanged, and return the updated Organizer. It SHALL fail with InvalidArgument, changing nothing, when any of the five is missing or breaks the Organizer's business details rule, and with NotFound when no Organizer has the id.

#### Scenario: Details entered at vetting

- **WHEN** an admin sets all five business details for an Organizer
- **THEN** the Organizer's business details are complete

#### Scenario: Malformed phone number

- **WHEN** the business phone number is `03-1234-5678`
- **THEN** SetBusinessDetails fails with InvalidArgument and nothing changes

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** SetBusinessDetails fails with NotFound
