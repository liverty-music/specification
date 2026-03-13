## MODIFIED Requirements

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via RPC, replacing localStorage-based persistence for authenticated users.

#### Scenario: Onboarding home area selection persisted at account creation

- **WHEN** a guest user has selected their home area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL include the selected home in the `UserService.Create` request
- **AND** SHALL NOT make a separate `UpdateHome` call for the initial home

#### Scenario: Settings home area change triggers UpdateHome RPC

- **WHEN** an authenticated user changes their home area via the `user-home-selector`
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the new structured home
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from User entity

- **WHEN** the dashboard loads for an authenticated user
- **THEN** the dashboard SHALL call `UserService.Get` to obtain the user's home status
- **AND** the `needsRegion` flag SHALL be determined by the presence of `user.home` in the response
- **AND** the dashboard SHALL NOT read from localStorage to determine `needsRegion`

#### Scenario: Guest fallback to localStorage

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** the frontend SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard SHALL read from localStorage for the `needsRegion` determination

#### Scenario: Dashboard reloads data after authenticated home change

- **WHEN** an authenticated user changes their home area via the `user-home-selector` on the dashboard
- **THEN** the dashboard SHALL reload concert data via `loadDashboardEvents()` after the home update completes
- **AND** the reloaded data SHALL reflect the new lane classification based on the updated home
