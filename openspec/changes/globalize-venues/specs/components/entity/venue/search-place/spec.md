## ADDED Requirements

### Requirement: Country and area of each place

SearchPlace SHALL return each place with the country its address names and, when the address names a first-level area that stands for an Area of that country (see Area.Resolve), that first-level Area; either is absent when the catalog does not tell it.

#### Scenario: Country and area of each place
- **WHEN** the catalog's match has an address in California, United States
- **THEN** the returned place carries the country US and the first-level Area US-CA

#### Scenario: Address without a country
- **WHEN** the catalog's match has no address
- **THEN** the returned place carries neither a country nor an Area
