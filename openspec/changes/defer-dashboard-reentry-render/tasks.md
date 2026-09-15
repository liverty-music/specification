## 1. Baseline

- [ ] 1.1 Record a reference-profile (Pixel 8 / 4× CPU) Performance trace of a signed-in dashboard tab-switch re-entry with a populated timetable; capture INP and confirm the current single-paint behavior (no early shell paint before the timetable render block). This is the before-baseline.

## 2. Implement — defer the cache fast-path render past first paint

- [ ] 2.1 In `frontend/src/routes/dashboard/dashboard-route.ts`, keep `loading() → void this.loadData()` as-is (do NOT relocate the trigger — `loadData()` is the single entry point for both the cache fast-path and the cold fetch, so moving it would also delay the cold-path fetch, out of scope). Inside `loadData()`, wrap ONLY the cache fast-path's synchronous `this.dateGroups = cachedDateGroups` (+ its `timetableLoaded` flip) in `queueAsyncTask(() => { … })` (from `aurelia`) so that render lands on the frame AFTER the shell's first paint. A macrotask hop (queueAsyncTask) or double-rAF is required — a single `requestAnimationFrame` runs before that frame's paint and would still coalesce. The cold path is untouched.
- [ ] 2.2 Cover the one-frame gap with the loading skeleton, never the empty state. Gate the empty-state placeholder on a "load has settled" condition (not `dateGroups.length === 0 && !isLoading`) so a pending cached paint shows the skeleton.
- [ ] 2.3 Do NOT overload `isLoading` for the fast-path skeleton — it also guards `refreshInBackground()`. Use a dedicated `pendingCachePaint` latch (or sequence the refresh after clearing it) so the background refresh still fires on re-entry.
- [ ] 2.4 Flip `timetableLoaded` inside the deferred task after `dateGroups` is assigned, keeping the celebration / onboarding-completion latch and deep-link resolution ordering unchanged. Cancel the queued task in `detaching()` / on a new load so a stale cached paint never writes into a torn-down or re-navigated route (mirror the `abortController` discipline).

## 3. Tests

- [ ] 3.1 Unit-test (`dashboard-route.spec.ts`) that on the cache fast-path the empty state never renders while a cached paint is pending (skeleton shown), the background refresh still fires, and `timetableLoaded` still flips (celebration/latch + deep-link paths intact).
- [ ] 3.2 `make lint` + `make test` in `frontend/`.

## 4. Verification (device-only) & acceptance

- [ ] 4.1 On the reference profile, signed in with a populated timetable, re-enter via the nav tab and record a trace. Confirm: (a) the header `<h1>` + active nav tab paint BEFORE the timetable render block; (b) no empty-state flash (skeleton only); (c) INP substantially below the 1.1 baseline and the shell interactive while the timetable fills; (d) background refresh swaps fresh data, the celebration fires once when due, and a `/concerts/:id` deep-link still opens the sheet.
- [ ] 4.2 If the post-skeleton timetable render is still a multi-second task on the reference profile, note the residual and route it to the deferred P4 (virtualization / group→lane→card flatten) — do not fold virtualization into this change.

## 5. Close-out

- [ ] 5.1 Sync the `dashboard-timetable-rendering` delta into the main specs (`openspec sync`) before archiving.
- [ ] 5.2 Record before/after re-entry INP + the "shell paints before render" evidence in the PR description.
