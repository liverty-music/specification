## ADDED Requirements

### Requirement: Idempotent venue get-or-create with place_id-authoritative identity

The venue lookup-or-create path SHALL be idempotent and SHALL NOT fail when a venue
matching the resolved identity already exists. This path runs only when a staged concert is
approved (the sole caller that creates a `venues` row), and it supersedes the insert-only
create step described by the "Venue Resolution During Concert Creation" requirement. Identity
SHALL be resolved in this order:
(1) by `google_place_id` when the staged/scraped concert carries one; (2) on miss, by
`(listed_venue_name, admin_area)`; (3) only when neither matches SHALL a new `venues`
row be created. Creation SHALL use `INSERT … ON CONFLICT DO NOTHING` (untargeted, so a
violation on either the `google_place_id` partial-unique index or the
`(listed_venue_name, admin_area)` partial-unique index is absorbed) followed by a
re-SELECT on the same keys, so a lost race or a divergent identity resolves to the
existing row rather than surfacing an `already_exists` error.

The `admin_area` used for the `(listed_venue_name, admin_area)` fallback lookup and the
`admin_area` written on insert SHALL be derived identically (the resolved admin_area when
present, otherwise the raw scraped admin_area), so the read key and the write key never
diverge.

When the fallback lookup finds a venue whose `google_place_id` is NULL and the incoming
concert carries a resolved `google_place_id`, the system MAY backfill that value; it
SHALL NEVER overwrite an existing non-NULL `google_place_id`.

#### Scenario: No existing venue — a new row is created

- **WHEN** neither `google_place_id` nor `(listed_venue_name, admin_area)` matches an
  existing venue
- **THEN** the system SHALL insert a new `venues` row for the resolved identity
- **AND** SHALL return the newly created venue id

#### Scenario: Existing venue found by place_id

- **WHEN** a venue with the resolved `google_place_id` already exists
- **THEN** the system SHALL return that venue
- **AND** SHALL NOT attempt an insert

#### Scenario: place_id miss falls back to listed name and admin_area

- **WHEN** the resolved `google_place_id` does not match any existing venue
- **AND** a venue with the same `(listed_venue_name, admin_area)` already exists (with a
  different or NULL `google_place_id`)
- **THEN** the system SHALL return that existing venue
- **AND** SHALL NOT attempt to insert a new venue row
- **AND** SHALL NOT raise `already_exists`

#### Scenario: Concurrent create resolves to a single row

- **WHEN** two approvals resolve the same venue identity concurrently and both reach the
  insert step
- **THEN** the `ON CONFLICT DO NOTHING` insert SHALL suppress the losing insert
- **AND** the losing path SHALL re-SELECT by `google_place_id` then by
  `(listed_venue_name, admin_area)` and return the surviving row

#### Scenario: Fallback lookup and insert use the same admin_area

- **WHEN** a concert has a raw `admin_area` and no resolved `admin_area`
- **THEN** the fallback lookup and any subsequent insert SHALL both use the raw
  `admin_area`
- **AND** the lookup SHALL therefore match a row the insert would have collided with

#### Scenario: NULL place_id backfilled, non-NULL never overwritten

- **WHEN** the fallback finds an existing venue whose `google_place_id` is NULL
- **AND** the incoming concert carries a resolved `google_place_id`
- **THEN** the system MAY set the existing row's `google_place_id` to the resolved value
- **WHEN** the existing venue already has a non-NULL `google_place_id`
- **THEN** the system SHALL leave it unchanged
