## ADDED Requirements

### Requirement: Scroll-Reveal Storytelling

When the dashboard preview is available and the landing page renders its value sections below the hero, the system SHALL present those sections as a continuous scrolling narrative and reveal each section's content on scroll entry. Reveal motion SHALL be entrance-only (fade with a short upward slide) and SHALL be fully disabled when the user prefers reduced motion. Content SHALL be fully readable and reachable regardless of whether reveal motion runs.

#### Scenario: Sections reveal on scroll entry

- **WHEN** an unauthenticated user scrolls the landing page and a value section enters the viewport
- **THEN** the system SHALL animate that section's content into view with an entrance-only fade and short upward slide
- **AND** each section SHALL reveal the first time it enters the viewport

#### Scenario: Reduced motion disables reveal animation

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **THEN** the system SHALL render all sections in their final visible state without reveal animation
- **AND** all section content SHALL remain fully readable and reachable

#### Scenario: Content is present without motion

- **WHEN** reveal motion does not run for any reason (reduced motion, or motion unsupported)
- **THEN** every value section's content SHALL still be rendered and reachable in the document

### Requirement: Timetable Value Section

The landing page SHALL present the concert auto-collection value pillar as a timetable section that displays the read-only dashboard preview as a complete, composed frame. The section SHALL NOT present the preview as a cropped or half-obscured peek. This section is rendered only when preview data is available.

#### Scenario: Timetable section shown with preview data

- **WHEN** an unauthenticated user reaches the timetable section and preview data is available
- **THEN** the system SHALL display the read-only concert timetable preview
- **AND** the preview SHALL be presented as a complete composed frame, not a cropped peek
- **AND** the section SHALL communicate that this timetable is auto-collected from the user's followed artists

#### Scenario: Timetable section absent without preview data

- **WHEN** preview data is unavailable
- **THEN** the system SHALL NOT render the timetable section
- **AND** the landing page SHALL fall back to the hero inline CTA behavior defined by `Passkey Authentication CTA`

### Requirement: Ticket and Goods Value Section

The landing page SHALL present the ticket and goods information value pillar as a section that shows the product's own concert detail view in a read-only form. The section SHALL surface the official-information link, the merchandise link, venue information, and the calendar affordance. Controls that require authentication (such as the ticket-journey tracker) SHALL NOT be shown to the anonymous visitor. On entry, the detail view SHALL play a single arrival motion; the motion SHALL be disabled under reduced-motion.

#### Scenario: Ticket and goods detail shown read-only

- **WHEN** an unauthenticated user reaches the ticket and goods section
- **THEN** the system SHALL display the concert detail view in a read-only form
- **AND** the view SHALL surface official-information, merchandise, venue, and calendar affordances
- **AND** the system SHALL NOT display authentication-gated controls such as the ticket-journey tracker

#### Scenario: Arrival motion on entry

- **WHEN** the ticket and goods section enters the viewport and reduced motion is not preferred
- **THEN** the system SHALL play a single arrival motion in which the detail view rises into place once
- **WHEN** reduced motion is preferred
- **THEN** the system SHALL render the detail view in its final state without arrival motion

### Requirement: New-Concert Notification Value Section

The landing page SHALL present the new-concert push notification value pillar as a section containing a mock notification card that represents an in-product new-concert alert, since a real operating-system push cannot be rendered inside the page. On entry, the mock card SHALL play a single arrival motion (a drop-in with a brief attention cue); the motion SHALL be disabled under reduced-motion.

#### Scenario: Notification mock card communicates the push value

- **WHEN** an unauthenticated user reaches the notification section
- **THEN** the system SHALL display a mock notification card representing a new-concert alert
- **AND** the card SHALL communicate that new concerts are delivered via push notification

#### Scenario: Notification arrival motion on entry

- **WHEN** the notification section enters the viewport and reduced motion is not preferred
- **THEN** the system SHALL play a single arrival motion in which the card drops in with a brief attention cue
- **WHEN** reduced motion is preferred
- **THEN** the system SHALL render the card in its final state without arrival motion

### Requirement: Landing Page Value Pillars Scope

The landing page SHALL communicate only the product capabilities that currently exist: concert-information auto-collection, ticket and goods information, and new-concert push notifications. The landing page SHALL NOT advertise capabilities that are not currently offered, and SHALL NOT present device-frame chrome, usage statistics, or social-proof material as value signals.

#### Scenario: Only existing capabilities are advertised

- **WHEN** the landing page renders its value sections
- **THEN** the system SHALL present only concert-information auto-collection, ticket and goods information, and new-concert push notifications
- **AND** the system SHALL NOT present any capability that is not currently offered
- **AND** the system SHALL NOT present usage statistics or social-proof material as value signals

## MODIFIED Requirements

### Requirement: Hero Screen Scroll Affordance

The landing page Screen 1 SHALL provide a single, clearly labeled affordance that invites the user to reveal the value sections below, whenever those sections are rendered. This affordance SHALL be the only primary interactive control on Screen 1 (apart from the language switcher) when the value sections are present, preserving the "message-first" intent of the hero screen. When the value sections are not rendered (no preview data), the scroll-affordance SHALL NOT be displayed, because there is no target to scroll to — the inline CTA fallback takes its place (see `Passkey Authentication CTA`). The affordance label and behavior are unchanged from the prior single-preview-screen design.

#### Scenario: Scroll affordance button is rendered when preview is available

- **WHEN** an unauthenticated user visits `/` and views Screen 1, and preview data is available
- **THEN** the system SHALL display a labeled scroll-affordance button within Screen 1
- **AND** the button SHALL be rendered as a `<button>` element
- **AND** the button SHALL have a minimum tap target of 44×44px
- **AND** the button SHALL be focusable via keyboard navigation
- **AND** the visible focus indicator SHALL be preserved under keyboard focus

#### Scenario: Tapping the scroll affordance reveals the preview

- **WHEN** the user taps or activates the scroll-affordance button
- **THEN** the system SHALL scroll the viewport to the first value section below the hero
- **AND** the scrolling SHALL use smooth-scroll animation by default

#### Scenario: Reduced motion preference disables smooth scroll

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **AND** the user activates the scroll-affordance button
- **THEN** the system SHALL jump directly to the first value section without a smooth-scroll animation

#### Scenario: Scroll affordance hidden when preview data is unavailable

- **WHEN** an unauthenticated user visits `/` and preview data is unavailable
- **THEN** the system SHALL NOT render the scroll-affordance button
- **AND** the hero Screen 1 SHALL instead render inline `[Get Started]` and `[Log In]` CTAs (see `Passkey Authentication CTA`)

#### Scenario: Button label is localized

- **WHEN** the landing page is rendered in Japanese
- **THEN** the button label SHALL display the Japanese scroll-affordance label
- **WHEN** the landing page is rendered in English
- **THEN** the button label SHALL display the English scroll-affordance label
