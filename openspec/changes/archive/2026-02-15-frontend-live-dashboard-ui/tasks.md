## 1. Color Generation Utility

- [x] 1.1 Create `src/components/live-highway/color-generator.ts` with deterministic artist name to HSL color function
- [x] 1.2 Add contrast-safe defaults (saturation 70%, lightness 45%) and ensure white text readability

## 2. Event Card Component

- [x] 2.1 Create `event-card` component (`src/components/live-highway/event-card.ts` and `.html`) that renders artist name as primary typography element with dynamic background color
- [x] 2.2 Support three card variants via a `lane` attribute: `main` (mega-typography, artist name only), `region` (medium card with artist + prefecture), `other` (text-only list item with artist + city)

## 3. Bottom Sheet Detail Modal

- [x] 3.1 Create `event-detail-sheet` component (`src/components/live-highway/event-detail-sheet.ts` and `.html`) with slide-up CSS transition using `transform: translateY()`
- [x] 3.2 Display event details: artist name, date/time, venue with Google Maps link, official info link, and "Add to Calendar" button
- [x] 3.3 Add open/close logic triggered by card click events and backdrop dismiss

## 4. Highway Lane Component

- [x] 4.1 Create `highway-lane` component (`src/components/live-highway/highway-lane.ts` and `.html`) that renders a vertical list of event cards for a given lane type and event list

## 5. Live Highway Container

- [x] 5.1 Create `live-highway` component (`src/components/live-highway/live-highway.ts` and `.html`) with CSS Grid three-column layout (50% / 30% / 20%)
- [x] 5.2 Add sticky date separator headers spanning all lanes, grouping events chronologically
- [x] 5.3 Add empty state messaging per lane when no events are available

## 6. Data Layer

- [x] 6.1 Extend `ConcertServiceClient` with a method to list upcoming concerts (or add a new `LiveEventService` if the RPC exists)
- [x] 6.2 Add client-side grouping logic to assign concerts to lanes based on user's registered prefecture vs event prefecture/region

## 7. Dashboard Route Integration

- [x] 7.1 Update `src/routes/dashboard.ts` and `.html` to render the `live-highway` component, fetch events on activation, and pass grouped data to the highway
- [x] 7.2 Wire card click events to open the `event-detail-sheet` with the selected event

## 8. Mobile Layout and Responsiveness

- [x] 8.1 Ensure the three-lane layout fits mobile portrait viewport with no horizontal scroll
- [x] 8.2 Optimize touch targets, font sizes, and spacing for one-handed thumb navigation
