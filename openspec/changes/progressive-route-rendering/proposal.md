## Why

`defer-dashboard-reentry-render` makes the dashboard timetable render
progressively: an App Shell frame that paints without data, viewport-scoped
rendering, entrance motion on cold load only, and scroll position preserved
across navigation. It also brings every bottom-nav tab under the non-blocking
data contract and adds a CI check that enforces it.

What it deliberately does **not** do is generalise any of that. After it ships:

- **The mechanism is hand-wired in one route.** The dashboard coordinates the two
  Aurelia lifecycles by itself — `attaching()` returning a promise to yield a
  paint, `attached()` reflecting render state, `unloading()` saving scroll. The
  next route that wants the same behavior has to re-derive all of it. That is the
  same fragmentation that let Settings drift out of the non-blocking contract
  while `my-artists` had the pattern documented in a comment three metres away.
- **Most routes still have no loading presentation at all.** Tickets and Order
  render a single line of text while their data is in flight; Discovery renders
  nothing. Only Dashboard and My Artists have a skeleton. A tab switch to Tickets
  shows a bare screen, then a full list — the exact layout-shift-and-wait
  experience the dashboard work removes.
- **Nothing outside the dashboard is viewport-scoped**, and no route other than
  the dashboard restores scroll position.

The CI check added by the previous change enforces the *non-blocking* half of the
contract app-wide. Nothing enforces or shares the *rendering* half.

This change generalises the mechanism now that its real shape is known from a
working implementation, rather than designing the abstraction up front.

## What Changes

**Extract the shared lifecycle mechanism**

- Introduce globally registered router lifecycle hooks, split by concern rather
  than collected into one class — Aurelia supports several registered hooks and a
  single god-hook would hide control flow:
  - a **data hook** that starts a route's declared data non-blocking on `loading`
    and cancels it on `unloading`, so no route writes that wiring again;
  - a **scroll-restoration hook** that saves a route's scroll offset on
    `unloading` (the framework's documented "save state" hook) and restores it
    after the route's content is reflected.
- Routes **declare** what data they need instead of implementing a `loading()`
  hook, so the anti-pattern has no place left to live.
- The optimistic page-identity update stays on the shell's `navigation-start`
  subscription: it must fire earlier than any per-component router hook, so it is
  not a candidate for this consolidation.

**Roll the App Shell treatment out to the remaining routes**

- Give Tickets, Order and Discovery a content-shaped loading presentation and a
  data-independent frame, replacing the bare text line or blank screen.
- Apply viewport-scoped rendering to the remaining long lists where a list can
  exceed a viewport.
- Extend scroll restoration to the other bottom-nav tabs via the shared hook.

Out of scope:

- Re-opening any decision this change inherits — the flatten, the containment
  approach and the yield mechanism are settled by the measurements recorded in
  `defer-dashboard-reentry-render`'s design.
- `@aurelia/ui-virtualization` / `virtual-repeat`.
- Any route that is not reachable from the bottom nav or does not fetch data.

## Capabilities

### New Capabilities

- `route-rendering-lifecycle`: the app-wide contract for how a route coordinates
  Aurelia's two lifecycles when it renders fetched data — where the fetch starts,
  where render state is reflected, where a paint is yielded, and where scroll
  position is saved and restored — expressed so that it holds for every
  data-fetching route rather than being re-derived per route.

### Modified Capabilities

- `non-blocking-menu-navigation`: the contract currently describes what each
  route must do. Once the shared hooks exist, it additionally requires that
  routes satisfy it by declaring their data rather than by implementing the
  wiring themselves, so conformance is structural instead of per-route
  discipline.

## Impact

- **Depends on `defer-dashboard-reentry-render` shipping first.** The hooks are
  extracted from that implementation; starting before it lands means designing
  the abstraction from speculation again.
- **Frontend only**, but broad: a new hooks module, `main.ts` registration, and
  every bottom-nav route's `loading()`/`attached()`/`unloading()` wiring.
  Templates for Tickets, Order and Discovery gain a frame and skeleton.
- **Migration is route-by-route.** The hooks and the declarative data form land
  first and coexist with hand-written `loading()` hooks; routes move over one at
  a time, so no single step rewrites every route at once.
- **The CI check from the previous change becomes the migration tracker** — it
  already fails on the anti-pattern, and can be tightened to require the
  declarative form once every route has moved.
- **Risk**: a global lifecycle hook runs for every routed component, so a defect
  in it is an app-wide defect. Component-lifecycle hooks registered globally
  would apply to *every* custom element, not just routes — the shared behavior
  must therefore sit on router hooks, with element-scoped concerns staying in the
  component that owns them.
- **Verification**: device traces on the reference profile for each migrated tab,
  confirming the frame paints before data and that no route regresses to holding
  the outgoing screen.
