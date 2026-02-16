# Typography-Focused Dashboard

## Purpose

Defines the Live Dashboard UI for Liverty Music, featuring a typography-first, image-free design with a three-lane "Live Highway" layout organized by geographical proximity and date, with a dark-themed aesthetic.

## Requirements

### Requirement: Image-Free Typography-Focused Design
The system SHALL implement a typography-focused dashboard design with enhanced visual polish, avoiding artist images to eliminate copyright concerns and operational costs.

#### Scenario: Dynamic color generation from artist names
- **WHEN** displaying live event cards
- **THEN** the system SHALL generate a unique theme color for each artist based on their name string
- **AND** the color SHALL be derived using a deterministic algorithm mapped to the HSL color space
- **AND** the lightness SHALL be adjusted for adequate contrast against the dark-themed dashboard background (55-65% lightness range)
- **AND** the color SHALL be used as the card background or accent color
- **AND** this SHALL provide visual variety without requiring image assets

---

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column timeline layout organized by geographical proximity and date, with a dark-themed aesthetic.

#### Scenario: Dashboard layout structure
- **WHEN** the dashboard is displayed
- **THEN** the system SHALL implement a vertical-scrolling three-lane layout
- **AND** the Y-axis SHALL represent time (date/month) displayed on the left edge or lane dividers
- **AND** the X-axis SHALL represent distance from the user's registered region
- **AND** the overall dashboard SHALL use the dark surface palette from the design system

#### Scenario: Lane 1 - My City (Main Lane)
- **WHEN** displaying Lane 1 (50% screen width)
- **THEN** the system SHALL show events in the user's registered prefecture
- **AND** the system SHALL use mega-typography style cards with the display font at 4xl size or larger
- **AND** cards SHALL feature the artist name in extra-bold font as the dominant visual element
- **AND** cards SHALL apply a subtle gradient or shadow to create visual depth
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
- **AND** the system SHALL handle long text (e.g., via truncation or wrapping) to maintain layout integrity

---

### Requirement: Typography-First Card Design
The system SHALL prioritize typography and dynamic colors over images in all event cards, with enhanced visual treatments.

#### Scenario: Card visual design
- **WHEN** rendering event cards
- **THEN** the system SHALL use artist names as the primary visual element
- **AND** the system SHALL apply dynamic colors derived from artist names
- **AND** the system SHALL use bold, readable typography optimized for mobile screens using the display font
- **AND** the system SHALL ensure sufficient contrast between text and background colors (WCAG AA minimum)

#### Scenario: Card entrance animation
- **WHEN** event cards scroll into the viewport
- **THEN** the system SHALL apply a subtle entrance animation (fade-in or slide-up) as cards become visible
- **AND** cards in the same date group SHALL stagger their entrance slightly for visual rhythm

---

### Requirement: Bottom Sheet Detail Modal
The system SHALL display detailed event information in a bottom sheet modal when users tap any event card, with enhanced interaction design.

#### Scenario: Opening event details
- **WHEN** a user taps any event card in any lane
- **THEN** the system SHALL quickly slide up a detail bottom sheet from the bottom of the screen
- **AND** the modal SHALL maintain smooth animation (60fps target)

#### Scenario: Detail modal content
- **WHEN** the bottom sheet detail modal is displayed
- **THEN** the modal SHALL show the artist name prominently using the display font
- **AND** the modal SHALL display the event date and start time
- **AND** the modal SHALL display the venue name with a link to Google Maps
- **AND** the modal SHALL provide a "View Official Info" button linking to the source with an SVG link icon
- **AND** the modal SHALL provide an "Add to Calendar" button for native calendar export with an SVG calendar icon
- **AND** all icons SHALL use inline SVG (not Unicode emoji) for cross-platform visual consistency

#### Scenario: Swipe-to-dismiss gesture
- **WHEN** the bottom sheet is open
- **AND** the user swipes downward on the sheet
- **THEN** the system SHALL close the bottom sheet with a smooth slide-down animation
- **AND** the backdrop SHALL fade out simultaneously

---

### Requirement: Date Separator Styling
The system SHALL display date separators with enhanced visual treatment that matches the dark theme.

#### Scenario: Date separator rendering
- **WHEN** the dashboard renders date group headers
- **THEN** the date text SHALL use a contrasting accent color or semi-transparent surface color
- **AND** the separator SHALL visually anchor the timeline with adequate padding and typography weight
- **AND** the separator SHALL be sticky at the top during scroll

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

### Requirement: Dashboard Header Branding
The system SHALL display a branded header on the Dashboard page.

#### Scenario: Header display
- **WHEN** the Dashboard page is rendered
- **THEN** the header SHALL display "Live Highway" using the display font with brand styling
- **AND** the header SHALL use the dark surface palette
- **AND** lane labels (My City, Region, Others) SHALL be clearly visible with appropriate contrast

---

### Requirement: Toast Notification Design Enhancement
The system SHALL display toast notifications with vibrant, attention-grabbing styling.

#### Scenario: Toast visual design
- **WHEN** a toast notification is displayed (e.g., live event found during Artist Discovery)
- **THEN** the toast SHALL use a vibrant background color (brand accent or gradient) instead of neutral gray
- **AND** the toast SHALL enter with a spring/bounce animation (not just opacity fade)
- **AND** the toast text SHALL use the design system's typography tokens
