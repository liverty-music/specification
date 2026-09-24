# Live Highway

## Purpose

Renders the shared three-lane concert card grid showing each artist's followed events with artist logo or name, hype-driven visual prominence, and a subtle glow effect on matched cards.

## Requirements

### Requirement: Event Card Logo Display
The dashboard event card SHALL display the artist's transparent logo image instead of the text artist name when a logo URL is available. The system SHALL use `hd_music_logo` as the primary source and fall back to `music_logo` when `hd_music_logo` is unavailable. When neither logo is available, the card SHALL display the existing text artist name.

#### Scenario: Artist has hd_music_logo
- **WHEN** an event card renders for an artist with `hd_music_logo` in their fanart data
- **THEN** the card SHALL display the `hd_music_logo` image with `object-fit: contain` instead of the text name

#### Scenario: Artist has only music_logo
- **WHEN** an event card renders for an artist with `music_logo` but no `hd_music_logo`
- **THEN** the card SHALL display the `music_logo` image as fallback

#### Scenario: Artist has no logo
- **WHEN** an event card renders for an artist without any logo in their fanart data
- **THEN** the card SHALL display the existing text artist name with the current styling

#### Scenario: Logo image fails to load
- **WHEN** the logo image URL returns an error or times out
- **THEN** the card SHALL fall back to displaying the text artist name

### Requirement: Fanart Data Propagation
The frontend service layer SHALL extract fanart image URLs from the `Artist.fanart` proto field in `ListFollowed` responses and propagate them to the `LiveEvent` and `FollowedArtist` view models for consumption by UI components.

#### Scenario: ListFollowed returns artist with fanart
- **WHEN** the `ListFollowed` RPC returns an artist with populated fanart data
- **THEN** the service layer SHALL map `hd_music_logo`, `music_logo`, `artist_background`, and `artist_thumb` URLs to the corresponding view model fields

#### Scenario: ListFollowed returns artist without fanart
- **WHEN** the `ListFollowed` RPC returns an artist without fanart data
- **THEN** the view model image URL fields SHALL be undefined or empty, triggering fallback display in UI components

#### Scenario: Dashboard events enriched with fanart
- **WHEN** the dashboard constructs `LiveEvent` objects from concert data
- **THEN** the system SHALL look up fanart URLs by artist ID from the `ListFollowed` response and attach them to the `LiveEvent`

### Requirement: Logo and text visibility on unmatched cards
Event cards that are not matched SHALL display artist logos and text at full visibility. No dimming filters (brightness, grayscale) SHALL be applied to logos, and no opacity reduction SHALL be applied to text fallback names on unmatched cards.

#### Scenario: Unmatched card with logo
- **WHEN** an unmatched event card displays an artist ClearLOGO image
- **THEN** the logo SHALL render without brightness or grayscale filters

#### Scenario: Unmatched card with text fallback
- **WHEN** an unmatched event card displays an artist name as text (no logo available)
- **THEN** the text SHALL render at full opacity (no opacity reduction)

### Requirement: Center-aligned card content
Artist logos and text fallback names SHALL be horizontally centered within event cards.

#### Scenario: Logo centered in card
- **WHEN** an event card displays a ClearLOGO image
- **THEN** the logo SHALL be horizontally centered within the card

#### Scenario: Text fallback centered in card
- **WHEN** an event card displays an artist name as text
- **THEN** the text SHALL be horizontally centered within the card

### Requirement: Text fallback font size prominence
Artist names displayed as text fallback SHALL be visually prominent and clearly distinguishable from the location label below. The text fallback font size SHALL be larger than the current sizing to provide visual weight comparable to ClearLOGO images.

#### Scenario: Text fallback versus location label
- **WHEN** an event card displays an artist name as text with a location label below
- **THEN** the artist name font size SHALL be noticeably larger than the location label font size

### Requirement: Logo scales to fill card space
Artist ClearLOGO images SHALL scale proportionally to the lane container width using cqi units. The logo SHALL NOT be constrained to a fixed small height.

#### Scenario: Logo fills card height
- **WHEN** an event card displays a ClearLOGO image
- **THEN** the logo SHALL expand proportionally to the lane width, maintaining aspect ratio via `object-fit: contain`

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

### Requirement: Beam tracking updates efficiently per frame

The laser-beam scroll tracking SHALL update without per-frame DOM element queries and without interleaving layout reads with style writes, so that the effect adds minimal INP cost on the dashboard and Welcome-preview hot paths. This constrains only HOW the beams update; the observable beam appearance and cadence defined by the "Laser beam effects for matched events" scenario are unchanged.

#### Scenario: Cached anchor-to-element resolution

- **WHEN** the beam overlay updates in response to a scroll frame
- **THEN** each beam's anchor card SHALL be resolved from a precomputed anchor→element map
- **AND** the component SHALL NOT perform a per-beam element query (e.g. `querySelector`) inside the per-frame update
- **AND** the map SHALL be (re)built when the `dateGroups` binding or the beam index map changes, i.e. on the same triggers that rebuild the beam set

#### Scenario: Batched read-before-write per frame

- **WHEN** the beam overlay updates in response to a scroll frame
- **THEN** the component SHALL complete all card geometry reads (`getBoundingClientRect`) before applying any beam style writes (`--beam-h` / `--beam-top-pct`)
- **AND** the resulting beam geometry SHALL be identical to computing each beam's values independently (the reorder is transparent)

#### Scenario: Missing anchor element degrades gracefully

- **WHEN** a beam's anchor card is absent from the cached map (e.g. not yet mounted)
- **THEN** that beam SHALL be skipped for the current frame without error
- **AND** the beam SHALL resume tracking once a rebuild repopulates its cache entry

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

### Requirement: Frontend Background Color Derivation
The frontend SHALL use `LogoColorProfile` data to determine the card background `--artist-hue` custom property. When `dominantHue` is present (chromatic logos), the hue SHALL be set to that value (logo's own hue family). When `dominantHue` is absent (achromatic logos), the hue SHALL fall back to the existing name-hash algorithm. When no `LogoColorProfile` is available, the existing name-hash algorithm SHALL be used unchanged.

#### Scenario: Chromatic logo card background
- **WHEN** an event card renders for an artist with `dominantHue` present and set to `0` (red)
- **THEN** `--artist-hue` SHALL be set to `0` (same hue family as the logo, with low-chroma background per CSS)

#### Scenario: Achromatic light logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.85`
- **THEN** `--artist-hue` SHALL be set to the name-hash value and background lightness SHALL remain dark (logo is light, background is dark for contrast)

#### Scenario: Achromatic dark logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.15`
- **THEN** `--artist-hue` SHALL be set to the name-hash value and background lightness SHALL be raised to ensure the dark logo is visible

#### Scenario: No logo analysis available
- **WHEN** an event card renders for an artist without `LogoColorProfile`
- **THEN** `--artist-hue` SHALL be computed from the artist name hash (existing behavior)

### Requirement: Hype Visual Indicators on Dashboard Cards

The system SHALL visually distinguish dashboard event cards based on whether the artist's hype level covers the concert's lane proximity (hype-lane match), rather than on hype level alone. A card is "matched" when the artist's hype radius includes the concert's lane, and "unmatched" otherwise. Matched cards SHALL evoke a live festival stage; unmatched cards SHALL evoke a faded concert poster.

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

#### Scenario: Matched card background

- **WHEN** an event card is rendered with `matched = true`
- **THEN** the card background SHALL use a radial-gradient spotlight effect using the artist-color at elevated saturation (oklch chroma 0.20), brighter at an off-center focal point and darker at the edges
- **AND** the card SHALL have a `2px solid` border using the artist's color at 40% opacity
- **AND** the card SHALL have a dual-layer glow: outer `box-shadow: 0 0 16px` at 50% opacity and inner `inset 0 0 12px` at 15% opacity
- **AND** the card background SHALL be clean (no overlay texture)

#### Scenario: Matched card clearLOGO neon glow

- **WHEN** a matched event card has a clearLOGO image (transparent PNG)
- **THEN** the logo SHALL be rendered as an `<img>` element
- **AND** the logo SHALL have a multi-layer `filter: drop-shadow()` neon glow using the artist-color, producing a contour-following glow around the exact logo shape

#### Scenario: Matched card text fallback neon glow

- **WHEN** a matched event card does not have a clearLOGO image
- **THEN** the artist name SHALL be rendered as a text `<span>` element
- **AND** the artist name SHALL have a multi-layer `text-shadow` neon glow using the artist-color

#### Scenario: Matched card spotlight beam cone

- **WHEN** a matched event card is rendered
- **THEN** a vertical light beam cone SHALL illuminate the card from above via a `::before` pseudo-element
- **AND** the beam SHALL use a `linear-gradient` (bright at top, transparent at bottom) shaped by a `mask-image: radial-gradient(ellipse)` to form a narrow cone
- **AND** a bright contact flash (`::after`) SHALL pulse at the card's top edge where the beam hits, using `box-shadow` layers
- **AND** the pseudo-elements SHALL be clipped by `overflow: hidden` on the card

#### Scenario: Matched card color drift animation

- **WHEN** a matched event card is rendered
- **THEN** the artist-color hue SHALL oscillate ±30 degrees over an 8-second ease-in-out infinite cycle via `@property --hue-drift`
- **AND** the hue drift SHALL affect all artist-color references simultaneously (background, border, glow, logo drop-shadow / text-shadow)

#### Scenario: Unmatched card styling

- **WHEN** an event card is rendered with `matched = false`
- **THEN** the card SHALL use a desaturated artist-color (oklch chroma 0.03) as a flat background-color
- **AND** the card SHALL have a `1px solid` border at `white/5%` opacity
- **AND** the card SHALL NOT have a glow effect
- **AND** the card SHALL display an SVG noise texture overlay at 8% opacity via a `::after` pseudo-element
- **AND** the card SHALL NOT have any animations

#### Scenario: Unmatched card clearLOGO dimming

- **WHEN** an unmatched event card has a clearLOGO image
- **THEN** the logo SHALL be rendered with `filter: brightness(0.35) grayscale(0.8)`, appearing dim and desaturated

#### Scenario: Unmatched card text fallback dimming

- **WHEN** an unmatched event card does not have a clearLOGO image
- **THEN** the artist name text SHALL have no text-shadow and reduced opacity

#### Scenario: Away artist matched on all stages

- **GIVEN** a user has set an artist's hype to Away (どこでも！)
- **WHEN** that artist's concerts appear on HOME STAGE, NEAR STAGE, and AWAY STAGE
- **THEN** all three cards SHALL render as matched (spotlight, neon glow, color drift)

#### Scenario: Home artist matched only on home stage

- **GIVEN** a user has set an artist's hype to Home (地元)
- **WHEN** that artist's concerts appear on HOME STAGE and AWAY STAGE
- **THEN** the HOME STAGE card SHALL render as matched
- **AND** the AWAY STAGE card SHALL render as unmatched (desaturated, no glow, noise texture)

#### Scenario: Watch artist always unmatched

- **GIVEN** a user has set an artist's hype to Watch (チェック)
- **WHEN** that artist's concerts appear on any stage
- **THEN** all cards SHALL render as unmatched

#### Scenario: Artist color source

- **WHEN** computing visual effects for a matched or unmatched event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generation logic

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight beam cone animation SHALL be disabled
- **AND** the color drift animation SHALL be disabled
- **AND** static matched effects SHALL remain fully visible (radial-gradient background at center position, border, dual glow, neon logo/text glow)
- **AND** unmatched styling SHALL be unaffected (already static)

#### Scenario: Color drift graceful degradation

- **WHEN** the browser does not support `@property` syntax
- **THEN** the `--hue-drift` value SHALL remain at its initial value of 0
- **AND** all other matched effects (spotlight, glow, border, saturation) SHALL render normally with the static artist-color

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
any concert card. Reading card geometry to position the beams forces layout of
content the browser would otherwise skip, so it both costs main-thread time
proportional to the number of concerts and defeats viewport-scoped rendering of
the timetable.

The effect SHALL degrade to no beams where the platform cannot drive it, and its
absence SHALL change nothing else: the timetable, the toggle and the persisted
preference SHALL behave identically.

#### Scenario: Beams track scroll position without scripting

- **WHEN** the fan scrolls the timetable with the beam effect enabled
- **THEN** each beam SHALL follow its anchor concert's position
- **AND** no per-frame script SHALL read the position or size of any concert card

#### Scenario: Beams do not defeat viewport-scoped rendering

- **WHEN** the beam effect is enabled on a timetable whose off-screen date groups
  are being skipped
- **THEN** those groups SHALL remain skipped
- **AND** the beams SHALL NOT cause them to be laid out

#### Scenario: Only concerts on screen are lit

- **WHEN** the beam effect is enabled on a timetable longer than the viewport
- **THEN** only the concerts currently on screen SHALL have a beam drawn
- **AND** a concert the fan has not scrolled to SHALL NOT be lit, whether its date
  group is merely below the fold or is being skipped entirely

#### Scenario: Beams are absent where unsupported, with nothing else affected

- **WHEN** the fan's browser cannot drive the effect
- **THEN** no beams SHALL be shown
- **AND** the toggle SHALL still be offered, still persist the preference, and the
  timetable SHALL render and behave exactly as it does with the effect disabled
