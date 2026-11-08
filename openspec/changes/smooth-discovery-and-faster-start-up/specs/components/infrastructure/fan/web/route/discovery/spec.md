## MODIFIED Requirements

### Requirement: Physics-Based Bubble Animation
The system SHALL implement smooth, natural bubble movement using physics simulation. With a full field of 50 bubbles on the frame reference setup, the bubble field SHALL keep a median frame interval of at most 17 ms and a 95th-percentile frame interval of at most 34 ms while the fan does not touch it, and in the 2.5 s after a tap on a bubble no frame SHALL take longer than 200 ms and at most 5 frames SHALL take longer than 50 ms, each as the median of about 5 runs. The frame reference setup is desktop Chrome with GPU rendering, device emulation at a 412 px viewport, and 4x CPU throttling, on a guest's field of 50 artists. The bounds hold with motion enabled; decorative animations elsewhere on the screen count toward them.

#### Scenario: Realistic bubble physics
- **WHEN** artist bubbles are displayed
- **THEN** the system SHALL use a physics engine (e.g., Matter.js, D3.js force simulation)
- **AND** bubbles SHALL float, bounce, and interact naturally
- **AND** performance SHALL be optimized for mobile devices using component optimization or Canvas/WebGL rendering

#### Scenario: Idle field of 50 bubbles
- **WHEN** a guest's field of 50 bubbles is shown on the frame reference setup and the fan does not touch it
- **THEN** the median frame interval is at most 17 ms
- **AND** the 95th-percentile frame interval is at most 34 ms

#### Scenario: Tap on a bubble in a field of 50
- **WHEN** the fan taps an artist bubble in a field of 50 on the frame reference setup, and similar artists arrive and enter the field
- **THEN** in the 2.5 s after the tap no frame takes longer than 200 ms
- **AND** at most 5 frames take longer than 50 ms

#### Scenario: Bubbles at rest stay where they are
- **WHEN** the bubbles have come to rest and the fan does not touch the field
- **THEN** no bubble moves until the field changes or the canvas is resized

#### Scenario: Field change wakes the bubbles at rest
- **WHEN** a bubble is removed from or added to a field whose bubbles are at rest
- **THEN** the remaining bubbles move again under gravity, and none stays floating where the removed bubble held it up

### Requirement: Revealed bubble names fade in on real time
When a bubble appears (a ghost switching to a real artist, or a new artist added to the field), its artist name SHALL become readable within 300 ms of real time, at any frame rate down to 10 frames per second. The fade-in SHALL follow elapsed real time and SHALL NOT slow down when frames take longer. The 300 ms count until the name is on screen: work that prepares the name for drawing outside the frame SHALL NOT make the name appear later. The time the cold-load reveal timings report for a name is the frame in which that name is on screen.

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

#### Scenario: Reported name time follows the screen
- **WHEN** the cold-load reveal timings are sent
- **THEN** the first-name and all-names times are those of the frames in which the names were on screen, not of the moment the bubbles became opaque enough to show them

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
