## Purpose

Defines the app's interaction-feedback contract: every interaction acknowledges immediately, communicates
in-progress state, and confirms its outcome, using shared feedback primitives (ripple, press-morph, skeleton,
haptic, list transitions, selection morph) applied consistently across all primary screens rather than
siloed in discovery.

## ADDED Requirements

### Requirement: Immediate tactile acknowledgement on press

Tappable controls (buttons and interactive cards) across the app SHALL acknowledge a press within the short
motion band via a shared primitive: a contact-point ripple and a round↔squircle corner morph on `:active`,
using a spatial spring. The primitive SHALL be applied app-wide (not only in discovery) via a reusable
mechanism, and SHALL keep the clickable hit area stable while the visual shape morphs.

#### Scenario: Button press ripples and morphs

- **WHEN** a user presses a button or tappable card
- **THEN** a ripple originates at the contact point and the corner radius morphs with a spatial spring, then
  settles on release

#### Scenario: Hit target is preserved during morph

- **WHEN** the press-morph animates the visual shape
- **THEN** the interactive/clickable bounds remain unchanged and the target stays ≥ 44–48px

#### Scenario: Reduced motion still acknowledges

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the ripple/morph animation is suppressed but a non-motion acknowledgement (e.g. state-layer or
  opacity change) still confirms the tap

### Requirement: Layout-preserving skeleton loading

While first-load content is pending, screens SHALL display a skeleton placeholder that preserves the final
layout, replacing bare "loading" text or a centered spinner for content regions. The skeleton SHALL be
removed when content resolves, and SHALL not introduce layout shift when replaced by real content.

#### Scenario: Content region shows a skeleton while loading

- **WHEN** a screen (e.g. the dashboard) is loading its primary content
- **THEN** it renders a skeleton matching the content's layout instead of a text-only loading state

#### Scenario: No layout shift on resolve

- **WHEN** the content finishes loading and replaces the skeleton
- **THEN** the surrounding layout does not jump (no cumulative layout shift attributable to the swap)

#### Scenario: Skeleton animation respects reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the skeleton shows a static placeholder without a shimmer animation

### Requirement: Haptic feedback for meaningful confirmations

The app SHALL provide a shared haptic feedback capability (generalized from the discovery orb) and invoke it
on meaningful confirm actions (e.g. follow/unfollow confirmation) where supported by the platform. Haptics
SHALL be feature-detected and degrade silently where unavailable (e.g. iOS Safari lacks the Web Vibration
API), and SHALL never be the sole feedback for an action.

#### Scenario: Confirm action triggers haptic where supported

- **WHEN** a user completes a meaningful confirm action on a device that supports vibration
- **THEN** a short haptic pulse fires in addition to the visual feedback

#### Scenario: Graceful degradation without vibration support

- **WHEN** the platform does not support the Web Vibration API
- **THEN** the action still completes with full visual feedback and no error

### Requirement: Animated list enter and exit

Content and following lists SHALL animate item insertion and removal (enter/exit) rather than swapping the
DOM instantly, using discrete-transition primitives with a reduced-motion fallback that lands the end state.

#### Scenario: Unfollow animates the item out

- **WHEN** a user removes an item from a list (e.g. unfollows an artist)
- **THEN** the item animates out before removal rather than disappearing instantly

#### Scenario: New item animates in

- **WHEN** an item is added to a rendered list
- **THEN** it animates in (enter transition) rather than appearing abruptly

#### Scenario: Reduced motion lands end state

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** list changes apply without transition, arriving directly at the final state

### Requirement: Animated selection state

Selection controls (bottom-nav tabs, filter chips) SHALL animate the transition into the selected state with
a spatial spring — including a shape morph where the selected element becomes rounder — driven by a real
selection attribute, not hover, with a reduced-motion fallback.

#### Scenario: Selecting a nav tab springs into state

- **WHEN** a user selects a navigation tab or filter chip
- **THEN** the selected element animates into its selected treatment (color plus a spring shape morph) rather
  than switching statically

#### Scenario: Selection is driven by state, not hover

- **WHEN** the selection morph is evaluated
- **THEN** it reflects the actual selected/`aria`-state attribute and does not trigger on hover alone

### Requirement: Expression budget and accessibility guarantees

Feedback SHALL follow the Material 3 expression budget — a small number of hero moments per flow with the
rest kept foundational — and SHALL never cost legibility, hit area, labels, reduced-motion support, or
high-contrast/forced-colors survivability.

#### Scenario: Every animation has a reduced-motion path

- **WHEN** any feedback animation is added
- **THEN** it includes a `prefers-reduced-motion: reduce` branch that reaches the same end state without
  overshoot

#### Scenario: Feedback does not degrade accessibility

- **WHEN** a feedback primitive is applied to a control
- **THEN** text labels remain, contrast targets hold, the touch target stays ≥ 44–48px, and the control
  remains operable under `forced-colors: active`
