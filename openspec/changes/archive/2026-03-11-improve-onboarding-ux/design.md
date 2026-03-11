## Context

The onboarding tutorial (Steps 0-7) guides new users through artist discovery, dashboard interaction, hype customization, and signup. The current implementation suffers from:

1. **Coach marks too small and easily missed** — overlay is only 60% opacity, tooltips are small (12px padding, 280px max-width), no pulse or attention-grabbing animation, scrolling is not locked so users scroll past them.
2. **Dashboard layout doesn't match festival timetable aesthetic** — "Live Highway" header with tiny (10px) labels, uneven 50:30:20 lane ratios, artist names overflow with line breaks, hype uses emoji badges that overlap text.
3. **Missing transition moments** — no celebration when dashboard is generated, Step 1 CTA is a plain button instead of guided nav-bar interaction, no lane explanation before first card interaction.
4. **Step 4 broken** — event-detail-sheet uses `<dialog>.showModal()` which promotes to top layer above the coach mark `popover`, making the My Artists guidance invisible.
5. **Nav bar hidden during most of onboarding** — users don't learn about navigation until Step 3.

All changes are frontend-only. No proto or backend modifications required.

## Goals / Non-Goals

**Goals:**
- Make coach marks impossible to miss (darker overlay, larger tooltips, pulse animation, scroll lock)
- Redesign dashboard header as festival-style sticky STAGE lanes (HOME / NEAR / AWAY)
- Replace hype emoji badges with border gradient + glow + neon text-shadow system
- Fix Step 4 coach mark visibility by converting event-detail-sheet to popover
- Add celebration overlay between discovery and dashboard
- Add sequential lane introduction before first card spotlight
- Change Step 1 CTA from button to nav-bar Dashboard icon spotlight
- Gate CTA on concert data readiness (3 artists with data), with progress bar
- Show nav bar on all pages except Welcome

**Non-Goals:**
- Changing the onboarding step count or adding new steps (sub-steps within Step 3 are visual only, not persisted)
- Backend API changes or new RPC endpoints
- Changing hype level tiers or persistence logic
- Redesigning the artist discovery bubble UI
- Changing the signup modal (Step 6) flow

## Decisions

### D1: Coach Mark Visual Overhaul

**Decision:** Increase overlay darkness to 75%, enlarge tooltips, add spotlight pulse ring, lock scroll during coach marks.

**Rationale:** The current 60% overlay with small tooltips blends into the dark theme. Festival apps and game tutorials use high-contrast overlays (70-80%) with animated spotlight rings to force attention. Scroll lock prevents users from accidentally scrolling past the guided element.

**Implementation:**
- Overlay: `oklch(0% 0 0deg / 75%)` (was 60%)
- Spotlight: Add `2px solid` ring in `--color-brand-accent` with `@keyframes coach-pulse` (scale 1→1.05→1, 1.5s infinite)
- Tooltip: `font-size: 16px`, `padding: 16px`, `background: var(--color-brand-accent)`, `color: white`, `border-radius: 12px`
- Scroll lock: When coach mark is active, add `overflow: hidden` to `<au-viewport>` (the scroll container per app-shell-layout spec)
- `prefers-reduced-motion: reduce` → disable pulse animation, keep static ring
- `detaching()` lifecycle hook must call `hide()` (not just `cleanup()`) to release scroll lock, clear anchor-name, and cancel retry timer — navigating away while a coach mark is active would otherwise leave `overflow: hidden` permanently on `<au-viewport>`

<!-- Why detaching() calls hide() instead of individual cleanups:
     hide() is the single method that reverses ALL side effects of highlight():
     anchor-name on target, overflow on au-viewport, and retry timer.
     Calling cleanup() alone only handles the timer, leaving scroll lock
     and anchor-name leaked. This was identified as a bug in code review. -->

**Alternative considered:** Using a full-screen modal dialog for each coach step. Rejected because it would break the spatial relationship between the spotlight and the target element.

### D2: Event Detail Sheet — `<dialog popover="manual">`

**Decision:** Convert `event-detail-sheet` from `<dialog>.showModal()` to `<dialog popover="manual">` with `showPopover()` / `hidePopover()`.

<!-- Why <dialog popover> and not <div popover>:
     MDN: "<dialog popover> is perfectly valid if you want to combine popover
     control with dialog semantics." This gives native <dialog> accessibility
     (screen readers understand it without role="dialog") while gaining popover
     top-layer LIFO ordering for coach mark stacking.

     Why ::backdrop works with popover="manual":
     MDN: "Backdrops appear for Popover API elements that have been shown in
     the top layer via HTMLElement.showPopover()." This applies to BOTH
     popover="auto" AND popover="manual". No sibling backdrop div is needed.

     Why manual Escape + detaching() are required:
     popover="manual" does not support light dismiss (neither Escape nor
     outside click). Escape handling must be added via a document-level
     keydown listener. This listener MUST be removed in detaching() because
     navigating away while the sheet is open skips close(), leaking the
     listener and preventing garbage collection of the component instance. -->

**Rationale:** `showModal()` promotes the dialog to the top layer with highest stacking priority, covering the coach mark popover. `<dialog popover="manual">` combines native dialog semantics with popover LIFO ordering: detail sheet shown first, coach mark shown after = coach mark on top. Unlike `<div popover>`, `<dialog>` provides native accessibility without requiring `role="dialog"`.

**Implementation:**
- Replace `<dialog>` with `<dialog popover="manual" tabindex="-1">` in event-detail-sheet.html
- Replace `showModal()` / `close()` with `showPopover()` / `hidePopover()`
- Use native `::backdrop` pseudo-element for the dimmed/blurred overlay — no sibling backdrop div
- Remove `cancel.trigger` (not applicable to popovers)
- Add manual Escape key handling via `document.addEventListener('keydown', ...)` with an arrow function instance method to preserve `this` binding
- Add `detaching()` lifecycle hook to remove the keydown listener unconditionally
- Add focus management: `open()` calls `this.sheetElement.focus()`, `close()` restores focus to the element that triggered the sheet
- Retain `history.pushState` / `popstate` URL management
- Retain swipe-to-dismiss gesture handling
- During onboarding Step 4: dismiss is blocked, coach mark targets `[data-nav-my-artists]`

**Alternative considered:** Re-promoting coach mark via `hidePopover()→showPopover()` after dialog opens. Rejected as fragile hack that depends on top-layer insertion order.

**Alternative considered:** `<div popover="manual" role="dialog">`. Rejected — `<dialog>` provides native semantics without manual ARIA, and MDN explicitly endorses the `<dialog popover>` combination.

### D3: Dashboard Lane Layout — Festival Timetable Style

**Decision:** Equal 33:33:33 lane ratio with sticky STAGE headers (HOME STAGE / NEAR STAGE / AWAY STAGE), dynamic font sizing via container queries.

**Rationale:** The 50:30:20 ratio was designed for a "mega-typography main lane" concept, but it leaves the away lane too narrow for readable content. Equal widths with consistent card styling better matches the festival timetable aesthetic. Sticky headers provide persistent context as users scroll through date groups.

**Implementation:**
- Grid: `grid-template-columns: 1fr 1fr 1fr` (was `50% 30% 20%`)
- Sticky header: `position: sticky; top: 0` with opaque background, above date group headers
- Header text: Bold, uppercase, 14-16px (was 10px). Remove "Live Highway" title entirely.
- Lane names: HOME STAGE / NEAR STAGE / AWAY STAGE
- Proto field mapping unchanged: `home` → HOME STAGE, `nearby` → NEAR STAGE, `away` → AWAY STAGE
- Font sizing: CSS `container-type: inline-size` on each lane cell, artist name uses `clamp(12px, 5cqi, 24px)` with `overflow-wrap: break-word`
- Card height: `min-height` based on content, no fixed height. Line breaks are allowed, card expands.

### D4: Hype Visualization — Border + Glow + Neon Text

**Decision:** Replace emoji badges with a 4-tier visual system using border gradient, box-shadow glow, and text-shadow neon effect. No extra DOM space consumed. Artist color is delivered to CSS via an Aurelia custom attribute, enforcing strict TS/HTML/CSS responsibility separation.

**Rationale:** Emoji badges (🔥🔥) overlap artist names in narrow lanes and feel inconsistent with the dark festival aesthetic. Border/glow/neon effects are zero-space, CSS-only, and scale naturally with card size.

**Tiers:**

| Level | Border | Glow (box-shadow) | Text Shadow | Animation |
|-------|--------|-------------------|-------------|-----------|
| WATCH (Keep an Eye) | `1px solid white/10` | none | none | none |
| HOME (Local Only) | `1px solid ${artistColor}/40` | `0 0 8px ${artistColor}/30` | `0 0 4px ${artistColor}/30` | none |
| NEARBY | `2px solid ${artistColor}` | `0 0 16px ${artistColor}/50` | `0 0 8px ${artistColor}/60` | gentle pulse (2s) |
| AWAY (Must Go) | `2px solid` gradient border | `0 0 24px ${artistColor}/60, 0 0 48px ${artistColor}/20` | `0 0 12px ${artistColor}, 0 0 24px ${artistColor}/40` | strong pulse (1.5s) + gradient rotation |

- Gradient border for AWAY uses `@property` animated `conic-gradient`
- `prefers-reduced-motion: reduce` → static styles only (no pulse, no gradient rotation)
- Remove all emoji badge elements and `HYPE_META` icon references from event cards

**Artist color delivery — `artist-color` custom attribute:**

<!-- Why a custom attribute instead of inline style or value converter:
     Responsibility separation: TS = business logic, HTML = structure, CSS = style.
     The artist name → color mapping requires a string hash (JS-only), but HOW
     that color is applied (background, border, glow) is purely CSS's job.
     A custom attribute encapsulates the JS→CSS bridge:
     - HTML declares intent: artist-color.bind="event.artistName"
     - The attribute computes the hue and sets --artist-hue on the element
     - CSS constructs all colors: hsl(var(--artist-hue), 65%, 60%)
     - The CSS custom property name is hidden from the template

     A value converter was considered but rejected: it would require the
     template to know about --artist-hue (style="--artist-hue: ${name | hue}"),
     leaking CSS implementation details into HTML.

     Inline style from TS (the prior approach) was rejected: cardStyle getter
     set background-color directly, which is a styling decision that belongs
     in CSS. This caused a bug where background-color covered the .hype-away
     gradient border. -->

- New Aurelia 2 custom attribute `artist-color` (`src/custom-attributes/artist-color.ts`)
- Input: artist name string. Computes deterministic hue via `color-generator.ts` hash
- Sets `--artist-hue` CSS custom property on the host element
- Cleans up in `detaching()` by removing the property
- CSS constructs the full color: `--artist-color: hsl(var(--artist-hue), 65%, 60%)`
- `background-color` is set per-tier in CSS (not in TS), avoiding the gradient border conflict:
  - `.hype-watch`, `.hype-home`, `.hype-nearby`: `background-color: var(--artist-color)`
  - `.hype-away`: no `background-color` — the first `background-image` layer fills the interior
- Hype class applied directly in HTML template: `class="... hype-${event.hypeLevel}"`
- Reusable across components (event-card, event-detail-sheet)

### D5: Onboarding Step 1 CTA — Nav Bar Dashboard Spotlight

**Decision:** Replace the "Generate Dashboard" button with a coach mark spotlight on the nav-bar Dashboard icon. Gate on concert data readiness for all 3 followed artists.

**Rationale:** Using the nav-bar icon teaches users about navigation while transitioning them to the dashboard. Gating on concert data prevents showing an empty timetable.

**Implementation:**
- When `followedCount >= 3`: begin tracking concert search completion per artist
- Progress bar shows concert search status (continuous fill, not numeric)
- When all 3+ followed artists have concert search results: activate coach mark targeting `[data-nav-dashboard]` (new data attribute on nav-bar dashboard link)
- Coach mark message: "タイムテーブルを見てみよう！"
- On tap: `onboarding.setStep(DASHBOARD)`, router navigates to `/dashboard`
- Nav bar must be visible during Step 1 (see D7)

**Concert data readiness tracking:**
- `DiscoverPage` already fires `SearchNewConcerts` on each follow via fire-and-forget
- Add an observable map `concertSearchStatus: Map<artistId, 'pending' | 'done'>` to track completion
- On follow: set status to `pending`, listen for search completion callback
- Progress bar width: `completedCount / followedCount * 100%` (only counts artists with followedCount >= 3)
- Timeout: 15s per artist (matching existing SearchNewConcerts timeout), treat timeout as `done` to prevent blocking

### D6: Celebration Overlay

**Decision:** Show a full-screen celebration overlay for 2-3 seconds after dashboard icon tap, before dashboard content appears. Displayed exactly once per SPA session.

**Implementation:**
- New component `<celebration-overlay>` rendered in dashboard route
- Triggers when `onboarding.currentStep === DASHBOARD` and dashboard data is loading
- Content: "あなただけのタイムテーブルが完成しました！" centered text with confetti particle CSS animation
- Duration: 2.5s, then fade out (400ms)
- After fade: dashboard content revealed, lane introduction begins
- `prefers-reduced-motion: reduce` → skip confetti animation, show text only for 1.5s
- One-time guard: `Dashboard` uses a `private static celebrationShown = false` flag to prevent re-triggering on subsequent navigations to the dashboard route during the same session

<!-- Why static flag instead of sessionStorage or service-level flag:
     Aurelia route components are re-created on each navigation, resetting
     instance state. A static class property persists across instances for
     the lifetime of the JS module (= SPA session). This is the simplest
     solution: no storage API, no service interface change, no serialization.
     Page reload during onboarding would re-show the 2.5s animation, which
     is acceptable — the user is resuming a tutorial and the celebration
     reinforces the transition moment. -->

### D7: Nav Bar Visibility During Onboarding

**Decision:** Show nav bar on all pages except Welcome (landing page). Rely on existing route guards for navigation restriction.

**Rationale:** Route guards (`AuthHook.canLoad()`) already prevent step-skipping by redirecting to the correct step route. Showing the nav bar early lets users become familiar with the navigation structure before they gain full access.

**Implementation:**
- Current `showNav` condition in `my-app.ts`: hidden for landing, discover, loading, auth-callback
- Change to: hidden only for landing page and auth-callback
- No additional click prevention needed — `AuthHook` redirects unauthorized route access
- If URL flicker from redirect is noticeable, add `event.preventDefault()` in nav-bar `<a>` click handler during onboarding (deferred, only if needed)

### D8: Dashboard Lane Introduction Sequence (Step 3 Sub-Steps)

**Decision:** Before spotlighting the first card, sequentially spotlight each STAGE header with a brief explanation. These are visual sub-steps, not persisted in `onboardingStep`.

**Implementation:**
- After celebration overlay fades and region selection completes, dashboard enters "lane intro" mode
- Sequence: HOME STAGE header → NEAR STAGE header → AWAY STAGE header → first card
- Each header spotlight: coach mark with explanation text, auto-advance after 2s or on tap
- Messages:
  - HOME STAGE: "地元のライブ情報！"
  - NEAR STAGE: "近くのエリアのライブも！"
  - AWAY STAGE: "全国のライブ情報もチェック！"
- After all 3 headers: scroll lock, spotlight first card with existing Step 3 coach mark
- Lane intro state managed locally in dashboard component (not in onboarding service)

### D9: Step 4 Guidance Message Update

**Decision:** Change Step 4 coach mark message from "Customize notifications from the artist screen" to "アーティスト一覧も見てみよう！"

**Rationale:** The original message was too functional ("customize notifications"). A lighter, curiosity-driven message reduces cognitive load and feels more natural in the tutorial flow.

## Risks / Trade-offs

**[Concert data gate may delay CTA]** → Mitigated by 15s timeout per artist and treating timeout as `done`. Users continue following artists while searches complete, reducing perceived wait. Progress bar provides visual feedback.

**[Equal lane widths reduce main lane prominence]** → Trade-off accepted. The festival timetable aesthetic benefits from visual balance. Card typography and hype glow effects provide sufficient differentiation for important events.

**[`<dialog popover>` requires manual focus and Escape handling]** → `showPopover()` does not provide focus trapping or Escape dismiss (unlike `showModal()`). Both must be implemented manually. Focus is moved to the dialog on open and restored to the trigger on close. Escape keydown listener is added/removed in `open()`/`close()` and unconditionally cleaned up in `detaching()`.

**[Lane intro adds 6+ seconds to first dashboard experience]** → Each sub-step auto-advances after 2s or can be tapped through immediately. Users who are eager can tap through all 3 in under 3 seconds. The educational value outweighs the delay.

**[Gradient border animation for AWAY hype]** → CSS `@property` for animated gradient is Baseline 2024 but may have edge cases. Fallback: static gradient border without rotation for browsers that don't support `@property`.
