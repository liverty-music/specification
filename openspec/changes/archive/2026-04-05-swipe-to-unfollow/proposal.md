## Why

The "My Artists" list always shows a trash icon column, consuming ~48px of horizontal space that could be used by the hype slider. On touch devices, unfollow via swipe is a more natural and discoverable interaction pattern — the permanent icon is wasted space.

## What Changes

- Remove the trash icon column from view on touch devices (`pointer: coarse`)
- Add swipe-left gesture on artist rows to trigger unfollow
- Adjust border-radius on the hype slider's last cell when trash column is hidden
- Implement as an Aurelia 2 Custom Attribute (`swipe-to-delete`) for reusability

## Capabilities

### New Capabilities
- `swipe-to-unfollow`: Touch gesture (swipe left) on an artist row triggers the unfollow action, replacing the always-visible trash icon on touch devices.

### Modified Capabilities
<!-- No existing spec-level behavior changes — unfollow itself is unchanged, only the trigger mechanism is added -->

## Impact

- **Frontend only**: No backend or API changes
- **Files affected**:
  - `src/routes/my-artists/my-artists-route.html` — remove `artist-unfollow-col` td on touch, add custom attribute to `<tr>`
  - `src/routes/my-artists/my-artists-route.css` — `@media (pointer: coarse)` to hide trash column, fix border-radius
  - `src/components/swipe-to-delete/` — new Aurelia 2 Custom Attribute (new files)
- **Accessibility**: Trash button remains in DOM (keyboard/screen reader accessible), hidden visually on touch only
- **Dependencies**: None — uses native Pointer Events API and WAAPI, no new packages
