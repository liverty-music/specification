## ADDED Requirements

### Requirement: Country and area of each place

SearchPlace SHALL return each place with the country its address names and the first-level Area its address stands for, found as Venue.GetPlace suggests an Area: the country itself when it is its own first-level Area (such as HK), otherwise the Area that the region's full name, then its short name, resolves to within the country (see Area.Resolve). The country is absent when the address names none; the Area is absent when the country is, or when neither the country nor the region stands for an Area. Neither case is an error.

#### Scenario: Country and area of each place
- **WHEN** the catalog's match has an address in California, United States
- **THEN** the returned place carries the country US and the first-level Area US-CA

#### Scenario: Territory without subdivisions
- **WHEN** the catalog's match has an address in Hong Kong
- **THEN** the returned place carries the country HK and the first-level Area HK

#### Scenario: Region that matches no Area
- **WHEN** the catalog's match has a United States address whose region stands for no Area
- **THEN** the returned place carries the country US and no Area

#### Scenario: Address without a country
- **WHEN** the catalog's match has no address
- **THEN** the returned place carries neither a country nor an Area
