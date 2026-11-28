## Purpose

The admin console's Artist MBIDs screen lists the artists whose MBID could not be verified automatically and lets an admin compare each one's namesakes in the music catalog and choose the right MBID, or enter it when the namesakes do not include it.

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

Selecting a listed artist SHALL read CatalogArtistService.ListByArtist for it and show each CatalogArtist in the returned order with its name, country, life span (begin to end, or begin and `active` when there is no end), disambiguation and official site as a link. Each MBID SHALL link to the artist's page in the music catalog, opening in a new tab. The artist's current MBID SHALL be labelled `Current`. While the read is in progress the list shows `Loading namesakes…`; when it fails, the screen SHALL show `The music catalog could not be reached. Try again.` with a `Try again` button that reads it again.

#### Scenario: Namesakes shown

- **WHEN** the admin selects an artist whose current MBID names a UK band ended in 2002 and whose name a Japanese band with an official site shares
- **THEN** both are shown, the UK band labelled `Current` with life span 1995-10 to 2002-11, the Japanese band with its official site link

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

### Requirement: An admin can enter an MBID the namesakes do not include

Below the namesakes of the selected artist, the screen SHALL offer an `MBID` field and `Set MBID`, for an artist whose right MBID the name search does not find (the catalog records it under another spelling, or no namesake is listed). The screen SHALL refuse a value that is not a UUID of 36 characters with `Enter an MBID of 36 characters.` and make no call. Otherwise `Set MBID` SHALL open the same modal confirmation as `Choose`, naming the artist and the entered MBID, and on confirmation call ArtistService.CorrectMbid with it; success and AlreadyExists are shown as for `Choose`. When the call fails with NotFound, the screen SHALL show `The music catalog has no artist with this MBID.` and keep the artist listed.

#### Scenario: MBID entered for an artist without namesakes

- **WHEN** the selected artist has no namesake listed and the admin enters an MBID the catalog knows and confirms
- **THEN** ArtistService.CorrectMbid is called with that MBID, the artist leaves the list and the screen shows `<artist name> is verified.`

#### Scenario: Malformed MBID entered

- **WHEN** the admin enters `abc` and activates `Set MBID`
- **THEN** the screen shows `Enter an MBID of 36 characters.` and makes no call

#### Scenario: MBID unknown to the catalog

- **WHEN** ArtistService.CorrectMbid fails with NotFound for the entered MBID
- **THEN** the screen shows `The music catalog has no artist with this MBID.` and the artist stays listed

