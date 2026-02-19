# Frontend Route Guard

## Purpose

Global authentication guard for frontend routing. Protects all non-public routes by checking the user's authentication state before allowing navigation, redirecting unauthenticated users to the landing page.

## Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook that checks the user's authentication state before loading protected route components.

**Rationale**: A centralized guard eliminates the need for per-component `canLoad` implementations, reducing the risk of unprotected routes.

#### Scenario: Unauthenticated user navigates to protected route

- **WHEN** a user who is not authenticated navigates to a route without `data: { auth: false }`
- **THEN** the system SHALL prevent the route component from loading
- **AND** display a toast notification ("ログインが必要です")
- **AND** redirect the user to the landing page (`/`)

#### Scenario: Authenticated user navigates to protected route

- **WHEN** a user who is authenticated navigates to a route without `data: { auth: false }`
- **THEN** the system SHALL allow the route component to load normally

#### Scenario: Any user navigates to public route

- **WHEN** any user navigates to a route with `data: { auth: false }`
- **THEN** the system SHALL allow the route component to load regardless of authentication state

### Requirement: Declarative Route Protection via Metadata

The system SHALL use a default-deny approach: all routes require authentication unless explicitly marked as public with `data: { auth: false }`.

**Rationale**: Default-deny eliminates the risk of accidentally exposing a new route without authentication. Only routes that are explicitly public need annotation.

#### Scenario: Protected route configuration (default)

- **WHEN** a route is defined without `data: { auth: false }`
- **THEN** the `AuthHook.canLoad()` lifecycle hook SHALL enforce authentication before loading that route's component

#### Scenario: Public route configuration

- **WHEN** a route is defined with `data: { auth: false }`
- **THEN** no authentication check SHALL be performed for that route

### Requirement: Protected Route Definitions

The following routes SHALL be protected (no `data` annotation needed, default-deny):
- `/onboarding/discover` (Artist Discovery)
- `/onboarding/loading` (Loading Sequence)
- `/dashboard` (Dashboard)

The following routes SHALL be marked public with `data: { auth: false }`:
- `/` and `/welcome` (Landing Page)
- `/about` (About Page)
- `/auth/callback` (OIDC Callback)

**Rationale**: The landing page, about page, and auth callback must be accessible without authentication. All other routes are protected by default.

#### Scenario: Direct URL access to dashboard without authentication

- **WHEN** an unauthenticated user enters `/dashboard` directly in the browser address bar
- **THEN** the system SHALL redirect to the landing page (`/`)

#### Scenario: Direct URL access to onboarding without authentication

- **WHEN** an unauthenticated user enters `/onboarding/discover` directly in the browser address bar
- **THEN** the system SHALL redirect to the landing page (`/`)

### Requirement: Auth State Readiness

The auth hook SHALL wait for the authentication service to complete its initialization before evaluating the authentication state.

**Rationale**: On page reload, `oidc-client-ts` asynchronously restores the session from storage. The guard must wait for this to complete to avoid incorrectly redirecting authenticated users.

#### Scenario: Page reload on protected route with valid session

- **WHEN** an authenticated user reloads the browser on a protected route
- **AND** the auth service has not yet finished restoring the session
- **THEN** the system SHALL wait for `authService.ready` to resolve
- **AND** allow navigation if the session is valid

### Requirement: Remove Per-Component canLoad Guards

Existing per-component `canLoad` guards for authentication checks SHALL be removed from individual route components and replaced by the global `AuthHook`.

**Rationale**: Consolidating auth logic into a single hook eliminates duplication and ensures consistent behavior across all protected routes.

#### Scenario: Loading sequence component

- **WHEN** the `LoadingSequence` component is loaded
- **THEN** the component SHALL NOT contain its own `canLoad` authentication check
- **AND** authentication SHALL be enforced by the global `AuthHook` via route metadata
