## MODIFIED Requirements

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via RPC, replacing
localStorage-based persistence for authenticated users. Home area SHALL be owned
by `UserStore`, which resolves its source (guest localStorage vs the
authenticated `User` entity) internally; callers SHALL read home from
`UserStore` and SHALL NOT branch on `auth.isAuthenticated`.

#### Scenario: Onboarding home area selection persisted at account creation

- **WHEN** a guest user has selected their home area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL include the selected home (read from `UserStore`'s
  guest view) in the `UserService.Create` request
- **AND** SHALL NOT make a separate `UpdateHome` call for the initial home
- **AND** `UserStore` SHALL clear its own guest home localStorage on success

#### Scenario: Settings home area change triggers UpdateHome RPC

- **WHEN** an authenticated user changes their home area via the `user-home-selector`
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the new structured home
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from the user store

- **WHEN** the dashboard loads
- **THEN** the lane assignment logic SHALL read the home area from `UserStore`
- **AND** SHALL NOT call `UserService.Get` independently
- **AND** SHALL NOT branch on `auth.isAuthenticated` to choose the source

#### Scenario: Settings reads home from the user store

- **WHEN** the settings page loads
- **THEN** the My Home Area display SHALL read from `UserStore`
- **AND** SHALL NOT read `I18N.getLocale()` or branch on auth state at the call site

#### Scenario: Guest home sourced from store-backed localStorage

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** `UserStore` SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard and settings SHALL read the home area from `UserStore`'s
  observable value (which stays reactive when the guest changes it)

#### Scenario: Dashboard reloads data after authenticated home change

- **WHEN** an authenticated user changes their home area via the `user-home-selector` on the dashboard
- **THEN** the dashboard SHALL reload concert data via `loadDashboardEvents()` after the home update completes
- **AND** the reloaded data SHALL reflect the new lane classification based on the updated home
