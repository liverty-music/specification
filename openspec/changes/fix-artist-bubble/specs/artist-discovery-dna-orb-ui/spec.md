## ADDED Requirements

### Requirement: Accurate bubble tap detection in overlapping regions
The system SHALL select the bubble whose center is closest to the tap point when multiple bubbles overlap at the tap coordinates. The system SHALL process exactly one bubble per tap event.

#### Scenario: Overlapping bubbles return closest-center bubble
- **WHEN** two or more bubbles overlap at the tap coordinates
- **THEN** the system SHALL return the bubble whose center is nearest to the tap point (minimum Euclidean distance)
- **AND** the system SHALL NOT return a bubble based on iteration order of the internal data structure

#### Scenario: Single tap produces single follow
- **WHEN** the user taps a bubble on a touch device
- **THEN** the system SHALL process exactly one `handleInteraction` call
- **AND** the system SHALL NOT fire a duplicate interaction from a synthesized click event following the touch event

#### Scenario: Fading-out bubbles are excluded from hit detection
- **WHEN** a bubble is in the fading-out state
- **THEN** the system SHALL exclude it from hit detection regardless of its position

#### Scenario: Spawning bubbles with scale=0 are excluded
- **WHEN** a bubble has `scale=0` (spawn animation not started)
- **THEN** the hit radius SHALL be `radius * scale = 0`
- **AND** the system SHALL NOT select this bubble

### Requirement: CJK text wrapping in bubble labels
The system SHALL wrap artist names containing CJK characters (Han, Hiragana, Katakana, Hangul) at character boundaries when the text contains no whitespace, ensuring readability inside the bubble.

#### Scenario: Japanese artist name without spaces wraps into multiple lines
- **WHEN** an artist name consists entirely of CJK characters (e.g., "ポルカドットスティングレイ")
- **AND** the full name exceeds the bubble's usable text width
- **THEN** the system SHALL break the text at character boundaries to produce multiple lines
- **AND** each line SHALL fit within `usableWidth` as measured by `Canvas.measureText`
- **AND** no characters SHALL be lost (concatenated lines equal the original name)

#### Scenario: Mixed CJK and Latin text wraps at appropriate boundaries
- **WHEN** an artist name contains both CJK characters and Latin words separated by spaces (e.g., "凛として時雨 TK")
- **THEN** the system SHALL first split at whitespace boundaries
- **AND** if any resulting segment still exceeds `usableWidth`, the system SHALL further break CJK segments at character boundaries

#### Scenario: Short CJK name fits in a single line
- **WHEN** a CJK artist name fits within `usableWidth` at the initial font size
- **THEN** the system SHALL render it as a single line without wrapping

### Requirement: Minimum readable font size for bubble labels
The system SHALL enforce a minimum font size of 10px for bubble text labels to ensure readability on mobile devices.

#### Scenario: Font does not shrink below 10px
- **WHEN** the adaptive font sizing loop runs for a given artist name and bubble radius
- **THEN** the font size SHALL NOT be reduced below 10px
- **AND** if the text still does not fit at 10px, the system SHALL render it using the CJK wrapping rules and accept truncation via `fillText` maxWidth as a last resort

## MODIFIED Requirements

### Requirement: Physics-Based Bubble Animation
The system SHALL implement smooth, natural bubble movement using physics simulation.

#### Scenario: Realistic bubble physics
- **WHEN** artist bubbles are displayed
- **THEN** the system SHALL use a physics engine (e.g., Matter.js, D3.js force simulation)
- **AND** bubbles SHALL float, bounce, and interact naturally
- **AND** performance SHALL be optimized for mobile devices using component optimization or Canvas/WebGL rendering

#### Scenario: Touch interaction uses unified pointer events
- **WHEN** the user interacts with the canvas via touch, mouse, or pen
- **THEN** the system SHALL handle interactions via a single event type (Pointer Events API)
- **AND** the system SHALL NOT register separate `click` and `touchstart` listeners
- **AND** the canvas element SHALL set `touch-action: manipulation` to prevent 300ms tap delay
