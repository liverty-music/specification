# Organizer Shell

## Purpose

The organizer (seller) frontend shell: a dedicated `organizer.html` entry,
bundle-isolated from the consumer SPA and admin console, authenticated
against the operator's own Zitadel tenant org via org-pinned entry, with a
role-claim route guard and a post-login placeholder. Business screens land
in later changes.

## Requirements

### Requirement: Route guard admits only owner-role operators

The organizer console SHALL guard its routes: unauthenticated visitors are
sent to sign-in, and an authenticated user is admitted only if the token's
`organizer-console` project roles include `owner`; otherwise access is
denied. The backend remains the source of truth for authorization; the guard
is a UX gate. On success the operator lands on a post-login welcome
placeholder.

#### Scenario: Unauthenticated visitor is redirected to sign-in

- **WHEN** an unauthenticated visitor navigates to an organizer console route
- **THEN** the guard SHALL redirect them to Zitadel sign-in

#### Scenario: Authenticated operator with owner role sees the placeholder

- **WHEN** an authenticated operator whose token carries the `owner` role
  loads the console
- **THEN** they SHALL see the post-login welcome placeholder

#### Scenario: Authenticated account without the owner role is denied

- **WHEN** an authenticated user whose token lacks the `owner` role loads
  the console
- **THEN** the guard SHALL deny access to organizer screens
