## MODIFIED Requirements

### Requirement: Cold-load reveal timings are reported
On a cold visit to Discovery (the first time Discovery is shown in the page, including when the start-up load already built the field), the fan app SHALL send exactly one usage analytics event once all bubbles show artist names, carrying the time from the moment Discovery was opened to: the first bubble drawn (a ghost placeholder, or an artist when the artists arrive before any ghost is drawn), the first artist name drawn, and every bubble showing an artist name, in milliseconds. A name counts as drawn in the frame in which it is on screen. The moment Discovery was opened is the start of the page load when Discovery is the first page of the visit, and the start of the in-app navigation otherwise; the event SHALL state which of the two applies. It SHALL also state which initial-load path ran (top artists or similar seeds) and the number of seeds. Re-entries that paint a cached field SHALL NOT send this event. A visit whose bubble field is paused (search mode, the All Nearby view, a hidden page) at any time before every bubble shows an artist name SHALL NOT send this event: the field draws no frame while it is paused, so the paused time would be counted as time to reveal. The event SHALL obey the analytics consent setting and the query-string rule of the analytics surface.

#### Scenario: Cold visit with followed artists
- **WHEN** a fan who follows artists opens Discovery with no cached field and analytics on
- **THEN** one event is sent with the similar-seed path, the seed count, whether Discovery was the first page, and the three timings in milliseconds

#### Scenario: Artists arrive before a ghost is drawn
- **WHEN** a cold visit's artists arrive before the first ghost bubble is drawn
- **THEN** one event is sent, with the time to the first bubble drawn taken from the first artist bubble

#### Scenario: A name appears after its bubble
- **WHEN** an artist bubble is fully shown and its name appears on screen in a later frame
- **THEN** the first-name and all-names times are taken from the frames in which the names appeared

#### Scenario: Re-entry
- **WHEN** the fan returns to Discovery within the session and the cached field is painted
- **THEN** no reveal-timing event is sent

#### Scenario: Analytics off
- **WHEN** the fan has turned analytics off in Settings
- **THEN** no reveal-timing event is sent

#### Scenario: Leaving before the reveal completes
- **WHEN** the fan leaves Discovery before every bubble shows an artist name
- **THEN** no reveal-timing event is sent for that visit

#### Scenario: Field paused before the reveal completes
- **WHEN** a fan opens Discovery with no cached field and analytics on, and before every bubble shows an artist name the field is paused (the page is hidden because the fan switched to another app or opened Discovery in a background tab, Discovery opens on or switches to the All Nearby view, or the fan enters search mode), and the fan later returns to the bubbles and every bubble shows an artist name
- **THEN** no reveal-timing event is sent for that visit
