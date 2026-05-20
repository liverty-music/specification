# Capability: Passion Level

## Purpose

Allow users to express different levels of enthusiasm for followed artists, influencing how prominently their events appear on the Dashboard and whether push notifications are sent.

## Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype level tiers for each followed artist. The tier surface labels are Layer B brand expressions (per the `brand-vocabulary` capability) rendered invariantly in English across all locales:

| Tier | Proto Value | Emoji | UI Label (invariant, all locales) | Notification Scope |
|------|-------------|-------|------------------------------------|-------------------|
| Watch | HYPE_TYPE_WATCH | 👀 | Watch | None |
| Home | HYPE_TYPE_HOME | 🔥 | Home | Home area only |
| Nearby | HYPE_TYPE_NEARBY | 🔥🔥 | Nearby | Within 200km |
| Away | HYPE_TYPE_AWAY | 🔥🔥🔥 | Away | All concerts |

All four tiers SHALL be selectable by authenticated users via the SetHype RPC. No tier SHALL be rejected by server-side validation.

#### Scenario: Default hype level on follow

- **WHEN** a user follows a new artist
- **AND** the follow relationship is created (a new row is inserted into the `followed_artists` table)
- **THEN** the hype level SHALL default to Nearby (HYPE_TYPE_NEARBY)
- **AND** the database column `followed_artists.hype` SHALL have its DEFAULT clause set to `'nearby'`, so the default is honored even when the `Follow` RPC carries no `hype` field

#### Scenario: UI labels are invariant English across locales

- **WHEN** hype level labels are displayed in any UI surface (my-artists table column header, page-help tier explanation, settings, accessibility names, slider legend)
- **THEN** the system SHALL display the invariant English forms `Watch / Home / Nearby / Away` regardless of the active locale
- **AND** the system SHALL NOT display the legacy JA-only forms `チェック / 地元 / 近くも / どこでも！` or `観測 / 地元 / 近郊 / 全国`
- **AND** the labels SHALL NOT be sourced from `entity.hype.values.*` i18n keys (which have been removed per the `brand-vocabulary` graduation to Layer B)

#### Scenario: SetHype accepts all four tiers

- **WHEN** an authenticated user calls SetHype with any of the four defined hype tiers (WATCH, HOME, NEARBY, AWAY)
- **THEN** the system SHALL accept the request and persist the hype level

### Requirement: Existing follow records preserve their stored hype

The change to the database column default SHALL be forward-looking only. Existing `followed_artists` rows whose `hype` column holds any value (including the previous `'watch'` default) SHALL retain that value; no `UPDATE` statement SHALL run as part of the migration.

#### Scenario: Pre-migration follows keep their hype

- **WHEN** a `followed_artists` row exists with `hype = 'watch'` before the migration applies
- **AND** the migration runs (`ALTER COLUMN hype SET DEFAULT 'nearby'`)
- **THEN** the row's `hype` value SHALL remain `'watch'` after the migration
- **AND** the user's view of that follow SHALL be unaffected

#### Scenario: Post-migration new follows pick up new default

- **WHEN** the migration has been applied
- **AND** a new follow is created via the `Follow` RPC (no `hype` field in the request)
- **THEN** the newly-inserted row SHALL have `hype = 'nearby'`
- **AND** subsequent `ListFollowed` calls SHALL return that follow with `hype = HYPE_TYPE_NEARBY`

### Requirement: Hype Changes Require Authentication

The system SHALL prevent unauthenticated users from changing hype levels. Hype state SHALL NOT be persisted in localStorage.

#### Scenario: Unauthenticated user attempts hype change

- **WHEN** an unauthenticated user attempts to change a hype level (via slider tap or any UI control)
- **THEN** the system SHALL NOT update the hype level
- **AND** the system SHALL trigger a signup prompt flow
- **AND** no hype value SHALL be written to localStorage

#### Scenario: Authenticated user changes hype

- **WHEN** an authenticated user changes a hype level
- **THEN** the system SHALL call `SetHype` RPC and persist the change on the backend
- **AND** the UI SHALL update optimistically

### Requirement: Hype Level Persistence

The system SHALL persist each user's hype level per followed artist in the backend database, enabling cross-device synchronization.

#### Scenario: Hype level survives session restart

- **GIVEN** a user sets an artist to Away (どこでも！)
- **WHEN** the user closes and reopens the app
- **THEN** the artist SHALL still display as Away (どこでも！)

### Requirement: SetHype API

The system SHALL provide a SetHype RPC endpoint that accepts an artist ID and a hype level, updating the user's preference for that artist. The endpoint SHALL accept all four defined HypeType values (WATCH, HOME, NEARBY, AWAY).

#### Scenario: Successful update

- **GIVEN** an authenticated user who follows an artist
- **WHEN** the user calls SetHype with a valid artist ID and hype level
- **THEN** the system SHALL update the hype level and return success

#### Scenario: Unauthenticated request

- **GIVEN** an unauthenticated request
- **WHEN** the user calls SetHype
- **THEN** the system SHALL return an Unauthenticated error

#### Scenario: Invalid artist ID

- **GIVEN** an authenticated user
- **WHEN** the user calls SetHype without an artist ID
- **THEN** the system SHALL return an InvalidArgument error

### Requirement: HypeLevel in ListFollowed Response

The system SHALL include the user's hype level for each artist in the ListFollowed response, using a FollowedArtist wrapper that contains both the artist entity and the hype level.

#### Scenario: ListFollowed returns hype levels

- **GIVEN** a user follows three artists with different hype levels
- **WHEN** the user calls ListFollowed
- **THEN** each artist in the response SHALL include its corresponding hype level

### Requirement: Hype Visual Indicators on Dashboard Cards

The system SHALL visually distinguish dashboard event cards based on whether the artist's hype level covers the concert's lane proximity (hype-lane match), rather than on hype level alone. A card is "matched" when the artist's hype radius includes the concert's lane, and "unmatched" otherwise. Matched cards SHALL evoke a live festival stage; unmatched cards SHALL evoke a faded concert poster.

The match truth table:
- **watch**: never matched (any lane)
- **home**: matched on HOME STAGE only
- **nearby**: matched on HOME STAGE and NEAR STAGE
- **away**: matched on HOME STAGE, NEAR STAGE, and AWAY STAGE

#### Scenario: Match computation is TypeScript responsibility

- **WHEN** the system builds a `LiveEvent` from concert data
- **THEN** the match result SHALL be computed in TypeScript as a pure function comparing hype level and lane
- **AND** the result SHALL be exposed as a boolean `matched` property on the `LiveEvent` interface
- **AND** the HTML template SHALL bind `data-matched` attribute from this property
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
- **THEN** the artist color SHALL be derived from the existing deterministic color generator (`color-generator.ts`)

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

### Requirement: WATCH card styling (REMOVED)

Replaced by hype-lane match model. Watch-level styling is now handled by the unmatched treatment (`data-matched` absent).

### Requirement: HOME card styling (REMOVED)

Replaced by hype-lane match model. Per-tier visual escalation is removed. Home artists use matched/unmatched styling based on lane.

### Requirement: NEARBY hype card styling (REMOVED)

Replaced by hype-lane match model. Per-tier visual escalation is removed. Nearby artists use matched/unmatched styling based on lane.

### Requirement: AWAY card styling (REMOVED)

Replaced by hype-lane match model. Per-tier visual escalation is removed. Away artists use matched/unmatched styling based on lane.

### Requirement: Emoji badge hype indicators on event cards (REMOVED)

**Reason**: Emoji badges overlap artist names in narrow lanes and consume card space. Replaced by zero-space border/glow/neon system.
**Migration**: Remove emoji badge elements from event card templates. Remove `HYPE_META` icon references from event card rendering. Hype visualization is now handled entirely via CSS classes based on hype level.
