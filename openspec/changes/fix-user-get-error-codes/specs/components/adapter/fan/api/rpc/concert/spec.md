# Spec Delta

## MODIFIED Requirements

### Requirement: ListByFollower acts for the signed-in fan with their stored home

ListByFollower SHALL resolve the signed-in caller to their stored User (User.GetByExternalID) and call ConcertUseCase.ListByFollowerGrouped with that User, the User's stored Home and the optional from-date of the request; the request carries no fan and no home. When the caller has no stored account, the call SHALL fail with NotFound.

#### Scenario: Fan with a home

- **WHEN** a signed-in fan whose Home is JP-13 calls ListByFollower
- **THEN** the concerts of the fan's followed artists are grouped by proximity to JP-13

#### Scenario: Caller without an account

- **WHEN** the signed-in caller has no stored account
- **THEN** the call fails with NotFound
