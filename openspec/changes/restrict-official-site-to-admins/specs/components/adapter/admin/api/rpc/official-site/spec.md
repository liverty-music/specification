## ADDED Requirements

### Requirement: Official site calls need the admin role

Every official site call reached through the admin console SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied. Both checks come before the request is validated and before any usecase runs.

#### Scenario: Admin creates a site

- **WHEN** a signed-in admin calls Create for an artist without a site with a valid URL
- **THEN** the site is stored for the artist

#### Scenario: Signed-in fan creates a site

- **WHEN** a signed-in caller without the admin role calls Create
- **THEN** the call fails with PermissionDenied and no usecase runs

#### Scenario: Guest creates a site

- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Non-admin updates a site

- **WHEN** a signed-in caller without the admin role calls Update
- **THEN** the call fails with PermissionDenied, no usecase runs and the stored site is unchanged

### Requirement: Official site requests are validated at the boundary

Create and Update SHALL fail with InvalidArgument, before any usecase runs, when the request has no artist id, an artist id that is not a UUID, or a URL that is not a valid URI of 1 to 2048 characters.

#### Scenario: Malformed URL on Create

- **WHEN** an admin calls Create with a URL longer than 2048 characters
- **THEN** it fails with InvalidArgument and no site is stored

#### Scenario: Missing artist id on Update

- **WHEN** an admin calls Update without an artist id
- **THEN** it fails with InvalidArgument and no usecase runs

### Requirement: Create stores the first official site of an artist

Create SHALL hand the artist id and URL to OfficialSiteUseCase.Create and return its error unchanged.

#### Scenario: Artist already has a site

- **WHEN** an admin calls Create for an artist that already has an official site
- **THEN** it fails with AlreadyExists and the existing site is kept

#### Scenario: Unknown artist

- **WHEN** an admin calls Create for an artist id no artist has
- **THEN** it fails with FailedPrecondition and nothing is stored

### Requirement: Update corrects the stored official site

Update SHALL hand the artist id and URL to OfficialSiteUseCase.Update and return its error unchanged.

#### Scenario: Admin corrects a site

- **WHEN** an admin calls Update for an artist whose site is a wrong URL, with the right URL
- **THEN** the artist's official site is the right URL and keeps its id

#### Scenario: Artist without a site

- **WHEN** an admin calls Update for an artist that has no official site
- **THEN** it fails with NotFound and nothing is stored
