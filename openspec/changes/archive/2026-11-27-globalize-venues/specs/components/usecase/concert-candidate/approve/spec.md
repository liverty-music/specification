## MODIFIED Requirements

### Requirement: The venue is found or created

Approve SHALL take an optional admin area (a code or a name) and an optional time zone from the admin, and decide the Venue's admin area and time zone before any change:

- the admin area SHALL be the first-level Area that the admin's area resolves to (Area.Resolve) when the admin gives one, and the one the ConcertCandidate's admin area resolves to otherwise;
- the time zone SHALL be the admin's when the admin gives one; otherwise the time zone of that Area when it has one; otherwise the ConcertCandidate's time zone when it is one of the time zones of the Area's country.

Approve SHALL fail with InvalidArgument and change nothing when no admin area can be decided (the admin's area does not resolve, or the admin gives none and the ConcertCandidate's is absent or does not resolve), when no time zone can be decided, or when the admin's time zone is not one a Venue in that Area may have (see Venue, "Time zone of a venue").

Approve SHALL then find or create the Venue for the ConcertCandidate in this order: by resolved place id (Venue.GetByPlaceID); by listed venue name and that admin area (Venue.GetByListedName), giving that Venue the resolved place id when it has none (Venue.BackfillPlaceID); otherwise by creating it (Venue.Create) named by the listed venue name, with the listed venue name, that admin area and that time zone, and, when the ConcertCandidate has a resolved place id, that place id and the place's coordinates read from the map catalog by it (Venue.GetPlaceCoordinates) with the time they were read. A Venue that is found keeps its own name, admin area and time zone. When reading the coordinates fails with Unavailable, Approve SHALL fail with Unavailable and change nothing; when the map catalog has no such place or no coordinates for it, the Venue SHALL be created with the place id and without coordinates. A start or open time of the ConcertCandidate that does not exist on its date in the Venue's time zone, because the clocks skip it, SHALL be published as unknown.

#### Scenario: Time skipped at the venue
- **WHEN** a ConcertCandidate on 2027-03-14 that starts at 02:30 is approved at a Venue in America/New_York
- **THEN** the Event is published without a start time

#### Scenario: Unresolved concert candidate
- **WHEN** a ConcertCandidate with no resolved place id, admin area JP-13 and no time zone is approved and no Venue lists its name in JP-13
- **THEN** a Venue named after the listed venue name, in JP-13 with time zone Asia/Tokyo, with no place id and no coordinates, is created

#### Scenario: New venue at a resolved place
- **WHEN** a ConcertCandidate listing "Zepp Haneda(TOKYO)" in JP-13 with resolved place id P, which no Venue holds, is approved
- **THEN** a Venue named "Zepp Haneda(TOKYO)" is created with place id P and the coordinates just read for P with their fetch time

#### Scenario: Different place id for a stored venue
- **WHEN** the resolved place id matches no Venue but a Venue holds the listed venue name and admin area with no place id
- **THEN** that Venue is used and takes the resolved place id

#### Scenario: Admin gives the area and the time zone
- **WHEN** a ConcertCandidate without an admin area or a time zone is approved with the area "California" and the time zone America/Los_Angeles
- **THEN** its Venue is found or created in US-CA, and a created Venue has the time zone America/Los_Angeles

#### Scenario: Area still unknown
- **WHEN** a ConcertCandidate without an admin area is approved without an area
- **THEN** Approve fails with InvalidArgument and nothing changes

#### Scenario: Area the admin gives does not resolve
- **WHEN** an admin approves with the area JP-99
- **THEN** Approve fails with InvalidArgument and nothing changes

#### Scenario: Candidate staged with a lower-level code
- **WHEN** a ConcertCandidate staged with admin area FR-33 is approved without an area or a time zone
- **THEN** its Venue is found or created in FR-NAQ, and a created Venue has the time zone Europe/Paris

#### Scenario: Time zone still unknown
- **WHEN** a ConcertCandidate in US-TX, which has no time zone of its own, and without a time zone is approved without a time zone
- **THEN** Approve fails with InvalidArgument and nothing changes

#### Scenario: Time zone of another country
- **WHEN** an admin approves a ConcertCandidate in US-TX with the time zone Asia/Tokyo
- **THEN** Approve fails with InvalidArgument and nothing changes

#### Scenario: Time zone other than the Area's own
- **WHEN** an admin approves a ConcertCandidate in US-CA, whose time zone is America/Los_Angeles, with the time zone America/New_York
- **THEN** Approve fails with InvalidArgument and nothing changes

#### Scenario: Catalog down while creating the venue
- **WHEN** a new Venue must be created for a resolved place id and reading its coordinates fails with Unavailable
- **THEN** Approve fails with Unavailable and the ConcertCandidate is kept
