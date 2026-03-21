## Context

The discover page currently uses a `<dialog popover="auto">` element with custom CSS to display a one-time onboarding guide. This component has poor visibility — the translucent gradient blends into the bubble canvas. Meanwhile, the app already has a mature `<snack-bar>` notification system with consistent styling, auto-dismiss, and fire-and-forget API via `IEventAggregator`.

The snack-bar is used elsewhere (e.g., unfollow undo notifications in my-artists) and provides a well-tested, accessible notification pattern that users will already be familiar with by the time they reach other parts of the app.

## Goals / Non-Goals

**Goals:**
- Replace the custom onboarding popover with a snack-bar notification for visual consistency
- Simplify `discovery-route` by removing ~50 lines of CSS, template markup, and ref/lifecycle logic
- Maintain the same user experience: a brief instructional message shown once on discover entry during onboarding

**Non-Goals:**
- Modifying the snack-bar component itself (the existing API is sufficient)
- Changing the onboarding flow progression (spotlight coach marks, step tracking)
- Adding new snack-bar features (e.g., light-dismiss mode)

## Decisions

### 1. Use snack-bar (EventAggregator) instead of toast primitive

**Decision**: Publish a `Snack` event in `attached()` rather than using the `<toast>` CE directly.

**Why**: The `<toast>` CE is a low-level popover wrapper — using it would require reimplementing timer-based dismiss logic that snack-bar already provides. The onboarding guide is semantically a notification ("here's what to do"), which maps directly to snack-bar's purpose.

**Alternative considered**: Using `<toast>` directly with manual timeout — rejected because it recreates snack-bar logic and diverges visually.

### 2. Auto-dismiss with extended duration (5000 ms)

**Decision**: Set `duration: 5000` on the Snack event instead of relying on light-dismiss.

**Why**: The default 2500 ms is too short for first-time users to read the guide message. 5000 ms provides ample reading time. Auto-dismiss is preferable to light-dismiss because it removes the cognitive overhead of "dismiss this before interacting with bubbles" — users can start exploring immediately.

### 3. Use `info` severity

**Decision**: Use `severity: 'info'` for the onboarding snack.

**Why**: The guide is informational, not a warning or error. The `info` severity provides the brand gradient styling (purple → blue) which aligns with the app's visual identity.

### 4. No action button on the snack

**Decision**: The onboarding snack has no action button — it is a passive, informational message.

**Why**: The guide is a one-way notification. There is no meaningful action to take on the snack itself; the user's next action is to interact with the bubble canvas directly.

## Risks / Trade-offs

**[Position change: bottom → top]** → The snack-bar renders at the top of the viewport, while the current popover sits at the bottom center. This changes the visual flow but places the guide in a more conventional notification position that users expect. Acceptable trade-off for consistency.

**[No light-dismiss]** → Users cannot tap to explicitly dismiss the snack. Mitigated by the 5000 ms auto-dismiss; the snack disappears before it becomes an obstacle. If needed in the future, a dismiss action could be added via `options.action`.

**[No backdrop overlay]** → The current popover has a backdrop that dims the background, drawing attention. The snack-bar has no backdrop. Mitigated by the snack-bar's solid gradient background and top-positioned entry animation which naturally draws the eye.
