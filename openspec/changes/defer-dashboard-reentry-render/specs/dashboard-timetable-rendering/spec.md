## ADDED Requirements

### Requirement: Page identity paints independent of the timetable render

On dashboard tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — MUST be painted at navigation intent, independent of
and ahead of the timetable's render. The re-entry render of the cached timetable
MUST NOT be driven from a pre-first-paint lifecycle hook (so it cannot coalesce
into the same paint as the optimistic page-identity update and starve it).

While the cached timetable is being deferred into a subsequent frame, the view
MUST show the loading skeleton, never the empty state, and MUST NOT lose the
background refresh, the data-ready celebration/onboarding latch, or an in-flight
deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the dashboard navigation tab from another tab
- **THEN** the shell header title and the active bottom-nav tab switch (paint) to
  the dashboard's identity before the timetable's render work runs — measured on
  the reference profile, an early paint frame containing the switched shell
  appears ahead of the timetable render block
- **AND** the tap's Interaction to Next Paint is substantially lower than the
  pre-change baseline and the shell is interactive while the timetable fills in

#### Scenario: Deferred cached render shows a skeleton, not an empty flash

- **WHEN** the cached timetable paint is deferred to a subsequent frame on re-entry
- **THEN** the intervening frame shows the loading skeleton
- **AND** the empty state ("no concerts") never renders while a cached paint is
  pending

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is deferred past the first paint
- **THEN** the background refresh still fetches and swaps in fresh data
- **AND** the data-ready celebration / onboarding-completion latch still fires
  once when due, and a pending `/concerts/:id` deep-link still opens the detail
  sheet
