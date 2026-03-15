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
- **THEN** the frontend SHALL call `UserService.updateHome()` with the new structured home
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from hydrated User entity

- **WHEN** the dashboard loads for an authenticated user
- **THEN** the lane assignment logic SHALL read the user's home area from `UserService.current.home` (the hydrated in-memory User entity)
- **AND** SHALL NOT call `UserService.Get` independently
- **AND** SHALL NOT read from localStorage

#### Scenario: Settings reads home from hydrated User entity

- **WHEN** the settings page loads for an authenticated user
- **THEN** the My Home Area display SHALL read from `UserService.current.home` (the hydrated in-memory User entity)
- **AND** SHALL NOT read from localStorage

#### Scenario: Guest fallback to localStorage

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** the frontend SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard and settings SHALL read from localStorage for home area display
