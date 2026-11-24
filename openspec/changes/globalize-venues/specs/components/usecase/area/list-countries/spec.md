## Purpose

AreaUseCase.ListCountries gives a member placing an event the countries and territories a venue can be in, for the country choice before the area choice.

## ADDED Requirements

### Requirement: The countries that have Areas

ListCountries SHALL return the result of Area.ListCountries unchanged, failures included. It SHALL store nothing.

#### Scenario: Countries listed

- **WHEN** ListCountries is called
- **THEN** the countries returned by Area.ListCountries, `JP` and `KR` among them, are returned

#### Scenario: Failure returned unchanged

- **WHEN** Area.ListCountries fails with Unavailable
- **THEN** ListCountries fails with Unavailable
