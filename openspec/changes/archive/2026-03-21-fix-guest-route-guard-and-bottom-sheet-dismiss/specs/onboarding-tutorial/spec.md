## ADDED Requirements

### Requirement: Completed guest route access control

The system SHALL restrict `isCompleted` guests (onboarding finished, not signed up) to a defined set of routes. Accessing an auth-required route SHALL NOT navigate away from the current page; instead the system SHALL display a "login required" toast and cancel the navigation.

#### Scenario: Completed guest accesses an allowed route

- **WHEN** a user has `onboarding.isCompleted === true` and is not authenticated
- **AND** the user navigates to a route with `data.onboardingStep` of `'dashboard'`, `'discovery'`, or `'my-artists'`
- **THEN** the auth hook SHALL return `true` and allow navigation

#### Scenario: Completed guest accesses tickets

- **WHEN** a user has `onboarding.isCompleted === true` and is not authenticated
- **AND** the user taps the Tickets tab in the bottom navigation bar
- **THEN** the auth hook SHALL return `false` to cancel the navigation
- **AND** the system SHALL publish a `Snack` with key `auth.loginRequired` and variant `'warning'`
- **AND** the user SHALL remain on the current page

#### Scenario: Completed guest accesses settings

- **WHEN** a user has `onboarding.isCompleted === true` and is not authenticated
- **AND** the user taps the Settings tab in the bottom navigation bar
- **THEN** the auth hook SHALL return `false` to cancel the navigation
- **AND** the system SHALL publish a `Snack` with key `auth.loginRequired` and variant `'warning'`
- **AND** the user SHALL remain on the current page

#### Scenario: Completed guest accesses a route with no onboardingStep

- **WHEN** a user has `onboarding.isCompleted === true` and is not authenticated
- **AND** the user navigates to a route that has no `data.onboardingStep` (e.g., about, settings)
- **THEN** the auth hook SHALL return `false` to cancel navigation
- **AND** the system SHALL publish a `Snack` with key `auth.loginRequired` and variant `'warning'`

### Requirement: Guest home selection persistence

The system SHALL persist the guest's home area selection to localStorage regardless of whether the user is mid-onboarding or has completed onboarding. This prevents the `user-home-selector` from re-appearing on subsequent dashboard visits.

#### Scenario: isCompleted guest selects home area on dashboard

- **WHEN** an `isCompleted` guest (not mid-onboarding) selects a home area on the dashboard
- **THEN** `dashboard-route.ts` SHALL dispatch `guest/setUserHome` with the selected code
- **AND** the persistence middleware SHALL save the home area to localStorage
- **AND** the `user-home-selector` SHALL NOT re-appear on next dashboard visit

#### Scenario: Mid-onboarding guest selects home area

- **WHEN** a guest in onboarding Step 3 (dashboard) selects a home area
- **THEN** `dashboard-route.ts` SHALL dispatch `guest/setUserHome` with the selected code
- **AND** the persistence middleware SHALL save the home area to localStorage
- **AND** the lane intro sequence SHALL start

#### Scenario: Authenticated user selects home area

- **WHEN** an authenticated user selects a home area on the dashboard
- **THEN** the system SHALL NOT dispatch `guest/setUserHome` (backend handles persistence via RPC)
