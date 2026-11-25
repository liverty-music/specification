## ADDED Requirements

### Requirement: Returning Guest Redirect

The system SHALL redirect an unauthenticated guest whose onboarding is complete and who follows at least one artist away from the landing page to the Timetable. A guest still in onboarding, and a guest who follows no artist, SHALL still be able to load the landing page. The redirect SHALL NOT discard any guest data, and the landing page's `[Log In]` SHALL keep discarding the guest follows and home before it starts sign-in.

#### Scenario: Returning guest opens the app

- **WHEN** an unauthenticated user whose onboarding is complete and who follows at least one artist navigates to `/`
- **THEN** the system SHALL redirect to the Timetable

#### Scenario: Guest in onboarding opens Welcome

- **WHEN** an unauthenticated user still in onboarding navigates to `/`, whether or not they follow an artist
- **THEN** the system SHALL load the landing page

#### Scenario: Guest with no follows opens Welcome

- **WHEN** an unauthenticated user whose onboarding is complete but who follows no artist (a signed-out fan, or a guest who tapped `[Log In]` and came back without signing in) navigates to `/`
- **THEN** the system SHALL load the landing page

## MODIFIED Requirements

### Requirement: The screen's address

The welcome page SHALL be served at `/welcome`, and `/` SHALL lead to it, except that `/` leads a returning guest, as "Returning Guest Redirect" defines, to the Timetable.

#### Scenario: The page's address
- **WHEN** a guest who is not a returning guest opens `/`
- **THEN** the app shows the welcome page at `/welcome`
