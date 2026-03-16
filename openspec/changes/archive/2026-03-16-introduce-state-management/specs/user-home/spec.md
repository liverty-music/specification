## MODIFIED Requirements

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via RPC, replacing localStorage-based persistence for authenticated users.

#### Scenario: Onboarding home area selection persisted at account creation

- **WHEN** a guest user has selected their home area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL read the home area from `store.getState().guestArtists.home`
- **AND** include it in the `UserService.Create` request
- **AND** SHALL NOT make a separate `UpdateHome` call for the initial home

#### Scenario: Settings home area change triggers UpdateHome RPC

- **WHEN** an authenticated user changes their home area via the `user-home-selector`
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the new structured home
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

#### Scenario: Guest fallback to Store

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** the frontend SHALL dispatch `{ type: 'guest/setUserHome', code }` to the Store
- **AND** the Store's persistence middleware SHALL write the code to localStorage
- **AND** the dashboard and settings SHALL read from `store.getState().guestArtists.home` for home area display

#### Scenario: Dashboard reloads data after authenticated home change

- **WHEN** an authenticated user changes their home area via the `user-home-selector` on the dashboard
- **THEN** the dashboard SHALL reload concert data via `loadDashboardEvents()` after the home update completes
- **AND** the reloaded data SHALL reflect the new lane classification based on the updated home

### Requirement: Unified Home Area Selector Component

The frontend SHALL provide a single reusable `user-home-selector` component for selecting the user's home area. This component SHALL be used in both the onboarding flow (Dashboard BottomSheet) and the Settings page. The component SHALL implement a consistent 2-step selection flow with an optional quick-select shortcut.

#### Scenario: Guest user home selection dispatches to Store

- **WHEN** a guest user selects a home area via `user-home-selector`
- **THEN** the component SHALL dispatch `{ type: 'guest/setUserHome', code }` to the Store
- **AND** SHALL NOT directly write to localStorage (persistence is handled by middleware)

#### Scenario: Persistence for authenticated users

- **WHEN** an authenticated user selects a home area
- **THEN** the component SHALL call `UserService.updateHome()` with the structured Home object
- **AND** the component SHALL NOT dispatch to the Store
