# Live Highway

## Purpose

Renders the shared three-lane concert card grid showing each artist's followed events with the artist name, hype-driven visual prominence, and a subtle glow effect on matched cards.

## Requirements

### Requirement: Fanart Data Propagation
The frontend service layer SHALL extract fanart image URLs from the `Artist.fanart` proto field in `FollowService.List` responses and propagate them to the `LiveEvent` and `FollowedArtist` view models for consumption by UI components.

#### Scenario: ListFollowed returns artist with fanart
- **WHEN** the `FollowService.List` RPC returns an artist with populated fanart data
- **THEN** the service layer SHALL map `hd_music_logo`, `music_logo`, `artist_background`, and `artist_thumb` URLs to the corresponding view model fields

#### Scenario: ListFollowed returns artist without fanart
- **WHEN** the `FollowService.List` RPC returns an artist without fanart data
- **THEN** the view model image URL fields SHALL be undefined or empty, triggering fallback display in UI components

#### Scenario: Dashboard events enriched with fanart
- **WHEN** the dashboard constructs `LiveEvent` objects from concert data
- **THEN** the system SHALL look up fanart URLs by artist ID from the `FollowService.List` response and attach them to the `LiveEvent`

### Requirement: Artist name larger than the location label
The artist name on an event card SHALL be visually prominent and clearly distinguishable from the location label below it: its font size SHALL be larger than the location label's.

#### Scenario: Text fallback versus location label
- **WHEN** an event card displays an artist name with a location label below
- **THEN** the artist name font size SHALL be noticeably larger than the location label font size

### Requirement: Concert Highway Custom Element

The system SHALL provide a reusable `<concert-highway>` custom element that renders a 3-column concert lane grid (home/nearby/away) with stage headers, date separators, event cards, and laser beam effects.

#### Scenario: Render date groups with 3-column layout

- **WHEN** `<concert-highway>` receives a `dateGroups` binding containing `DateGroup[]`
- **THEN** the element SHALL render a 3-column grid with stage headers labeled HOME, NEAR, and AWAY
- **AND** each date group SHALL display a sticky date separator followed by three lane columns containing `<event-card>` components

#### Scenario: Laser beam effects for matched events

- **WHEN** `showBeams` is true (default) and the date groups contain matched events
- **THEN** the element SHALL render laser beam overlays spanning from the top of the viewport to each matched event card
- **AND** beam positions SHALL update on scroll via `requestAnimationFrame`
- **AND** the element's own CSS SHALL NOT establish a CSS containing block that would clip `position: fixed` children

#### Scenario: Readonly mode suppresses card interaction

- **WHEN** `readonly` is set to true
- **THEN** all `<event-card>` components SHALL be rendered with `readonly="true"`
- **AND** tapping a card SHALL NOT dispatch the `event-selected` event

#### Scenario: Interactive mode dispatches event selection

- **WHEN** `readonly` is false and the user taps an event card
- **THEN** the `event-selected` custom event SHALL bubble up from the element
- **AND** the event detail payload SHALL contain the selected `Concert` object

#### Scenario: Empty lane display

- **WHEN** a lane (home, nearby, or away) has no concerts for a given date
- **THEN** the lane SHALL display a placeholder dash ("—")

### Requirement: Matched event card glow opacity
The dashboard matched event card (`[data-matched]`) SHALL render a diffuse laser-beam glow effect around its border using `--_spot-glow` at alpha 50% or lower so that the glow does not visually overwhelm surrounding content.

#### Scenario: Matched card glow is visually subdued
- **WHEN** a concert card has the `data-matched` attribute
- **THEN** the surrounding box-shadow glow SHALL use an alpha value of 50% or lower for the diffuse layers

### Requirement: Event card computes display properties
The `EventCard` component SHALL compute background color from artist name and format dates in Japanese locale.

#### Scenario: Background color from artist name
- **WHEN** an `EventCard` is rendered with an event
- **THEN** `backgroundColor` SHALL return the HSL color from `artistColor(event.artistName)`

#### Scenario: Click dispatches event-selected
- **WHEN** the user clicks the event card
- **THEN** a bubbling `CustomEvent` named `event-selected` SHALL be dispatched with `{ event }` in `detail`

### Requirement: Live highway displays grouped events
The `LiveHighway` component SHALL render date groups and delegate event selection.

#### Scenario: Empty state
- **WHEN** `dateGroups` is an empty array
- **THEN** `isEmpty` SHALL return `true`

#### Scenario: Event selection delegation
- **WHEN** `onEventSelected` is called with a custom event containing a `LiveEvent`
- **THEN** it SHALL open the event detail sheet with that event

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column equal-width timeline layout organized by geographical proximity and date, with festival-style sticky STAGE headers using per-stage identity colors and a vibrant dark-themed aesthetic. The dashboard SHALL handle data loading errors gracefully and distinguish between empty data and error states.

#### Scenario: Dashboard data loading uses promise.bind
- **WHEN** the dashboard loads event data
- **THEN** the template SHALL use `promise.bind` to declaratively handle pending, success, and error states
- **AND** the pending state SHALL display loading skeletons matching the three-lane card layout
- **AND** the error state SHALL display an error message with a "Retry" button

#### Scenario: Dashboard displays empty state
- **WHEN** the dashboard data loads successfully but no events are found
- **THEN** the system SHALL display an empty state message (distinct from the error state)
- **AND** the empty state SHALL NOT be confused with a loading failure

#### Scenario: Dashboard silently displays cached data on refresh failure
- **WHEN** the dashboard has previously loaded data successfully
- **AND** a subsequent data refresh fails
- **THEN** the system SHALL continue displaying the previously loaded data silently
- **AND** the system SHALL NOT display any warning banner or stale data indicator
- **AND** the error SHALL be logged for observability but not surfaced to the user

#### Scenario: Equal-width three-lane grid
- **WHEN** the dashboard renders the event grid
- **THEN** the system SHALL use `grid-template-columns: 1fr 1fr 1fr` for equal lane widths
- **AND** each lane SHALL occupy exactly one-third of the viewport width

#### Scenario: Festival-style color-coded STAGE headers
- **WHEN** the dashboard renders
- **THEN** the system SHALL display a sticky header row at the top of the timetable
- **AND** each stage header span SHALL use its stage identity color as background via `data-stage` attribute selectors (CUBE CSS exception pattern) within the dashboard block's `@scope`:
  - `[data-stage="home"]`: `--color-stage-home` (orange)
  - `[data-stage="near"]`: `--color-stage-near` (cyan)
  - `[data-stage="away"]`: `--color-stage-away` (magenta)
- **AND** text color SHALL be `--color-surface-base` (dark) for contrast against the vibrant backgrounds
- **AND** the labels SHALL use `--font-display` with `font-weight: normal` (400, Righteous single weight), uppercase text
- **AND** the header SHALL use `position: sticky; inset-block-start: 0` with an opaque background

#### Scenario: Lane 1 - HOME STAGE
- **WHEN** displaying the HOME STAGE lane
- **THEN** the system SHALL show events in the user's registered prefecture (proto field: `home`)
- **AND** cards SHALL feature the artist name as the dominant visual element
- **AND** cards SHALL use `container-type: inline-size` for responsive font sizing

#### Scenario: Lane 2 - NEAR STAGE
- **WHEN** displaying the NEAR STAGE lane
- **THEN** the system SHALL show events in nearby prefectures (proto field: `nearby`)
- **AND** cards SHALL display artist name and location label

#### Scenario: Lane 3 - AWAY STAGE
- **WHEN** displaying the AWAY STAGE lane
- **THEN** the system SHALL show events in all other prefectures (proto field: `away`)
- **AND** cards SHALL display artist name and location label

#### Scenario: Dynamic artist name font sizing
- **WHEN** rendering an artist name within a lane card
- **THEN** the system SHALL use CSS container queries to dynamically size the font
- **AND** the font size SHALL use `clamp(12px, 5cqi, 24px)` or equivalent container-relative sizing
- **AND** the minimum font size SHALL be 12px to ensure readability
- **AND** long artist names SHALL wrap with `overflow-wrap: break-word`
- **AND** card height SHALL expand to accommodate line breaks (no fixed height, no text truncation)

#### Scenario: Stage-colored lane accents
- **WHEN** rendering the lane columns in the timetable
- **THEN** each lane SHALL have a subtle `border-block-start` accent using its stage color at 40% opacity
- **AND** lane separators SHALL use `border-inline-end` with the adjacent stage color at 15% opacity

#### Scenario: Date separator gradient treatment
- **WHEN** rendering a date separator between date groups
- **THEN** the separator background SHALL use a linear gradient from `--color-stage-home` through `--color-stage-near` to `--color-stage-away` at 10% opacity
- **AND** the date text SHALL use `--color-brand-accent` color
- **AND** the separator SHALL maintain `position: sticky` with `inset-block-start: 0` behavior and `backdrop-filter: blur(4px)`

### Requirement: The beam effect is presentational and costs nothing to render

The laser beam spotlight SHALL be driven by the scroll position of the concert it
is anchored to, without per-frame scripting and without reading the geometry of
any concert card. Reading card geometry to position the beams forces layout, so
it costs main-thread time proportional to the number of concerts.

The effect is off unless the fan turns it on. While it is off it SHALL add no
work to building or rendering the timetable: no concert card SHALL declare a
beam timeline or carry a beam binding that is observed for changes, and no beam
set SHALL be computed. A card MAY carry a fixed name derived from its concert's
identity, set once when the card is built, so that turning the effect on needs
nothing from the cards. Turning the effect on or off SHALL NOT rebuild the
timetable, and while it is on its cost SHALL be proportional to the number of
beams drawn, not to the number of cards.

The effect SHALL degrade to no beams where the platform cannot drive it, and its
absence SHALL change nothing else: the timetable, the toggle and the persisted
preference SHALL behave identically.

#### Scenario: Beams track scroll position without scripting

- **WHEN** the fan scrolls the timetable with the beam effect enabled
- **THEN** each beam SHALL follow its anchor concert's position
- **AND** no per-frame script SHALL read the position or size of any concert card

#### Scenario: Beams do not defeat viewport-scoped rendering

- **WHEN** the beam effect is enabled on a timetable whose later dates are not
  yet built
- **THEN** the beams SHALL NOT cause any of those dates to be built
- **AND** a matched concert whose date is not built SHALL have no beam

#### Scenario: Only concerts on screen are lit

- **WHEN** the beam effect is enabled on a timetable longer than the viewport
- **THEN** only the concerts currently on screen SHALL have a beam drawn
- **AND** a concert the fan has not scrolled to SHALL NOT be lit, whether its
  date is merely below the fold or not built at all

#### Scenario: Beams are absent where unsupported, with nothing else affected

- **WHEN** the fan's browser cannot drive the effect
- **THEN** no beams SHALL be shown
- **AND** the toggle SHALL still be offered, still persist the preference, and the
  timetable SHALL render and behave exactly as it does with the effect disabled

#### Scenario: Disabled beams cost nothing

- **WHEN** the beam effect is off and the timetable is built
- **THEN** no concert card SHALL declare a beam timeline
- **AND** no card SHALL carry a beam binding that is observed for changes
- **AND** no beam set SHALL be computed

#### Scenario: Turning beams on reaches the concerts already on screen

- **WHEN** the fan turns the beam effect on while the timetable is displayed
- **THEN** the matched concerts already on screen SHALL be lit without leaving
  the page
- **AND** no date group or concert card SHALL be rebuilt

### Requirement: Dashboard cards show whether the hype level matches the concert

The system SHALL visually distinguish dashboard event cards based on whether the artist's hype level matches the concert by its lane, rather than on hype level alone. A card is "matched" when the artist's hype level matches the concert's lane, and "unmatched" otherwise. A matched card SHALL look lit like a festival stage; an unmatched card SHALL show the artist's color without light effects.

The match truth table:
- **watch**: never matched (any lane)
- **home**: matched on HOME STAGE only
- **nearby**: matched on HOME STAGE and NEAR STAGE
- **away**: matched on HOME STAGE, NEAR STAGE, and AWAY STAGE

#### Scenario: Match computation is application-code responsibility

- **WHEN** the system builds the data used to render a dashboard event card
- **THEN** the match result SHALL be computed as a pure function comparing hype level and lane
- **AND** the result SHALL be exposed as a matched/unmatched state on the card's data
- **AND** the card's template SHALL bind a `data-matched` attribute from this state
- **AND** CSS SHALL NOT contain hype-lane comparison logic

#### Scenario: Matched card is lit like a stage

- **WHEN** a matched event card is rendered
- **THEN** the card SHALL fill with a diagonal gradient of the artist's color, from the artist's hue to that hue turned by 40 degrees
- **AND** the card SHALL have a 2px border in a bright tint of the artist's color
- **AND** the card SHALL glow in the artist's color around its edges and inward from its top edge

#### Scenario: Matched card has a light beam from above

- **WHEN** a matched event card is rendered
- **THEN** a narrow beam of light in the artist's color SHALL fall from the center of the card's top edge, brightest at the top and faded out before 70% of the card's height
- **AND** the beam SHALL stay inside the card

#### Scenario: Matched card artist name glows

- **WHEN** a matched event card is rendered
- **THEN** the artist name SHALL glow in the artist's color

#### Scenario: Unmatched card shows the artist's color without light

- **WHEN** an unmatched event card is rendered
- **THEN** the card SHALL fill with the same diagonal gradient of the artist's color as a matched card, at a lighter shade
- **AND** the card SHALL have a 1px border in white at 12% opacity
- **AND** the card SHALL show a fine grain texture at 8% opacity over its background
- **AND** the card SHALL have no glow, no light beam, and no glow on the artist name

#### Scenario: Away artist matched on all stages

- **GIVEN** a user has set an artist's hype to Away (どこでも！)
- **WHEN** that artist's concerts appear on HOME STAGE, NEAR STAGE, and AWAY STAGE
- **THEN** all three cards SHALL render as matched (lit like a stage, with a light beam and a glowing artist name)

#### Scenario: Home artist matched only on home stage

- **GIVEN** a user has set an artist's hype to Home (地元)
- **WHEN** that artist's concerts appear on HOME STAGE and AWAY STAGE
- **THEN** the HOME STAGE card SHALL render as matched
- **AND** the AWAY STAGE card SHALL render as unmatched (no glow, no light beam, grain texture)

#### Scenario: Watch artist always unmatched

- **GIVEN** a user has set an artist's hype to Watch (チェック)
- **WHEN** that artist's concerts appear on any stage
- **THEN** all cards SHALL render as unmatched

#### Scenario: Artist color source

- **WHEN** computing visual effects for a matched or unmatched event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generation logic

#### Scenario: Card treatments hold still

- **WHEN** a matched or unmatched event card is on screen, whether or not the fan prefers reduced motion
- **THEN** no part of the card's matched or unmatched treatment SHALL animate
- **AND** the treatment SHALL look the same with reduced motion as without it

### Requirement: Artist name shown on every card

Every dashboard event card SHALL show the artist's name as text, horizontally centered on the card, in white at full opacity on matched and unmatched cards alike. A card SHALL NOT show the artist's logo image.

#### Scenario: Artist name centered on the card

- **WHEN** an event card is rendered
- **THEN** the artist's name SHALL be shown as text, horizontally centered on the card

#### Scenario: Unmatched card name at full visibility

- **WHEN** an unmatched event card is rendered
- **THEN** the artist's name SHALL render in white with no opacity reduction or dimming filter
