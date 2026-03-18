## Context

The welcome page (`/`) is the first screen unauthenticated users see. It currently uses a single boolean getter `showGetStarted` (derived from `onboarding.isCompleted`) to toggle between two mutually exclusive button states. The onboarding step is persisted in localStorage and restored on page load via the `@aurelia/state` middleware.

The `canLoad()` guard already handles authenticated users (redirect to dashboard) and mid-onboarding users (redirect to current step). The welcome page only renders for unauthenticated users who are either brand new or have completed onboarding but logged out.

## Goals / Non-Goals

**Goals:**
- Always present both "Get Started" and "Log In" on the welcome page so any user can take the correct action regardless of localStorage state
- Fix the accessibility gap on the secondary CTA (missing `href`/`tabindex` on `<a>`)
- Consolidate `onboarding.complete()` to a single call site in `guest-data-merge-service.ts`
- Preserve guest artist data when re-entering onboarding via "Get Started"

**Non-Goals:**
- Redesigning the welcome page layout or visual hierarchy beyond the CTA area
- Adding server-side onboarding state (no backend changes)
- Changing the onboarding step progression or route guard logic
- Modifying the OAuth/Zitadel integration

## Decisions

### 1. Both CTAs as `<button>` elements with primary/secondary styling

Replace the current `if.bind` toggle and `<a>` link with two always-visible `<button>` elements.

- "Get Started" uses the existing `.welcome-btn-primary` style (brand color fill)
- "Log In" uses a new `.welcome-btn-secondary` style (outline/ghost variant)

**Why not keep `<a>` for login?** The login action calls `authService.signIn()` which triggers a programmatic redirect — it's not a navigation link. `<button>` is semantically correct and resolves the a11y issue without needing `href="#"` hacks or `role="link"`.

**Why not a single button that changes label?** Users should always see both options. A returning user on a new device needs "Log In" visible without depending on localStorage. A user who completed onboarding but abandoned OAuth needs "Get Started" to retry.

### 2. Remove `showGetStarted` getter entirely

The getter and its `if.bind` bindings are the sole source of conditional rendering. With both CTAs always visible, this getter has no remaining consumers. Delete it to keep the ViewModel clean.

### 3. Remove `guest/clearAll` from `handleGetStarted()`

Currently `handleGetStarted()` dispatches both `guest/clearAll` and `onboarding/reset`. The `guest/clearAll` wipes followed artists — destructive if the user already went through discovery on a previous attempt. Keep only `onboarding/reset` so the user re-enters onboarding at the discovery step with their previous artist selections intact.

**Trade-off:** If stale guest data causes issues (e.g., artists that no longer exist), the discovery page already handles missing data gracefully via its error boundary. The benefit of preserving data outweighs this edge case.

### 4. Consolidate `onboarding.complete()` in merge service only

Remove the call at `auth-callback-route.ts:43-45`. The `guest-data-merge-service.ts:51` call already executes unconditionally at the end of `merge()`, which runs immediately after. Having two call sites is confusing and the first one (`auth-callback-route`) fires before merge completes, which breaks the semantic that "completed = all guest data has been merged."

### 5. Secondary button styling approach

Use a ghost/outline variant that pairs with the primary button:
- Transparent background with a subtle border
- Same dimensions as primary (`min-block-size: 48px`, full width)
- Brand color text, hover fills lightly

This maintains visual hierarchy (primary = Get Started, secondary = Log In) while keeping both equally accessible as tap targets.

## Risks / Trade-offs

- **Two prominent CTAs may increase decision fatigue** → Mitigated by clear visual hierarchy (filled primary vs outline secondary) and distinct labels. The current design already shows two CTAs for new users (button + link); this change just makes both consistently visible.
- **Preserving stale guest data on re-enter** → Low risk. Discovery page renders from store state and handles missing artist images/data. Worst case: user sees previously followed artists pre-selected in the bubble UI, which is actually helpful context.
- **localStorage cleared = always shows both CTAs** → This is now the intended behavior, not a bug. Both paths are always available regardless of persisted state.
