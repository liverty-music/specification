# Admin Area Names

## Purpose

The `live-events` capability defines the core domain entities—Artists, Venues, and Concerts—and the standard interfaces for managing them. It establishes the single source of truth for concert metadata, enabling consistent data representation and access across the platform's crawler, backend services, and frontend applications.

## Requirements

### Requirement: Display localized admin-area names

The frontend SHALL convert ISO 3166-2 codes to human-readable names for display, using the browser's locale for language selection.

#### Scenario: Display admin_area in venue detail

- **WHEN** a venue's `admin_area` ISO 3166-2 code is displayed to the user
- **THEN** the frontend SHALL render the localized name (e.g., `JP-13` → "東京都" for `ja`, "Tokyo" for `en`)

#### Scenario: Display home area in region setup

- **WHEN** the region setup sheet presents area options to the user
- **THEN** the options SHALL display localized names
- **AND** the selected value sent to the backend SHALL be structured as a `Home` message with `country_code` and `level_1`
