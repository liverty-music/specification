## Purpose

Defines the shared, audience-agnostic building blocks such as buttons, cards, form fields, and dialogs that every audience's screens reuse for consistent, responsive, accessible styling and interaction instead of each reimplementing its own copy.

## ADDED Requirements

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
