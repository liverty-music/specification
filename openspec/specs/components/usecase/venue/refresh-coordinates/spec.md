# components/usecase/venue/refresh-coordinates Specification

## Purpose
VenueUseCase.RefreshCoordinates keeps each Venue's coordinates, which are a cache of the map catalog, no older than the catalog's terms allow: once a day it reads again the coordinates that are missing or older than 20 days and removes every coordinate older than 30 days.

## Requirements

### Requirement: Refresh due coordinates, then remove expired ones

RefreshCoordinates SHALL take the instant the run starts and list the Venues due for a refresh at that instant (Venue.ListCoordinatesDue) with a maximum count of 1,000. For each listed Venue, one at a time, it SHALL read the place's coordinates by its place id from the map catalog (Venue.GetPlaceCoordinates) and:

- when coordinates are returned, store them with the time they were read (Venue.SetCoordinates);
- when the map catalog has no such place (NotFound), remove the Venue's coordinates (Venue.SetCoordinates with no coordinates);
- when the place has no coordinates, or on any other failure, leave the Venue unchanged and continue with the next Venue.

Nothing but the coordinates and their fetch time SHALL change on the Venue. After the listed Venues, and also when listing failed, RefreshCoordinates SHALL remove every coordinate fetched more than 30 days before the run's start (Venue.ClearExpiredCoordinates). It SHALL fail when listing, removing expired coordinates or reading any Venue's coordinates failed other than with NotFound, after doing the rest.

#### Scenario: Coordinates refreshed
- **WHEN** a Venue's coordinates were fetched 21 days before the run and the map catalog returns its place's coordinates
- **THEN** the Venue holds the coordinates just read, with the time they were read, and keeps its name, admin area and time zone

#### Scenario: Place no longer exists
- **WHEN** the map catalog has no place with a listed Venue's place id
- **THEN** the Venue's coordinates are removed and its place id is kept

#### Scenario: More than 1,000 due
- **WHEN** 1,200 Venues are due at the run's start
- **THEN** the 1,000 listed first are refreshed and the other 200 are left for a later run

#### Scenario: Catalog down for the whole run
- **WHEN** every read from the map catalog fails with Unavailable, one Venue's coordinates were fetched 31 days before the run and another's 25 days before
- **THEN** the first Venue's coordinates are removed, the second's are kept, and the run fails

### Requirement: RefreshCoordinates runs daily

Once a day at 04:00 Japan time, RefreshCoordinates SHALL run with the run's start as its instant. A failed run is not repeated the same day; the coordinates it could not refresh are listed again by the next day's run.

#### Scenario: Daily run
- **WHEN** it is 04:00 Japan time
- **THEN** RefreshCoordinates runs once with that instant

#### Scenario: Retried the next day
- **WHEN** a run fails to read the coordinates of a Venue whose coordinates were fetched 21 days before it
- **THEN** the next day's run lists that Venue again and keeps its coordinates until they are more than 30 days old
