## 1. Baseline

- [ ] 1.1 Record what each surface costs today, so the change has something to be measured against: with the discovery orb on screen, capture a trace; then scroll it out of view and background the tab, and confirm the animation-frame work continues in both. Do the same for the welcome page's ambient glow (which should already stop on a background tab, but not when scrolled away).

## 2. Suspend the discovery orb

- [ ] 2.1 Give the orb's host surface `content-visibility: auto` with a `contain-intrinsic-size` sized from its real layout box, so the browser has a reason to skip it and the page does not reflow when it does.
- [ ] 2.2 Suspend and resume the animation-frame loop from `contentvisibilityautostatechange` on that surface. Listen on the element itself or with `{ capture: true }` — the event does not bubble reliably. Use this event rather than an `IntersectionObserver`: this is rendering-heavy work, and the event is tied to the browser's rendering lifecycle so the loop resumes within the pre-render margin, before the orb is actually on screen.
- [ ] 2.3 Keep the physics simulation and the renderer intact while suspended — pause the loop, do not tear down or clear. The canvas must still show its last frame, so a partially-visible or just-resumed orb never appears blank or torn.
- [ ] 2.4 Handle the elapsed-time gap on resume. The loop computes a delta from the previous frame; after a long pause that delta is enormous and would make the simulation jump. Reset the timebase on resume so it continues rather than lurching.
- [ ] 2.5 Add a background-tab suspension too — the orb currently has none. A hidden tab and an off-screen element are different conditions and the rendering event only covers the second.
- [ ] 2.6 Confirm teardown still stops everything: leaving the route must leave no loop, timer or subscription running.

## 3. Suspend the ambient glow

- [ ] 3.1 Apply the same `content-visibility` + `contentvisibilityautostatechange` suspension to the welcome page's ambient glow canvas. Keep its existing `visibilitychange` handling — that covers the background tab, this covers being scrolled away, and both are needed.
- [ ] 3.2 Preserve the last painted frame while suspended, and keep the reduced-motion path (which paints one static frame and never loops) working — it must not be started by a resume.

## 4. Declarative entry and exit for the celebration overlay

- [ ] 4.1 Replace the `transitionend` listener and the fade-in-progress flag with `@starting-style` and discrete-transition behaviour. Both are Baseline since 2024-08-06, so no fallback is required; where unsupported the overlay toggles instantly instead of animating, which is acceptable for a celebration.
- [ ] 4.2 Keep the dismissal callback firing at the end of the exit. Restructure how that is detected if needed, but the flag tracking "am I currently fading" should not survive — it exists only because the choreography is in script.
- [ ] 4.3 Confirm the two celebration tiers (guest light acknowledgement, post-signup confetti) and the hand-off to the post-signup dialog are unchanged, including the one-shot storage flags.

## 5. Coach mark: visibility query instead of box measurement

- [ ] 5.1 First verify that a visibility query reports what this check actually needs — it exists to reject targets inside closed popovers that measure 0×0. The project's platform guidance does not cover this API, so confirm its support and semantics before relying on it. If it does not answer the same question, keep the measurement, record the finding as a non-issue, and skip 5.2.
- [ ] 5.2 Swap the box measurement for the visibility query. This is a layout read on a path that also retries on a timer, so removing it takes a forced layout out of a polling loop.

## 6. Ripple: size in CSS, position from the event

- [ ] 6.1 Size the ripple from CSS using container query units against its host, removing the host measurement. The diameter must still cover the host from the contact point, which is what the current calculation guarantees.
- [ ] 6.2 Take the contact point from the pointer event's element-relative coordinates instead of subtracting the host's box.
- [ ] 6.3 Keep the keyboard-activation path working: Enter/Space carry no pointer coordinates and must still ripple from the host's centre.
- [ ] 6.4 Keep the right-to-left mirroring correct — the ripple's horizontal origin is measured from the inline-start edge, which is the right edge under RTL.

## 7. Bottom sheet — spike first, rewrite only on a positive result

- [ ] 7.1 SPIKE: determine whether the sheet's dismiss gesture can be rebuilt on a modal dialog. `showModal()` and the `popover` attribute are mutually exclusive programmatic states, so this is a replacement of the current architecture, not an addition to it. `closedby="any"` covers light-dismiss; the open question is the scroll-snap drag and the `IntersectionObserver` that commits the close. Build it in isolation rather than reasoning about it.
- [ ] 7.2 If the spike is negative: stop here, record why in design.md, and leave the sheet alone. This is an acceptable outcome — the hand-rolled `inert` walk and focus trap stay, with a note explaining that they compensate for a deliberate architectural choice rather than being an oversight.
- [ ] 7.3 If the spike is positive: replace the ancestor-walking `inert` application, the focus trap and the Escape handling with what `<dialog>.showModal()` provides natively, and write the `bottom-sheet-ce` delta — its stated behaviour names all three as component-managed, so the requirement changes.
- [ ] 7.4 If it proceeds, verify against the existing capability's scenarios before considering it done: focus containment, Escape, background inertness, the dismiss gesture, reversing the gesture mid-drag, and the background remaining interactive during the close.

## 8. Tests and verification

- [ ] 8.1 Add tests that a suspended surface stops its per-frame work and resumes — both are invisible when working and quiet when broken, so neither can be left to manual noticing.
- [ ] 8.2 `make lint` + `make test`, plus the Storybook component tests.
- [ ] 8.3 Visual baselines must be unchanged across every item in this change. A baseline diff here means something was got wrong — do NOT regenerate baselines to make it pass.
- [ ] 8.4 Device check: the orb and the glow stop when scrolled away and when the tab is backgrounded, both resume showing a complete frame, and the orb's resume does not read as a stutter.

## 9. Close-out

- [ ] 9.1 Sync the `offscreen-work-suspension` delta into the main specs before archiving, plus the `bottom-sheet-ce` delta if 7.3 happened.
- [ ] 9.2 Record in the PR which items shipped and which were dropped, and for anything dropped, why — particularly the bottom sheet, whose outcome is unknown when this change is written.
