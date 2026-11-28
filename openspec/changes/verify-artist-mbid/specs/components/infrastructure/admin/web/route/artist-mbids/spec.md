## Purpose

The admin console's Artist MBIDs screen lists the artists whose MBID could not be verified automatically and lets an admin compare each one's namesakes in the music catalog and choose the right MBID.

## ADDED Requirements

### Requirement: The screen lists the ambiguous artists

The admin console's navigation SHALL offer `Artist MBIDs`. The screen SHALL list the Artists that ArtistService.ListByMbidStatus returns for Ambiguous, oldest first, each with its name and MBID. When there is none, it SHALL show `No artist is waiting for an MBID choice.`

#### Scenario: Two ambiguous artists

- **WHEN** the admin opens the screen while two artists are Ambiguous
- **THEN** both are listed with their names and MBIDs

#### Scenario: Nothing to choose

- **WHEN** no artist is Ambiguous
- **THEN** the screen shows `No artist is waiting for an MBID choice.`

### Requirement: Selecting an artist shows its namesakes

Selecting a listed artist SHALL read CatalogArtistService.ListByArtist for it and show each CatalogArtist in the returned order with its name, country, life span, shown as one of `<begin> to <end>`, `<begin> ended`, `<begin> active`, `to <end>`, `ended` or `active`: the begin when there is one, then `to` and the end when there is an end, otherwise `ended` when activity_ended is true and `active` when it is false, disambiguation and official site as a link. Each MBID SHALL link to the artist's page in the music catalog, opening in a new tab. The artist's current MBID SHALL be labelled `Current`. While the read is in progress the list shows `Loading namesakes…`; when it fails, the screen SHALL show `The music catalog could not be reached. Try again.` with a `Try again` button that reads it again.

#### Scenario: Namesakes shown

- **WHEN** the admin selects an artist whose current MBID names a UK band ended in 2002 and whose name a Japanese band with an official site shares
- **THEN** both are shown, the UK band labelled `Current` with life span 1995-10 to 2002-11, the Japanese band with its official site link

#### Scenario: Namesake ended without an end date

- **WHEN** a namesake has begin 1998, no end and activity_ended true
- **THEN** its life span is shown as 1998 and `ended`, not `active`

#### Scenario: Current MBID listed without a life span

- **WHEN** the artist's current MBID is listed first with no begin and no end, and the catalog marks its activity as ended
- **THEN** it is labelled `Current` with life span `ended` alone

#### Scenario: Namesake with an end and no begin

- **WHEN** a namesake has no begin and an end of 2002
- **THEN** its life span is shown as `to 2002`

#### Scenario: Catalog unreachable

- **WHEN** CatalogArtistService.ListByArtist fails with Unavailable
- **THEN** the screen shows `The music catalog could not be reached. Try again.` and `Try again`

### Requirement: Choose sets the artist's MBID after a confirmation

Each namesake SHALL offer `Choose`. Activating it SHALL open a modal confirmation dialog that names the artist and the chosen namesake with its country and life span; Cancel SHALL receive initial focus, and Cancel and Escape SHALL close the dialog without a change. On confirmation the screen SHALL call ArtistService.CorrectMbid with the artist's id and the namesake's MBID. On success the artist SHALL leave the list and the screen SHALL show `<artist name> is verified.` with the name the call returned. When the call fails with AlreadyExists, the screen SHALL show `Another artist already has this MBID.` and keep the artist listed; on any other failure, `The MBID could not be set. Try again.`

#### Scenario: Namesake chosen

- **WHEN** the admin chooses the Japanese band and confirms
- **THEN** ArtistService.CorrectMbid is called with its MBID, the artist leaves the list and the screen shows `Penthouse is verified.`

#### Scenario: Current MBID chosen

- **WHEN** the admin chooses the namesake labelled `Current` and confirms
- **THEN** ArtistService.CorrectMbid is called with the current MBID and the artist leaves the list

#### Scenario: Cancelled

- **WHEN** the admin activates `Choose` and then presses Escape
- **THEN** the dialog closes and no call is made

#### Scenario: MBID already held

- **WHEN** ArtistService.CorrectMbid fails with AlreadyExists
- **THEN** the screen shows `Another artist already has this MBID.` and the artist stays listed
