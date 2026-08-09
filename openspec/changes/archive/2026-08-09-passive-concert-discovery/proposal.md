## Why

Users can already see upcoming concerts for artists they follow, but have no way to passively discover concerts happening near them — the "I wonder what's on this weekend?" use case is unaddressed. Adding location-and-date-driven concert browsing directly into the Dashboard covers this gap without introducing a new navigation tab.

## What Changes

- Dashboard gains a "My Timetable / All Nearby" toggle; "All Nearby" mode shows all concerts in the DB within 200 km of a chosen location and date range
- New `entity.v1.GeoLocation` proto message — a geographic reference point (lat/lng + admin_area) distinct from the user-specific `Home` entity
- New RPC `ConcertService.ListByLocation` — returns concerts near a `GeoLocation` within a date range, grouped by proximity, no auth required
- **BREAKING**: `ConcertService.ListWithProximity` renamed to `ListByArtists` — its primary filter has always been `artist_ids`; "WithProximity" described the output format, not the filter
- `UserHomeSelector` component refactored — selection and persistence responsibilities separated so the component is reusable without saving to account

## Capabilities

### New Capabilities

- `geo-location`: Introduces `entity.v1.GeoLocation` proto message (latitude, longitude, admin_area) as a reusable geographic reference point for proximity-based queries
- `passive-concert-discovery`: `ConcertService.ListByLocation` RPC and the "All Nearby" Dashboard mode — date-range and location-driven concert browsing for all artists in the DB

### Modified Capabilities

- `concert-service`: Adds `ListByLocation` RPC; renames `ListWithProximity` → `ListByArtists` (**BREAKING**)
- `dashboard-concert-cache`: Dashboard view gains a mode toggle; "All Nearby" mode introduces date-preset and area-override filters
- `artist-following`: `UserHomeSelector` responsibility split — caller now owns persistence; follow CTA moves to `EventDetailSheet`

## Impact

- **Proto / BSR**: New `entity/v1/geo_location.proto`; `concert/v1/concert_service.proto` updated (new RPC + rename) → minor BSR version bump, breaking rename requires semver major or buf lint suppression with deprecation comment
- **Backend**: New `ConcertRepository.ListByLocation` query (date + proximity filter); new `ConcertService` handler; `ListByArtists` handler (rename only)
- **Frontend**: Dashboard route updated (toggle, filters, `ListByLocation` call); `UserHomeSelector` refactored; `EventDetailSheet` gains follow CTA for unfollowed artists; FE centroid constants added for 47 JP prefectures
- **Spec repo**: `concert/v1`, `entity/v1` proto files
