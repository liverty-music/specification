# Spec Delta

## Purpose

The fan-facing official site service boundary: who may create or delete an artist's official site, and which requests the boundary rejects before OfficialSiteUseCase runs.

## ADDED Requirements

### Requirement: Official site calls need a signed-in caller

Create and Delete SHALL require a signed-in caller and SHALL fail with Unauthenticated, before any usecase runs, when the caller is not signed in. Neither call acts for a particular fan, so no account is looked up.

#### Scenario: Guest creates a site

- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated and no usecase runs

### Requirement: Official site requests are validated at the boundary

Create SHALL fail with InvalidArgument, before any usecase runs, when it has no artist id, an artist id that is not a UUID, or a URL that is not a valid URI of 1 to 2048 characters.

#### Scenario: Malformed URL

- **WHEN** Create is called with a URL longer than 2048 characters
- **THEN** it fails with InvalidArgument and no site is stored

### Requirement: Official sites are created through the boundary but never deleted

Create SHALL hand the artist id and URL to OfficialSiteUseCase.Create. Delete SHALL fail with Unimplemented for every signed-in caller; there is no usecase behind it.

#### Scenario: Create a site

- **WHEN** a signed-in caller calls Create for an artist without a site with a valid URL
- **THEN** the site is stored for the artist

#### Scenario: Delete a site

- **WHEN** a signed-in caller calls Delete
- **THEN** it fails with Unimplemented and nothing changes
