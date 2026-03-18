## Context

The Aurelia 2 frontend has grown to 25 components and 9 routes. Dialog/sheet patterns were implemented independently per feature, resulting in 5 separate dialog implementations with nearly identical CSS for backdrop, handle-bar, slide-in transitions, and scroll containers. The event-detail-sheet was recently optimized to use the Popover API with CSS scroll-snap dismiss — this is the gold standard implementation that all dialogs should adopt.

Current state:
- **event-detail-sheet**: Popover API, scroll-snap dismiss, backdrop opacity linked to scroll progress
- **user-home-selector**: `showModal()` API, CSS translate transition, backdrop click dismiss
- **settings language-selector**: Copy-pasted CSS from user-home-selector (~80 lines)
- **hype-notification-dialog**: `showModal()`, centered, no transition
- **error-banner**: `showModal()`, centered, no transition
- **tickets center-dialogs**: `showModal()`, centered, no transition
- **notification-prompt / pwa-install-prompt**: `popover="manual"`, top-positioned, 99% identical CSS

The app uses CUBE CSS methodology with `@layer` cascade ordering and `@scope` for component isolation.

## Goals / Non-Goals

**Goals:**
- Eliminate ~350+ lines of duplicated CSS across dialog, prompt, and spinner patterns
- Create Storybook-testable primitive CEs that enforce consistent UX
- Simplify DOM structure by removing redundant wrapper elements
- Establish `<bottom-sheet>` as the single dialog primitive for all overlay content
- Rename components to match their actual UX roles (snack-bar, toast)

**Non-Goals:**
- Refactoring business logic within consuming components (ViewModels stay as-is)
- Extracting button styles into a CE (deferred to a follow-up change)
- Adding new features to any of the consolidated components
- Changing visual design or animations beyond what's needed for unification

## Decisions

### D1: All dialogs become bottom-sheets (no center dialog variant)

The `<bottom-sheet>` CE uses the Popover API exclusively. All current center-dialog usages (hype-notification-dialog, error-banner, tickets QR/generating dialogs) migrate to bottom-sheet presentation.

**Rationale**: Mobile-first app where thumb reach matters. Bottom sheets are the standard mobile pattern for contextual content. Maintaining two presentation modes adds complexity for marginal benefit.

**Alternative considered**: Keep a `position` bindable (`center` | `bottom`). Rejected — adds API surface for a pattern we want to eliminate.

### D2: Popover API over `showModal()`

All `<bottom-sheet>` instances use `popover="auto"` (light dismiss) by default, with `popover="manual"` for non-dismissable cases. No `showModal()` usage.

**Rationale**: Popover API provides free light dismiss (Escape, click-outside, Android back gesture) without manual event handling. The event-detail-sheet already proves this works well. `showModal()` requires manual backdrop-click and cancel-event handling.

**Migration for user-home-selector**: Replace `showModal()`/`close()` with `showPopover()`/`hidePopover()`. Remove `handleCancel()` and `handleBackdropClick()` methods.

### D3: Scroll-snap dismiss for all bottom-sheets

Every `<bottom-sheet>` gets the scroll-snap dismiss zone (swipe down to close). The `dismissable` bindable controls whether the dismiss zone is rendered.

**Rationale**: Consistent gesture-based UX across all sheets. Users learn one interaction pattern.

### D4: `<bottom-sheet>` API — minimal bindables

```typescript
export class BottomSheet {
  @bindable open = false      // two-way: controls visibility
  @bindable dismissable = true // false: no dismiss zone, popover="manual"
}
```

The CE dispatches a `'sheet-closed'` CustomEvent when dismissed (light dismiss, scroll-snap, or backdrop click). The parent responds by setting `open = false`.

**Rationale**: Two bindables cover all current use cases. `open` is the universal control. `dismissable` handles onboarding lock-in and required-selection scenarios.

### D5: `<toast>` replaces notification-prompt + pwa-install-prompt

A single `<toast>` CE with `popover="manual"` positioned at the top of the viewport. Content is fully slotted.

```typescript
export class Toast {
  @bindable open = false
}
```

**Rationale**: The two prompt components have identical HTML structure and 99% identical CSS. The only difference is the icon (emoji vs SVG) — handled by slotting.

### D6: `toast-notification` renamed to `<snack-bar>`

Rename only — no functional changes. The existing `Toast` class in `toast.ts` is renamed to `Snack` (or `SnackMessage`) to avoid collision with the new `<toast>` CE.

**Rationale**: "Snack bar" accurately describes an auto-dismissing notification at the bottom. "Toast" describes a user-action banner at the top. This aligns with Material Design terminology.

### D7: `<loading-spinner>` as standalone CE

```typescript
export class LoadingSpinner {
  @bindable size: 'sm' | 'md' | 'lg' = 'md'
}
```

HTML: `<output role="status" aria-busy="true"><span class="spinner"></span></output>`

**Rationale**: Spinner is a visual primitive like `<svg-icon>`. It has 6 CSS properties — this is a Block in CUBE terms, not a utility. CE enables Storybook isolation and consistent ARIA semantics.

### D8: `<state-placeholder>` simplified to icon + slot

```typescript
export class StatePlaceholder {
  @bindable icon = ''
}
```

All content (title, description, buttons, spinner) goes through `<au-slot>`. Remove dead `ctaLabel` bindable and `title`/`description` bindables.

**Rationale**: Current `title`/`description` bindables duplicate what `<au-slot>` already provides. Most usages already slot custom content. Single `icon` bindable remains because every state-placeholder uses an icon at the top.

## Risks / Trade-offs

**[R1] Center-dialog content may feel awkward in bottom-sheet** → Small content (hype-notification-dialog) will have a short bottom-sheet. This is acceptable — mobile apps commonly show small bottom sheets. The content fills naturally with `max-block-size: fit-content` on the sheet body.

**[R2] Popover API browser support** → Popover API is Baseline 2024 (Chrome 114+, Safari 17+, Firefox 125+). The app already uses it in event-detail-sheet without polyfill. No new risk.

**[R3] Scroll-snap dismiss on short content** → If the sheet body is shorter than the viewport, the dismiss zone scroll distance is minimal. Mitigation: ensure `min-block-size` on the sheet-page so there's always enough scroll travel for the snap engine.

**[R4] Renaming toast-notification → snack-bar** → All import paths and template references must be updated. Grep for `toast-notification` and `Toast` class references. The `Toast` EventAggregator event class rename to `Snack`/`SnackMessage` touches ~8 files.

**[R5] Removing title/description bindables from state-placeholder** → All current usages must migrate to slotted content. This is straightforward but touches 4-5 template files.
