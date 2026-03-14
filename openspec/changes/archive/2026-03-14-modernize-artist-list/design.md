## Context

Current DOM structure (6 levels deep):

```
.artist-list (overflow-y: auto, flex: 1)
  .artist-list-inner (padding only)          ← unnecessary wrapper
    .artist-list-item (overflow: hidden)     ← clip wrapper for swipe
      .delete-zone (position: absolute)      ← always in DOM, every row
      .artist-row (flex, transform)          ← JS-driven translateX per frame
        .indicator
        .name
        <hype-inline-slider>                 ← independent grid context
```

Problems:
- `.artist-list-inner` exists only for padding — can be applied to `.artist-list` directly
- `.artist-list-item` exists only to clip `.artist-row` during swipe — unnecessary if swipe uses scroll-snap (scroll container clips by default)
- `.delete-zone` is position-absolute behind every row — always rendered even when not swiping
- `.artist-row` transform is driven by JS touch handlers on the main thread

## Goals / Non-Goals

**Goals:**
- Flatten DOM from 6 levels to 3 levels
- Move swipe tracking from main thread (JS) to compositor thread (native scroll)
- Align hype header columns with slider dots via shared `grid-template-areas`
- Add smooth dismiss animation via View Transitions API
- Remove long-press unfollow from list view

**Non-Goals:**
- Changing the hype-inline-slider component API (props/events)
- Modifying the Grid (Festival) view
- Adding new unfollow gestures (e.g., button-based)

## Decisions

### 1. Flattened DOM structure

Target structure (3 levels deep):

```
.artist-list (overflow-y: auto, padding)
  header.hype-legend
    (grid: 2fr 1fr 1fr 1fr 1fr)
    areas: "spacer watch home nearby away"

  .artist-row (overflow-x: auto, scroll-snap-type: x mandatory)
    .artist-row-content (grid: 2fr 1fr 1fr 1fr 1fr)
      areas: "name watch home nearby away"
      [name]: .artist-identity (indicator + name)
      [col 2/-1]: <hype-inline-slider>
    .dismiss-end (scroll-snap-align: end)
```

Changes from current:
- `.artist-list-inner` removed — padding moves to `.artist-list`
- `.artist-list-item` removed — `.artist-row` is now the direct child
- `.delete-zone` removed — replaced by `.dismiss-end` inside the scroll container
- `.artist-row` changes role from "swipeable content" to "scroll container"
- `.artist-row-content` is the new grid layout element

### 2. Scroll-snap swipe-to-dismiss

Each `.artist-row` is a horizontal scroll container:

```css
.artist-row {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
}

.artist-row-content {
  flex: 0 0 100%;
  scroll-snap-align: start;
}

.dismiss-end {
  flex: 0 0 5rem;
  scroll-snap-align: end;
}
```

Swipe behavior:
- User swipes left → native horizontal scroll (compositor thread, no jank)
- `scroll-snap` snaps to either "content" (cancel) or "dismiss-end" (trigger delete)
- A single `scroll` event listener checks `scrollLeft > threshold` to trigger dismiss
- No `touchstart`/`touchmove`/`touchend` handlers needed

```
Normal state:
┌─ .artist-row (viewport) ──────────────────┐
│ ┌─ .artist-row-content ─────────────────┐ │ .dismiss-end
│ │ ● Taylor Swift   ·  ·  ●  ·          │ │ (off-screen)
│ └───────────────────────────────────────┘ │
└───────────────────────────────────────────┘

After swipe left:
        ┌─ .artist-row (viewport) ──────────────────┐
        │ ───────────────────────────┐ ┌────────────┐│
        │ ·  ●  ·                    │ │     🗑️     ││
        │ ───────────────────────────┘ └────────────┘│
        └───────────────────────────────────────────┘
```

**Why scroll-snap over JS transform:**
- Scroll runs on the compositor thread — zero main-thread work during swipe
- `scroll-snap-type: x mandatory` handles snap-back automatically
- No clip wrapper needed — scroll container clips by definition
- `scrollbar-width: none` hides the scrollbar
- Accessible by default — screen readers can navigate via scroll semantics

### 3. Column alignment via shared `grid-template-areas`

Header and artist-row-content use identical grid definitions:

```css
/* Shared pattern */
grid-template-columns: 2fr repeat(4, 1fr);
```

**Header:**
```css
.hype-legend {
  display: grid;
  grid-template-columns: 2fr repeat(4, 1fr);
  grid-template-areas: "spacer  watch  home  nearby  away";
}
```

```
┌───────────┬────────┬────────┬────────┬────────┐
│  spacer   │ watch  │  home  │ nearby │  away  │
│   (2fr)   │ (1fr)  │ (1fr)  │ (1fr)  │ (1fr)  │
│           │   👀   │   🔥   │  🔥🔥  │ 🔥🔥🔥 │
└───────────┴────────┴────────┴────────┴────────┘
```

First `.hype-legend-item` starts at `grid-column: 2` to skip the spacer.

**Artist row content:**
```css
.artist-row-content {
  display: grid;
  grid-template-columns: 2fr repeat(4, 1fr);
  grid-template-areas: "name  watch  home  nearby  away";
}
```

```
┌───────────────────┬────────┬────────┬────────┬────────┐
│       name        │ watch  │  home  │ nearby │  away  │
│      (2fr)        │ (1fr)  │ (1fr)  │ (1fr)  │ (1fr)  │
│ ● Taylor Swift    │   ·    │   ·    │   ●    │   ·    │
└───────────────────┴────────┴────────┴────────┴────────┘
```

Alignment is guaranteed: both elements share the same `fr` ratio at the same parent width. The header and `.artist-row-content` both inherit the full width of `.artist-list` (minus padding), so column lines match exactly.

`<hype-inline-slider>` spans `grid-column: 2 / -1`. Its internal `repeat(4, 1fr)` grid subdivides the same 4-column span as the header, so dots align with emojis automatically.

### 4. View Transitions dismiss animation

When an artist is removed from the list, the remaining rows should reflow smoothly:

```typescript
async executeDismiss(artist: FollowedArtist) {
  if (!document.startViewTransition) {
    await this.unfollowArtist(artist);
    return;
  }
  document.startViewTransition(async () => {
    await this.unfollowArtist(artist);
  });
}
```

Each `.artist-row` gets a unique `view-transition-name` so the browser can animate individual rows sliding up to fill the gap. No manual animation CSS required — the browser interpolates between old and new DOM states.

```css
.artist-row {
  view-transition-name: var(--_vt-name);
}
```

The `--_vt-name` custom property is set per-row via inline style bound to the artist ID.

### 5. Name area internal structure

The `name` grid area contains indicator + artist name, wrapped in `.artist-identity`:

```html
<div class="artist-identity">
  <span class="artist-indicator" style="background: ${artist.color}"></span>
  <span class="artist-name">${artist.name}</span>
</div>
```

Styled as `display: flex; gap: var(--space-xs); align-items: center; min-inline-size: 0` for horizontal layout with ellipsis truncation.

### 6. Long-press removal

Long-press unfollow is removed from list view entirely. The only unfollow gesture is swipe-to-dismiss. This simplifies the event handling (no `setTimeout` timers, no `clearLongPressTimer`). Grid (Festival) view retains its own long-press context menu as a separate concern.

## Risks / Trade-offs

- **[Risk] Nested scroll containers (vertical list + horizontal swipe)** → Browser handles direction disambiguation natively. The `.artist-row` has horizontal scroll, `.artist-list` has vertical scroll. Browsers disambiguate based on initial gesture direction. Needs device testing to confirm feel
- **[Risk] View Transitions API browser support** → Fallback: if `document.startViewTransition` is undefined, execute unfollow immediately without animation. Progressive enhancement, not a hard dependency
- **[Risk] `scrollbar-width: none` support** → Baseline 2024. Fully supported in Chrome, Firefox, Safari 16+. No concern for target audience
- **[Risk] Hype slider tap vs horizontal scroll conflict** → `scroll-snap` only activates on horizontal drag. Taps on dots fire `click` events normally. The slider dots have `touch-action: manipulation` which prevents double-tap zoom but allows click
