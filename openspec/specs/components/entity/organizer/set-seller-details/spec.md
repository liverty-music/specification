# components/entity/organizer/set-seller-details Specification

## Purpose
Stores an Organizer's 特商法 (Specified Commercial Transactions Act) seller details as a whole.

## Requirements

### Requirement: Seller details replaced as a whole

SetSellerDetails SHALL replace the Organizer's seller details with the given ones. It SHALL fail with InvalidArgument when any of them is missing or breaks the seller details rules, and with NotFound when no Organizer has the id.

#### Scenario: Details entered at vetting

- **WHEN** an admin sets complete seller details for an Organizer
- **THEN** the Organizer's seller details are complete

#### Scenario: Malformed phone number

- **WHEN** the phone number is `03-1234-5678`
- **THEN** SetSellerDetails fails with InvalidArgument and nothing changes
