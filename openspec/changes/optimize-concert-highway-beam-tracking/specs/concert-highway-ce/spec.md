## ADDED Requirements

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
