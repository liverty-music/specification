## ADDED Requirements

### Requirement: Country and area of each place

SearchPlace SHALL return each place with the country its address names and the first-level Area its address stands for, found as Venue.GetPlace suggests an Area: the country itself when it is its own first-level Area (such as HK), otherwise the Area that the region's full name, then its short name, resolves to within the country (see Area.Resolve). Either is absent when the catalog does not tell it.

#### Scenario: Country and area of each place
- **WHEN** the catalog's match has an address in California, United States
- **THEN** the returned place carries the country US and the first-level Area US-CA

#### Scenario: Territory without subdivisions
- **WHEN** the catalog's match has an address in Hong Kong
- **THEN** the returned place carries the country HK and the first-level Area HK

#### Scenario: Address without a country
- **WHEN** the catalog's match has no address
- **THEN** the returned place carries neither a country nor an Area
