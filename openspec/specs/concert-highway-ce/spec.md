# Concert Highway Custom Element

## Purpose

Reusable custom element that renders the 3-column concert lane grid (home/nearby/away) with stage headers, date separators, event cards, and laser beam effects. Used by both the authenticated dashboard and the Welcome page preview.
## Requirements
### Requirement: Concert Highway Custom Element

The system SHALL provide a reusable `<concert-highway>` custom element that renders a 3-column concert lane grid (home/nearby/away) with stage headers, date separators, event cards, and laser beam effects.

#### Scenario: Render date groups with 3-column layout

- **WHEN** `<concert-highway>` receives a `dateGroups` binding containing `DateGroup[]`
- **THEN** the CE SHALL render a 3-column grid with stage headers labeled HOME, NEAR, and AWAY
- **AND** each date group SHALL display a sticky date separator followed by three lane columns containing `<event-card>` components

#### Scenario: Laser beam effects for matched events

- **WHEN** `showBeams` is true (default) and the date groups contain matched events
- **THEN** the CE SHALL render laser beam overlays spanning from the top of the viewport to each matched event card
- **AND** beam positions SHALL update on scroll via `requestAnimationFrame`
- **AND** the CE's own CSS SHALL NOT establish a CSS containing block that would clip `position: fixed` children

#### Scenario: Readonly mode suppresses card interaction

- **WHEN** `readonly` is set to true
- **THEN** all `<event-card>` components SHALL be rendered with `readonly="true"`
- **AND** tapping a card SHALL NOT dispatch the `event-selected` event

#### Scenario: Interactive mode dispatches event selection

- **WHEN** `readonly` is false and the user taps an event card
- **THEN** the `event-selected` custom event SHALL bubble up from the CE
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

