# concert-detail Specification

## Purpose

The Concert Detail capability provides users with a rich detail view for a selected concert, including venue information, time, and entry points for ticket purchase. It also defines the logic for assigning concerts to dashboard lanes based on the user's stored region preference.

## Requirements

### Requirement: Concert Detail View

The system SHALL provide a detail view for a selected concert that surfaces full event information and entry points for ticket purchase.

#### Scenario: Open detail from dashboard

- **WHEN** a user taps a concert card on the dashboard
- **THEN** the system SHALL open a bottom sheet displaying the concert detail
- **AND** the URL SHALL update to `/concerts/:id` without triggering full page navigation

#### Scenario: Display venue information

- **WHEN** the concert detail view is open
- **THEN** it SHALL display the venue name (`listed_venue_name`) and administrative area (`venue.admin_area`) if available

#### Scenario: Google Maps link

- **WHEN** the concert detail view is open
- **THEN** it SHALL render a tappable link that opens Google Maps with a query composed of venue name and admin area

#### Scenario: Ticket / official info link

- **WHEN** the concert detail view is open and `source_url` is present
- **THEN** it SHALL render a "View Official Info" button linking to `source_url` in a new tab

#### Scenario: Dismiss sheet

- **WHEN** the user swipes down or taps the backdrop
- **THEN** the sheet SHALL close and the URL SHALL revert to the dashboard URL

### Requirement: Dashboard Lane Assignment

The system SHALL assign concerts to one of three lanes — My City, My Region, Others — based on the concert's `venue.admin_area` relative to the user's stored region preference.

#### Scenario: Concert in user's city/prefecture

- **WHEN** a concert's `venue.admin_area` matches the user's stored region exactly
- **THEN** the concert SHALL be placed in the `main` (My City) lane

#### Scenario: Concert in a different prefecture

- **WHEN** a concert's `venue.admin_area` does not match the user's stored region
- **THEN** the concert SHALL be placed in the `other` lane

#### Scenario: Venue admin area not available

- **WHEN** a concert has no `venue.admin_area`
- **THEN** the concert SHALL be placed in the `other` lane
