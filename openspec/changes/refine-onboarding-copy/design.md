## Context

This change is the second major copy-and-microUX pass over the onboarding surface since the dashboard preview / coach mark / home selector flows were introduced. The earlier passes (see archived changes covering `welcome-dashboard-preview`, `onboarding-tutorial`, `onboarding-popover-guide`, `user-home`) established the structural flow; this change focuses on language and small affordance bugs that surfaced during informal user observation:

- "推し" is fan-culture jargon that signals a narrower audience than the product targets. The team has aligned on using neutral, entity-grounded vocabulary ("アーティスト" + "フォローする") for the broad consumer surface.
- The Discovery snack "近日開催予定" makes a temporal claim ("imminent") that is not actually verified — the snack fires when *any* concerts are discovered, regardless of date proximity.
- The Step 1 → Step 3 coach mark on Discovery currently auto-dismisses after 2 seconds (`COACH_MARK_FADE_MS = 2000`). Field observation: users do not read and act in 2 seconds; the spotlight disappears before they understand it.
- The home selector's Step 2 (prefecture) header renders an icon-only `<button>` with a 2rem circular background and an SVG chevron at `--color-text-secondary`. Users perceive the circle but not the chevron, leading them to ask "what is this dot?" — i.e., the back affordance is invisible as a back affordance.
- The concert detail sheet (`event-detail-sheet.html`) ships hardcoded English strings ("Open / Start", "Open in Google Maps", "Ticket Status", "Stop tracking", "View Official Info", "Add to Calendar") and renders `JourneyStatus` enum values (`'tracking' | 'applied' | 'lost' | 'unpaid' | 'paid'`) verbatim via `${s}`. Japanese users see English in an otherwise Japanese UI.

Stakeholders: product/design (vocabulary, copy), frontend (implementation), QA (Playwright selectors that may need updates).

## Goals / Non-Goals

**Goals:**

- Replace "推し" everywhere in active onboarding copy with the "アーティスト" / "フォローする" pair, and codify this in `brand-vocabulary` so it cannot drift back silently.
- Make the Discovery snack copy semantically accurate ("found upcoming concerts" — not "imminent").
- Change the Discovery coach mark from time-based dismissal to tap-based dismissal.
- Rephrase the home selector description for accuracy (`居住エリア` is asked, not assumed).
- Make the prefecture-step back button recognizable as a back affordance — visible text label plus the existing chevron.
- Localize the concert detail sheet, including journey-status enum surface forms, into JA and EN under a new `eventDetail.*` namespace.

**Non-Goals:**

- Redesigning the coach mark visual style, the dashboard lane introduction sequence, or the home-selector layout structure.
- Restructuring the i18n architecture (still i18next + `@aurelia/i18n`, still ja/en, still file-per-locale).
- Adding new locales beyond JA/EN.
- Touching protobuf entities, RPC contracts, or backend behavior.
- Migrating `JourneyStatus` from a string-literal union to a proto-generated enum (out of scope; the rendering fix at the i18n layer is sufficient).
- Removing the brief 2-second window in *other* coach marks that may also use timers — this change targets only the Discovery → Dashboard coach mark identified in `onboarding-tutorial` Step 1.

## Decisions

### D1. Retire "推し" as a Layer B brand expression rather than treating it as ad-hoc copy

**Decision**: Register the policy in `brand-vocabulary` (Layer B registry) so that the lint script can enforce it long-term, instead of just rewriting current strings and hoping nobody re-introduces "推し" later.

**Alternative considered**: Bulk-edit translation.json only. Rejected because the term is short, evocative, and likely to creep back into copy proposals; making it a registry-level decision means future PRs explicitly need to discuss it.

**Rationale**: `brand-vocabulary` already exists exactly for managing this kind of cross-cutting term policy. Using it as designed is cheaper than inventing a side-channel rule.

### D2. JA replacement strategy — verb-noun pair, not a single token

**Decision**: Use the pair (noun `アーティスト`, verb `フォローする`) rather than a single token, and apply per-context:

| Context | JA |
|---|---|
| Primary CTA button | `アーティストをフォローする` |
| Preview hint | `アーティストをフォローすると、…` |
| Signup title | `好きなアーティストのライブを逃さなくなる` |
| Popover guide | `フォローしたアーティストのライブが…` |
| Progress subtitle | `もっとアーティストをフォローすると…` |

**Alternative considered**: A single noun "好きなアーティスト" everywhere. Rejected — it reads as awkward filler in CTA buttons ("好きなアーティストを選んでみる" repeats the same idea twice). Splitting verb vs noun usage keeps each touchpoint natural-sounding.

### D3. Coach mark dismissal — delete the timer entirely, do not just extend it

**Decision**: Remove `COACH_MARK_FADE_MS`, the `coachMarkFadeTimer` field, the `setTimeout` block, and the corresponding cleanup in `detaching()`. The spotlight stays visible until the user taps the highlighted Dashboard icon, which already triggers `onCoachMarkTap()` → `deactivateSpotlight()` + navigation.

**Alternative considered**: Extend the timer to 4 seconds (the user's first suggestion during exploration). Rejected because the underlying problem is "users don't have a deterministic moment to act"; 4 seconds is still arbitrary and can still feel rushed for users reading slowly. Tap-only is the natural model for an instructional spotlight that must be acted on.

**Risk**: A user who reads the coach mark, dismisses it via browser back / nav tab tap rather than the highlighted icon, could in principle see the spotlight persist. Mitigation: existing `Route Detach Spotlight Cleanup` requirement in `onboarding-spotlight` already calls `deactivateSpotlight()` from `detaching()`, so any route change clears it. No new cleanup path is required.

### D4. Home-selector back button — visible label "地方一覧" + existing chevron, NOT a wholesale layout rewrite

**Decision**: Keep the existing `selector-header-row` flex layout and the chevron SVG. Add visible text inside the button (e.g., `<span>地方一覧</span>` next to the SVG) and update CSS so the button is `inline-size: auto` (pill-shaped) instead of a 2rem square. Introduce a new i18n key `userHome.backToRegions` for the label.

**Alternative considered**:
- (a) Replace the button entirely with a text-only "← 地方を選び直す" link. Rejected — losing the chevron icon weakens the universal "back" semantics across locales.
- (b) Keep the icon-only design but increase contrast / size. Rejected — even at higher contrast, an unlabeled icon-button next to a heading reads as decoration, especially on first encounter.

**Rationale**: Icon + short text is the standard mobile pattern (matches iOS/Android nav-back conventions and the rest of the app's bottom-sheet back affordances).

### D5. `eventDetail.*` namespace scope — translate the surface only, do not refactor the type model

**Decision**: Create a new top-level i18n namespace `eventDetail.*` with subkeys for every literal string currently embedded in `event-detail-sheet.html`. Add a sub-namespace `eventDetail.journeyStatus.{tracking|applied|lost|unpaid|paid}` for the journey-status enum surface forms, and look it up at the rendering site via `${'eventDetail.journeyStatus.' + s | t}` or equivalent binding.

| Key | JA | EN |
|---|---|---|
| `eventDetail.ariaLabel` | ライブ詳細 | Event details |
| `eventDetail.openStart` | 開場 {{open}} / 開演 {{start}} | Open {{open}} / Start {{start}} |
| `eventDetail.openStartFallback` | — | — |
| `eventDetail.openInGoogleMaps` | Google Maps で開く | Open in Google Maps |
| `eventDetail.ticketStatus` | チケット状況 | Ticket Status |
| `eventDetail.stopTracking` | 追跡を停止 | Stop tracking |
| `eventDetail.viewOfficialInfo` | 公式情報を見る | View Official Info |
| `eventDetail.addToCalendar` | カレンダーに追加 | Add to Calendar |
| `eventDetail.journeyStatus.tracking` | 検討中 | Tracking |
| `eventDetail.journeyStatus.applied` | 申込済み | Applied |
| `eventDetail.journeyStatus.lost` | 落選 | Lost |
| `eventDetail.journeyStatus.unpaid` | 当選・未入金 | Unpaid |
| `eventDetail.journeyStatus.paid` | 入金済み | Paid |

**Alternative considered**: Promote `JourneyStatus` to a proto-generated enum and surface translations via the existing `entity.*` namespace per `brand-vocabulary` Layer A. Rejected for this change — it requires a proto change, BSR gen, and backend updates, none of which are needed for the copy fix. Can be revisited as a follow-up if/when the entity model is formalized.

**Rationale**: The string-literal union `JourneyStatus` is private to the frontend right now. Treating its labels as Layer B brand expressions (frontend-managed surface forms) is consistent with `brand-vocabulary`'s current shape until a proto entity exists.

### D6. Discovery snack copy — change at the i18n key level, no spec scenario rewording

**Decision**: Update only the value behind the existing key `discovery.hasUpcomingEvents`. The `discover` spec's snack scenario says "the page SHALL show a snack notification" without prescribing exact wording, so no spec delta is needed for this scenario.

**Rationale**: Minimal blast radius; preserves the existing call site and i18n key shape (`{{name}}` interpolation).

## Risks / Trade-offs

- **[Risk]** Playwright E2E tests that assert specific Japanese copy (e.g., "推しを選んでみる" button text) will fail after the change. **Mitigation**: Audit `frontend/tests` and any `*.spec.ts` for hardcoded JA strings affected by this change; update them in the same PR as part of `make check`.
- **[Risk]** The `brand-vocabulary` lint script may not currently scan for arbitrary banned terms; only known `entity.*` parity. If it does not enforce "推し" absence, the registry update is documentation-only until the linter is extended. **Mitigation**: Capture this as an Open Question; the registry entry still provides a single source of truth even if enforcement is manual for now.
- **[Risk]** Removing the auto-dismiss timer means a user who context-switches away (e.g., tab-switches the browser, gets a phone notification) and returns may see the spotlight still active. **Mitigation**: This is actually the desired behavior — the spotlight is *guidance*, not *progress indication*, and persisting through inattention is correct.
- **[Trade-off]** The `eventDetail.journeyStatus.*` JA translations are best-effort interpretations of the enum semantics (`tracking` = 検討中, `applied` = 申込済み, etc.). Product may want to refine these — they are reviewable copy, not technical constants.
- **[Trade-off]** The back-button label "地方一覧" is more verbose than the previous icon-only button. On very narrow viewports (<360px) it could push the region heading slightly. Mitigation: the button uses `inline-size: auto` so the heading naturally wraps if needed; no overflow is expected at standard mobile widths.

## Migration Plan

This is a pure frontend copy / behavior tweak with no data, schema, or contract changes.

1. Merge frontend changes; `make check` (lint + tests) must pass.
2. Deploy via existing CI/ArgoCD path. No coordinated backend release needed.
3. Rollback: revert the frontend commit. No data is written; no state needs cleanup.

## Open Questions

- Does the existing `brand-vocabulary` lint script support flagging an absolute banned term ("推し" anywhere in `translation.json`), or does it only check `entity.*` parity? If the former is not yet supported, do we extend the linter in this change or file a follow-up?
- Are the proposed JA translations for `JourneyStatus` (`tracking → 検討中`, `applied → 申込済み`, `lost → 落選`, `unpaid → 当選・未入金`, `paid → 入金済み`) acceptable to product, or should `tracking` map to a different verb (e.g., 追跡中 vs 検討中)?
- Should the popover-guide string `discovery.popoverGuide` retain its em-dash structure ("気になるアーティストをタップ — フォローしたアーティストのライブが…") or be rewritten more naturally as two sentences? (Defaulting to "preserve structure" for this change.)
