## Why

On touch devices, the trash icon column for unfollowing an artist was removed (`pointer: coarse`) to give the hype slider more horizontal space. Horizontal swipe was attempted but abandoned due to `<table>` scroll container constraints. Long-press (500ms) on an artist row opening a BottomSheet confirmation is the replacement unfollow trigger for touch devices, while desktop keeps the existing trash button.

## What Changes

- Add long-press (500ms) gesture on artist rows (`pointer: coarse` devices only) that opens an unfollow confirmation BottomSheet
- The BottomSheet shows artist name + "Unfollow" danger button + cancel
- Add help text to the My Artists `page-help` explaining the long-press gesture
- Desktop (`pointer: fine`) retains the existing trash icon column — no change

## Capabilities

### New Capabilities
- `long-press-unfollow`: Long-press gesture (500ms) on an artist row on touch devices triggers an unfollow confirmation BottomSheet. Confirmed unfollow calls the existing `unfollowArtist()` method (optimistic removal + undo toast).

### Modified Capabilities
- `my-artists`: Help content updated to document the long-press-to-unfollow gesture for touch devices.
- `onboarding-page-help`: No spec-level change — help content update is implementation detail only.

## Impact

- **Frontend only**: No backend or API changes
- **Files affected**:
  - `src/custom-attributes/long-press.ts` — new Aurelia 2 Custom Attribute (500ms timer, pointer cancel cleanup)
  - `src/components/artist-unfollow-sheet/` — new BottomSheet component (`.ts` + `.html` + `.css`)
  - `src/routes/my-artists/my-artists-route.html` — `long-press` attr on `<tr>`, `<artist-unfollow-sheet>` element
  - `src/routes/my-artists/my-artists-route.ts` — `openUnfollowSheet()` method
  - `src/main.ts` — register `LongPressCustomAttribute` + `ArtistUnfollowSheet`
  - `src/locales/*/translation.json` — new help text key
  - Help page content for `my-artists`
- **Dependencies**: None — uses native `setTimeout` + Pointer Events, no new packages
