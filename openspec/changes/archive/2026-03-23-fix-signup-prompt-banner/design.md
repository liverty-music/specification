## Context

The signup-prompt-banner is the primary conversion CTA for guest users who completed onboarding without creating an account. It currently has three bugs:

1. **Invisible background**: `--_surface-bg: oklch(100% 0 0deg / 5%)` renders nearly transparent on the dark surface base (`oklch(18% 0.04 275deg)`).
2. **Missing on My Artists**: `showSignupBanner` is never set to `true` in `loading()` — only triggered by notification dialog dismissal via `onDialogDismissed()`.
3. **401 on Dashboard**: `DashboardService.fetchJourneyMap()` calls `TicketJourneyRpcClient.listByUser()` without checking `isAuthenticated`, producing a console error for every unauthenticated page load.

Existing design tokens: `--color-surface-raised`, `--color-brand-primary`, `--color-brand-secondary`, `--radius-button`, `--space-*` scale.

## Goals / Non-Goals

**Goals:**
- Fix all three bugs so the banner is visible, displayed on both pages, and causes no 401 errors.
- Increase visual prominence of the CTA button with a subtle glow pulse animation.
- Add a slide-in entrance animation to draw attention.
- Respect `prefers-reduced-motion`.

**Non-Goals:**
- Redesigning the banner layout or adding new content sections.
- A/B testing infrastructure.
- Backend changes (the 401 fix is a client-side auth guard).

## Decisions

### D1: Frosted glass surface instead of flat background

Use `backdrop-filter: blur(12px)` with `oklch(18% 0.04 275deg / 85%)` (surface-base at 85% opacity) for a frosted glass effect that feels integrated with the dark theme.

**Why not a solid color?** The banner sits above scrollable content. A frosted glass effect maintains visual depth and looks polished without being jarring. Solid opaque backgrounds feel disconnected from the dark UI.

**Why not `--color-surface-raised`?** Surface-raised (`oklch(24% 0.03 275deg)`) is fully opaque and used for cards/sheets. The banner is a transient overlay element — frosted glass communicates this distinction.

### D2: Brand gradient top border as visual anchor

Replace the current `1px solid oklch(100% 0 0deg / 10%)` top border with a 2px gradient using `--color-brand-primary` → `--color-brand-secondary`. This creates a strong color accent that draws the eye without overwhelming the layout.

### D3: CTA glow pulse animation

Apply a CSS `@keyframes` animation on the `.signup-banner-btn` using `box-shadow` with `--color-brand-primary` at varying opacity. Cycle: 2.5s, ease-in-out, infinite. This creates a breathing glow effect.

```
@keyframes cta-glow {
  0%, 100% { box-shadow: 0 0 8px oklch(from var(--color-brand-primary) l c h / 30%); }
  50%      { box-shadow: 0 0 18px oklch(from var(--color-brand-primary) l c h / 55%); }
}
```

**Why box-shadow over scale/transform?** Box-shadow changes don't trigger layout recalculation. Scale transforms on buttons can shift adjacent elements and feel unintentional at small magnitudes.

### D4: Slide-in entrance via CSS animation

Use `translateY(100%)` → `translateY(0)` with `opacity: 0` → `opacity: 1`, 400ms ease-out. Defined as a `@keyframes banner-enter` animation applied on the `:scope` element.

### D5: prefers-reduced-motion

Wrap both `cta-glow` and `banner-enter` in `@media (prefers-reduced-motion: no-preference)`. Users with reduced motion preference see the banner without animation (instant appearance, no glow).

### D6: Auth guard pattern for fetchJourneyMap

Follow the established pattern from `FollowServiceClient.listFollowed()`: check `this.authService.isAuthenticated` before the RPC call, return `new Map()` for unauthenticated users. Inject `IAuthService` into `DashboardService` constructor.

### D7: My Artists banner display logic

Add the same pattern from `DashboardRoute.loading()` to `MyArtistsRoute.loading()`:
```typescript
if (!this.authService.isAuthenticated && this.onboarding.isCompleted) {
    this.showSignupBanner = true
}
```

This runs unconditionally in `loading()`, regardless of the notification dialog flow. The existing `onDialogDismissed()` path still works as an additional trigger.

## Risks / Trade-offs

- **[Frosted glass browser support]** → `backdrop-filter` is Baseline since 2022-03. All target browsers support it. No fallback needed.
- **[Animation jank on low-end devices]** → Both animations use `box-shadow` and `opacity`/`transform` only — no layout triggers. The 2.5s glow cycle is slow enough to avoid frame pressure.
- **[Banner competing with onboarding coach-mark]** → The banner only appears after onboarding is completed (`onboarding.isCompleted`), so no visual conflict.
