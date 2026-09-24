<!-- spec: user-home | target: stories/set-home-area | flags: CLASSNAME | new_name: Home area persists across onboarding, settings, and dashboard -->

### Requirement: Home area persists across onboarding, settings, and dashboard

The frontend SHALL store the user's home area server-side via RPC, replacing
local-storage-based persistence for authenticated users. Home area SHALL be owned
by a single user data store, which resolves its source (guest local storage vs the
authenticated user's record) internally; callers SHALL read home from
the user store and SHALL NOT branch on authentication state.

#### Scenario: Onboarding home area selection persisted at account creation

- **WHEN** a guest user has selected their home area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL include the selected home (read from the user
  store's guest view) in the `UserService.Create` request
- **AND** SHALL NOT make a separate home-update call for the initial home
- **AND** the user store SHALL clear its own guest home local storage on success

#### Scenario: Settings home area change triggers a home update

- **WHEN** an authenticated user changes their home area via the home-area selector
- **THEN** the frontend SHALL call the backend to update the home with the new structured home
- **AND** SHALL NOT write to local storage for the home area

#### Scenario: Dashboard reads home from the user store

- **WHEN** the dashboard loads
- **THEN** the lane assignment logic SHALL read the home area from the user store
- **AND** SHALL NOT fetch the user profile independently
- **AND** SHALL NOT branch on authentication state to choose the source

#### Scenario: Settings reads home from the user store

- **WHEN** the settings page loads
- **THEN** the My Home Area display SHALL read from the user store
- **AND** SHALL NOT branch on authentication state at the call site

#### Scenario: Guest home sourced from store-backed localStorage

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** the user store SHALL store the selection in local storage
- **AND** the dashboard and settings SHALL read the home area from the user
  store's observable value (which stays reactive when the guest changes it)

#### Scenario: Dashboard reloads data after authenticated home change

- **WHEN** an authenticated user changes their home area via the home-area selector on the dashboard
- **THEN** the dashboard SHALL reload concert data after the home update completes
- **AND** the reloaded data SHALL reflect the new lane classification based on the updated home
