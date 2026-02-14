## ADDED Requirements

### Requirement: Image-Free Typography-Focused Design
The system SHALL implement a typography-focused dashboard design that avoids artist images to eliminate copyright concerns and operational costs.

#### Scenario: Dynamic color generation from artist names
- **WHEN** displaying live event cards
- **THEN** the system SHALL generate a unique theme color for each artist based on their name string
- **AND** the color SHALL be derived using a deterministic algorithm (e.g., HSL color space conversion)
- **AND** the color SHALL be used as the card background or accent color
- **AND** this SHALL provide visual variety without requiring image assets

---

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column timeline layout organized by geographical proximity and date.

#### Scenario: Dashboard layout structure
- **WHEN** the dashboard is displayed
- **THEN** the system SHALL implement a vertical-scrolling three-lane layout
- **AND** the Y-axis SHALL represent time (date/month) displayed on the left edge or lane dividers
- **AND** the X-axis SHALL represent distance from the user's registered region

#### Scenario: Lane 1 - My City (Main Lane)
- **WHEN** displaying Lane 1 (45-50% screen width)
- **THEN** the system SHALL show events in the user's registered prefecture
- **AND** the system SHALL use mega-typography style cards
- **AND** cards SHALL feature the artist name in extra-bold, large font as the primary element
- **AND** cards SHALL NOT display images, dates, or venue names on the surface

#### Scenario: Lane 2 - My Region (Adjacent Lane)
- **WHEN** displaying Lane 2 (30% screen width)
- **THEN** the system SHALL show events in the same geographical region as the user's prefecture
- **AND** cards SHALL be medium-sized with compressed information
- **AND** cards SHALL display artist name + prefecture name (e.g., "福岡")
- **AND** background SHALL be solid color or subtle gradient

#### Scenario: Lane 3 - Others (Opposite Lane)
- **WHEN** displaying Lane 3 (20% screen width)
- **THEN** the system SHALL show all other nationwide events
- **AND** cards SHALL be text-only list format
- **AND** cards SHALL display artist name + major city name (e.g., "Osaka")

---

### Requirement: Bottom Sheet Detail Modal
The system SHALL display detailed event information in a bottom sheet modal when users tap any event card.

#### Scenario: Opening event details
- **WHEN** a user taps any event card in any lane
- **THEN** the system SHALL quickly slide up a detail bottom sheet from the bottom of the screen
- **AND** the modal SHALL maintain smooth animation (60fps target)

#### Scenario: Detail modal content
- **WHEN** the bottom sheet detail modal is displayed
- **THEN** the modal SHALL show the artist name prominently
- **AND** the modal SHALL display the event date and start time
- **AND** the modal SHALL display the venue name with a link to Google Maps
- **AND** the modal SHALL provide a "[🔗 View Official Info]" button linking to the source
- **AND** the modal SHALL provide a "[📅 Add to Calendar]" button for native calendar export

---

### Requirement: Typography-First Card Design
The system SHALL prioritize typography and dynamic colors over images in all event cards.

#### Scenario: Card visual design
- **WHEN** rendering event cards
- **THEN** the system SHALL use artist names as the primary visual element
- **AND** the system SHALL apply dynamic colors derived from artist names
- **AND** the system SHALL use bold, readable typography optimized for mobile screens
- **AND** the system SHALL ensure sufficient contrast between text and background colors

---

### Requirement: Mobile-First Responsive Layout
The system SHALL optimize the Live Highway UI for mobile portrait orientation with one-handed scrolling.

#### Scenario: Mobile layout constraints
- **WHEN** the dashboard is rendered on a mobile device
- **THEN** the system SHALL use CSS Grid or Flexbox for the three-lane layout
- **AND** the system SHALL prevent horizontal scrolling
- **AND** the system SHALL enable smooth vertical scrolling
- **AND** the system SHALL optimize for one-handed thumb navigation

---

### Requirement: Date/Time Display Along Y-Axis
The system SHALL display date markers along the timeline to provide temporal context.

#### Scenario: Timeline date markers
- **WHEN** scrolling through the dashboard
- **THEN** the system SHALL display month and day markers on the left edge or lane dividers
- **AND** date markers SHALL be fixed or scroll-following for easy reference
- **AND** events SHALL be chronologically organized from top (near future) to bottom (distant future)

---

## Technical Context

This specification defines the Live Dashboard UI for Liverty Music MVP, featuring:
- **Design Philosophy**: Typography-first, image-free to avoid copyright issues
- **Layout**: "Live Highway" - 3-lane vertical timeline organized by distance
- **Dynamic Styling**: Color generation from artist name strings (deterministic algorithm)
- **UI Pattern**: Mega-typography for primary lane, compressed info for secondary lanes
- **Interaction**: Bottom sheet modals for event details
- **Target Platform**: Mobile PWA with portrait orientation focus

## Reference Documentation

For detailed visual design, layout ratios, and interaction patterns, see:
- `../docs/onboarding-ux.md` (Japanese detailed specification - Step 4)
