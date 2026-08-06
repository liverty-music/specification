## MODIFIED Requirements

### Requirement: Database tables SHALL NOT include metadata timestamp columns

Application tables SHALL NOT include `created_at` or `updated_at` columns for audit purposes. Business-meaningful timestamps (e.g., `start_at`, `open_at`, `searched_at`, `scheduled_at`, `sent_at`) SHALL be retained. (The `tickets.minted_at` and `nullifiers.used_at` columns are removed along with the blockchain ticket schema under the Scenario A pivot.)

#### Scenario: Metadata timestamps removed from all tables

- **WHEN** the migration is applied
- **THEN** the following columns SHALL be dropped:
  - `users.created_at`, `users.updated_at`
  - `events.created_at`, `events.updated_at`
  - `venues.created_at`, `venues.updated_at`
  - `artist_official_site.created_at`, `artist_official_site.updated_at`
  - `followed_artists.created_at`
  - `notifications.created_at`, `notifications.updated_at`
- **AND** `schema.sql` SHALL NOT contain `created_at` or `updated_at` in any table definition

#### Scenario: Business timestamps are preserved

- **WHEN** the migration is applied
- **THEN** the following columns SHALL remain unchanged:
  - `events.start_at`, `events.open_at`
  - `latest_search_logs.searched_at`
  - `notifications.scheduled_at`, `notifications.sent_at`
