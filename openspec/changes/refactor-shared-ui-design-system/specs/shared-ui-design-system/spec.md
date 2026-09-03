## Purpose

The shared-ui-design-system capability gives Liverty Music's three web audiences
(fan-web, admin console, organizer console) one consistent, accessible UI
foundation — a single source of design tokens plus reusable UI primitives and a
console navigation shell — so screens look and behave consistently, adapt across
devices, and no screen is a dead end, while the fan-web bundle stays free of
console code.

## ADDED Requirements

### Requirement: Single source of design tokens

The system SHALL define its design tokens (color, spacing, typographic scale,
radius, elevation, and motion) in **one shared source** consumed by all three
web audiences. Each token value SHALL be defined once; audiences SHALL NOT keep
divergent copies of the same token, and SHALL NOT redefine a token under a
different name for the same role.

#### Scenario: Same primitive renders consistently across audiences

- **WHEN** the same UI primitive is rendered in fan-web, the admin console, and the organizer console
- **THEN** it uses identical token values (same brand color, spacing, radius, and type scale) so it looks the same in every audience

#### Scenario: A token change propagates everywhere from one edit

- **WHEN** a shared token's value is changed in the single source
- **THEN** the new value is reflected across all three audiences without any per-audience token edit

### Requirement: Shared reusable UI primitives

The system SHALL provide a **shared set of audience-agnostic UI primitives** —
at minimum: button, card, form field, badge, dialog/sheet, toast, spinner, and
back-link/breadcrumb — that every audience uses for those roles. An audience
SHALL NOT re-implement a primitive that already exists in the shared set. Each
shared primitive SHALL expose its variants and states (e.g. default / disabled /
busy) as a documented, reusable component.

#### Scenario: Screens reuse the shared primitive rather than a local copy

- **WHEN** any screen in any audience needs a role covered by the shared set (e.g. a button, card, or badge)
- **THEN** it uses the shared primitive, rendering consistent styling and interaction states, instead of a screen-local re-implementation

#### Scenario: Primitive states are consistent

- **WHEN** a shared primitive is placed in a busy or disabled state
- **THEN** it presents that state consistently everywhere it is used (same affordance and non-interactivity)

### Requirement: Console persistent navigation with no dead-end screens

Each console (admin and organizer) SHALL present a **persistent navigation
shell** around every screen — providing at least a home/return affordance, the
current organization/user context, and sign-out — and **every screen SHALL be
reachable through navigation and offer a way back**. No screen SHALL be reachable
only by typing a URL.

#### Scenario: Every console screen has navigation and a way back

- **WHEN** an operator opens any screen in a console
- **THEN** a persistent navigation (home + current context + sign-out) is present, and the screen offers a back or breadcrumb path to where it came from

#### Scenario: A created resource's status is reachable without a URL

- **WHEN** a resource that has a status/detail screen exists (for example a configured lottery phase)
- **THEN** that screen is reachable from a listing or navigation entry, not only by entering its URL directly

### Requirement: Responsive and accessible primitives

Shared primitives SHALL be **responsive** (adapt across viewport sizes without
overflow or clipping) and SHALL meet **baseline accessibility**: operable by
keyboard with a visible focus indicator, controls have accessible names, and text
meets sufficient contrast against its background.

#### Scenario: Primitive remains usable on a small viewport

- **WHEN** a shared primitive is rendered on a small (mobile) viewport
- **THEN** it remains usable with no horizontal overflow or clipped content

#### Scenario: Primitive is keyboard-operable

- **WHEN** a user navigates a shared interactive primitive with the keyboard
- **THEN** it is focusable with a visible focus indicator and exposes an accessible name

### Requirement: Consumer and console bundle isolation preserved

Introducing the shared UI layer SHALL NOT weaken bundle isolation: the fan-web
(consumer) entry bundle SHALL contain **no admin- or organizer-origin module**,
and shared UI code SHALL be safe for the consumer bundle — importing a shared
primitive SHALL NOT transitively pull any console-only module into fan-web.

#### Scenario: Consumer bundle graph excludes console code

- **WHEN** the fan-web consumer entry bundle is built
- **THEN** its chunk graph contains no module originating from the admin or organizer source directories

#### Scenario: Shared primitive is consumer-safe

- **WHEN** fan-web imports a shared UI primitive
- **THEN** the primitive pulls in only shared/consumer-safe code and no console-only module
