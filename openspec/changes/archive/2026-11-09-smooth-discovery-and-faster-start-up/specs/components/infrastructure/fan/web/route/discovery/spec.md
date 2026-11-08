## MODIFIED Requirements

### Requirement: Physics-Based Bubble Animation
The system SHALL implement smooth, natural bubble movement using physics simulation. With a full field of 50 bubbles on the frame reference setup, the bubble field SHALL keep a median frame interval of at most 17 ms and a 95th-percentile frame interval of at most 34 ms while the fan does not touch it, and in the 2.5 s after a tap on a bubble no frame SHALL take longer than 200 ms and at most 5 frames SHALL take longer than 50 ms, each as the median of about 5 runs. The frame reference setup is desktop Chrome with GPU rendering, device emulation at a 412 px viewport, and 4x CPU throttling, on a guest's field of 50 artists. The bounds hold with motion enabled; decorative animations elsewhere on the screen count toward them.

#### Scenario: Realistic bubble physics
- **WHEN** artist bubbles are displayed
- **THEN** the system SHALL use a physics engine (e.g., Matter.js, D3.js force simulation)
- **AND** bubbles SHALL float, bounce, and interact naturally
- **AND** performance SHALL be optimized for mobile devices using component optimization or Canvas/WebGL rendering

#### Scenario: Idle field of 50 bubbles
- **WHEN** a guest's field of 50 bubbles is shown about 5 times on the frame reference setup and the fan does not touch it
- **THEN** the median over those runs of the median frame interval is at most 17 ms
- **AND** the median over those runs of the 95th-percentile frame interval is at most 34 ms

#### Scenario: Tap on a bubble in a field of 50
- **WHEN** the fan taps an artist bubble in a field of 50, about 5 times on the frame reference setup, and each time similar artists arrive and enter the field
- **THEN** the median over those runs of the longest frame in the 2.5 s after the tap is at most 200 ms
- **AND** the median over those runs of the number of frames longer than 50 ms in that window is at most 5

#### Scenario: Bubbles at rest stay where they are
- **WHEN** the bubbles have come to rest and the fan does not touch the field
- **THEN** no bubble moves until the field changes or the canvas is resized

#### Scenario: Field change wakes the bubbles at rest
- **WHEN** a bubble is removed from or added to a field whose bubbles are at rest
- **THEN** the remaining bubbles move again under gravity, and none stays floating where the removed bubble held it up

### Requirement: Revealed bubble names fade in on real time
When a bubble appears (a ghost switching to a real artist, or a new artist added to the field), its artist name SHALL become readable within 300 ms of real time, at any frame rate down to 10 frames per second. The fade-in SHALL follow elapsed real time and SHALL NOT slow down when frames take longer. The 300 ms count until the name is on screen: work that prepares the name for drawing outside the frame SHALL NOT make the name appear later.

#### Scenario: Normal frame rate
- **WHEN** a ghost bubble switches to a real artist and frames arrive every 16 ms
- **THEN** the artist name is drawn within 300 ms of the switch

#### Scenario: Slow frames
- **WHEN** a ghost bubble switches to a real artist and frames arrive every 100 ms
- **THEN** the artist name is drawn within 300 ms of the switch, not after the longer time a 32 ms per-frame cap would imply

#### Scenario: Reduced motion
- **WHEN** the user prefers reduced motion
- **THEN** the artist name is readable no later than with motion enabled

#### Scenario: Name preparation has not finished
- **WHEN** a ghost bubble switches to a real artist on a cold load, before the work that prepares that name for faster drawing has finished
- **THEN** the artist name is still drawn within 300 ms of the switch
- **AND** the name looks the same before and after that work finishes

### Requirement: Cold-load reveal timings are reported
On a cold visit to Discovery (the first time Discovery is shown in the page, including when the start-up load already built the field), the fan app SHALL send exactly one usage analytics event once all bubbles show artist names, carrying the time from the moment Discovery was opened to: the first bubble drawn (a ghost placeholder, or an artist when the artists arrive before any ghost is drawn), the first artist name drawn, and every bubble showing an artist name, in milliseconds. A name counts as drawn in the frame in which it is on screen. The moment Discovery was opened is the start of the page load when Discovery is the first page of the visit, and the start of the in-app navigation otherwise; the event SHALL state which of the two applies. It SHALL also state which initial-load path ran (top artists or similar seeds) and the number of seeds. Re-entries that paint a cached field SHALL NOT send this event. The event SHALL obey the analytics consent setting and the query-string rule of the analytics surface.

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

## ADDED Requirements

### Requirement: Discovery frame timings are reported
On each visit to Discovery, the fan app SHALL send one usage analytics event about the frames of the artist bubbles when the visit ends: the fan leaves Discovery, switches to the All Nearby view, or hides the page. The event SHALL carry, over the frames in which the bubble field was shown and running: the number of frames measured, the median and 95th-percentile frame interval in milliseconds, the longest frame in milliseconds, the number of frames longer than 50 ms, and the number of bubbles shown when the visit ended. It SHALL also state whether bubble names were prepared off the main thread on this device. Time while the field is paused (search mode, the All Nearby view, a hidden page) SHALL NOT count. A visit with fewer than 30 measured frames SHALL NOT send the event. The event SHALL obey the analytics consent setting and the query-string rule of the analytics surface.

#### Scenario: Fan leaves Discovery after browsing bubbles
- **WHEN** the fan, with analytics on, watches and taps the bubbles for 10 s and then opens another tab of the app
- **THEN** one frame-timing event is sent with the frame count, the median and 95th-percentile intervals, the longest frame, the count of frames over 50 ms, the bubble count, and whether names were prepared off the main thread

#### Scenario: Paused time is left out
- **WHEN** the fan opens search mode for 20 s during a visit and then leaves Discovery
- **THEN** the event counts only the frames drawn while search mode was off

#### Scenario: Visit too short to measure
- **WHEN** the fan leaves Discovery before 30 frames of the bubble field were measured
- **THEN** no frame-timing event is sent for that visit

#### Scenario: One event per visit
- **WHEN** the fan hides the page, comes back, and later leaves Discovery
- **THEN** exactly one frame-timing event is sent for that visit, when the page was hidden

#### Scenario: Analytics off
- **WHEN** the fan has turned analytics off in Settings
- **THEN** no frame-timing event is sent
