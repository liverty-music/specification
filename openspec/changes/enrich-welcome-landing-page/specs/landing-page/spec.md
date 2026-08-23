## ADDED Requirements

### Requirement: Guided Product Demo Sequence

When preview data is available, the landing page SHALL present a single guided product-demo sequence below the hero that replays the product's core journey — new-concert notification, auto-collected timetable, and ticket/goods detail — as one connected flow. The sequence SHALL begin when it scrolls into view. It SHALL communicate all three value pillars. All sequence motion SHALL be disabled when the user prefers reduced motion, and the demo's end state (an interactive timetable the visitor can explore) SHALL remain reachable regardless of whether the sequence animates.

#### Scenario: Demo begins on scroll entry

- **WHEN** an unauthenticated user with preview data available scrolls the demo into view
- **THEN** the system SHALL start the sequence by presenting a mock new-concert push notification
- **AND** the notification SHALL animate in to draw attention (a drop-in entrance) indicating new activity, and a pulsing hint SHALL invite the visitor to advance

#### Scenario: Notification advances to the timetable

- **WHEN** the user taps the mock notification
- **THEN** the system SHALL transition the notification into the concert timetable
- **WHEN** the user does not interact within a short interval
- **THEN** the system SHALL auto-advance to the timetable so the sequence always completes

#### Scenario: Notification transitions into the timetable

- **WHEN** the sequence advances from the notification to the timetable and reduced motion is not preferred
- **THEN** the system SHALL play a sequential transition — the notification is dismissed, and only after it has fully left does the timetable appear — so the two views never overlap
- **WHEN** reduced motion is preferred
- **THEN** the system SHALL present the timetable directly without transition motion

#### Scenario: Reduced motion presents the interactive end state directly

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **THEN** the system SHALL present the interactive timetable without the notification, transition, or attention-cue motion
- **AND** the timetable and its detail interaction SHALL remain fully usable

#### Scenario: Content present without motion

- **WHEN** demo motion does not run for any reason (reduced motion or script failure)
- **THEN** the interactive timetable SHALL still be rendered and reachable in the document

### Requirement: Interactive Timetable Detail

The landing page SHALL present the concert auto-collection pillar as the product's own timetable, rendered as a complete composed frame, and SHALL make its concert cards interactive so that activating a card opens the product's real concert detail view. The detail view SHALL surface the official-information link, the merchandise link, venue information, and the calendar affordance. Controls that require authentication (such as the ticket-journey tracker) SHALL NOT be shown to the anonymous visitor. The landing page SHALL guide the visitor to this interaction rather than relying on a hover-only affordance.

#### Scenario: Timetable shown as a composed frame

- **WHEN** an unauthenticated user reaches the timetable and preview data is available
- **THEN** the system SHALL display the concert timetable as a complete composed frame, not a cropped peek
- **AND** the system SHALL communicate that this timetable is auto-collected from the user's followed artists

#### Scenario: Guidance to open a concert

- **WHEN** the timetable becomes interactive in the demo
- **THEN** the system SHALL surface a guidance affordance directing the visitor to open a concert card
- **AND** the guidance SHALL NOT depend on a pointer hover state

#### Scenario: Card opens the real detail view

- **WHEN** the unauthenticated user activates a concert card
- **THEN** the system SHALL open the product's real concert detail view for that concert
- **AND** the view SHALL surface official-information, merchandise, venue, and calendar affordances
- **AND** the system SHALL NOT display authentication-gated controls such as the ticket-journey tracker

#### Scenario: Timetable absent without preview data

- **WHEN** preview data is unavailable
- **THEN** the system SHALL NOT render the demo or the timetable
- **AND** the landing page SHALL fall back to the hero inline CTA behavior defined by `Passkey Authentication CTA`

### Requirement: New-Concert Notification Cue

The landing page SHALL represent the new-concert push notification pillar with a mock notification card that stands in for an in-product new-concert alert, since a real operating-system push cannot be rendered inside the page. The mock notification SHALL be the entry point of the guided demo sequence and SHALL communicate that new concerts are delivered via push notification. Its attention-cue motion SHALL be disabled under reduced motion.

#### Scenario: Notification communicates the push value

- **WHEN** an unauthenticated user reaches the demo
- **THEN** the system SHALL display a mock notification card representing a new-concert alert
- **AND** the card SHALL communicate that new concerts are delivered via push notification

### Requirement: Hero Kinetic Brand Treatment

The landing page hero SHALL present the product brand wordmark with a continuous, ambient kinetic treatment consistent with the product's festival-spotlight visual vocabulary, so the hero reads as a living product rather than static text. The treatment SHALL animate only compositor-friendly properties and SHALL be disabled under reduced motion, leaving the brand fully legible.

#### Scenario: Brand wordmark is kinetic

- **WHEN** an unauthenticated user views the hero and reduced motion is not preferred
- **THEN** the system SHALL animate the brand wordmark with an ambient kinetic treatment
- **WHEN** reduced motion is preferred
- **THEN** the system SHALL render the brand wordmark in a static, fully legible state

### Requirement: Ambient Background

The landing page SHALL render an ambient background effect behind its content to give the dark surface depth and reinforce the product's discovery theme. The effect SHALL be decorative, SHALL NOT capture pointer input, SHALL keep foreground content legible, and SHALL be disabled or static under reduced motion.

#### Scenario: Ambient background is decorative and non-blocking

- **WHEN** the landing page renders
- **THEN** the system SHALL display the ambient background behind the content
- **AND** the ambient background SHALL NOT intercept pointer interaction with the content
- **WHEN** reduced motion is preferred
- **THEN** the system SHALL disable or freeze the ambient background motion

### Requirement: Landing Page Value Pillars Scope

The landing page SHALL communicate only the product capabilities that currently exist: concert-information auto-collection, ticket and goods information, and new-concert push notifications. The landing page SHALL NOT advertise capabilities that are not currently offered, and SHALL NOT present device-frame chrome, usage statistics, social-proof material, or a promotional name marquee as value signals.

#### Scenario: Only existing capabilities are advertised

- **WHEN** the landing page renders its demo and value content
- **THEN** the system SHALL present only concert-information auto-collection, ticket and goods information, and new-concert push notifications
- **AND** the system SHALL NOT present any capability that is not currently offered
- **AND** the system SHALL NOT present usage statistics, social-proof material, or a promotional name marquee as value signals

## MODIFIED Requirements

### Requirement: Hero Screen Scroll Affordance

The landing page Screen 1 SHALL provide a single, clearly labeled affordance that invites the user to reveal the guided demo below, whenever the demo is rendered. This affordance SHALL be the only primary interactive control on Screen 1 (apart from the language switcher) when the demo is present, preserving the "message-first" intent of the hero screen. When the demo is not rendered (no preview data), the scroll-affordance SHALL NOT be displayed, because there is no target to scroll to — the inline CTA fallback takes its place (see `Passkey Authentication CTA`). The affordance label and behavior are unchanged from the prior single-preview-screen design.

#### Scenario: Scroll affordance button is rendered when preview is available

- **WHEN** an unauthenticated user visits `/` and views Screen 1, and preview data is available
- **THEN** the system SHALL display a labeled scroll-affordance button within Screen 1
- **AND** the button SHALL be rendered as a `<button>` element
- **AND** the button SHALL have a minimum tap target of 44×44px
- **AND** the button SHALL be focusable via keyboard navigation
- **AND** the visible focus indicator SHALL be preserved under keyboard focus

#### Scenario: Tapping the scroll affordance reveals the preview

- **WHEN** the user taps or activates the scroll-affordance button
- **THEN** the system SHALL scroll the viewport to the guided demo below the hero
- **AND** the scrolling SHALL use smooth-scroll animation by default

#### Scenario: Reduced motion preference disables smooth scroll

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **AND** the user activates the scroll-affordance button
- **THEN** the system SHALL jump directly to the demo without a smooth-scroll animation

#### Scenario: Scroll affordance hidden when preview data is unavailable

- **WHEN** an unauthenticated user visits `/` and preview data is unavailable
- **THEN** the system SHALL NOT render the scroll-affordance button
- **AND** the hero Screen 1 SHALL instead render inline `[Get Started]` and `[Log In]` CTAs (see `Passkey Authentication CTA`)

#### Scenario: Button label is localized

- **WHEN** the landing page is rendered in Japanese
- **THEN** the button label SHALL display the Japanese scroll-affordance label
- **WHEN** the landing page is rendered in English
- **THEN** the button label SHALL display the English scroll-affordance label
