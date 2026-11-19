## Why

A fan web screen or shared part had a different name in each layer: the home screen was `/dashboard` in the URL, `DashboardRoute` in code, `nav.home` in i18n, "Timetable" on screen, and its grid was `live-highway` in the spec and `<concert-highway>` in code. The first-party concert page lived at `/events/:id` and the timetable's sheet at `/concerts/:id`, although both show a Concert. The main specs now carry one name per screen and part (renamed in the commit before this change); this change brings the URLs and the code to the same names, so a name found in one layer finds the same thing in every other.

## What Changes

- **One naming rule.** A screen's spec name (`route/<name>`) is its file, class (`<Name>Route`), custom element, i18n namespace (camelCase) and, for screens that are not a resource, its URL. A shared part's spec name (`global/<name>`) is its component folder, class, element and i18n namespace. A part with no spec of its own (a card inside a grid) is named for what it shows.
- **One URL rule.** A screen that shows or creates a resource uses the plural resource noun: a list at `/<resources>`, one item at `/<resources>/:id`, a creation form at `/<resources>/new`, nested at most one level under its parent; inputs to a form and the state of a list (a filter, an open sheet) go in the query string. Words are lowercase and joined by hyphens.
- **BREAKING (URL):** the fan web's addresses change, and the old ones are not redirected (the product has no users yet):

  | before | after |
  |---|---|
  | `/dashboard` | `/timetable` |
  | `/concerts/:id` (the timetable's sheet) | `/timetable?concert=:id` |
  | `/events/:id` (the first-party concert page) | `/concerts/:id` |
  | `/events/:id/checkout/:stockId` | `/concerts/:id/checkout?stock=:stockId` |
  | `/events/:id/lottery/:saleId/:stockId` | `/concerts/:id/lottery-entries/new?sale=:saleId&stock=:stockId` |
  | `/events/:id/lottery/:saleId/:stockId/entry` | `/concerts/:id/lottery-entries?sale=:saleId` |
  | `/events/:id/resale/:stockId` | `/concerts/:id/resale-entries/new?stock=:stockId` |
  | `/passkey-recovery` | `/sign-in-help` |
  | `/discovery?view=nearby` | `/discovery?view=concerts` |

- **Links the backend builds follow.** A Notification's link, the link preview's page match and the passkey-change email's link use the new addresses.
- **One English title per screen.** The page header and the browser tab show the same title, in English in every language (the bottom navigation labels already are). Labels that name a screen use the same words: Discovery's two views are the Artists view and the Concerts view, and the swap tile reads 「ライブ」 / "Concerts" (was 「近くのライブ」 / "Near you"), since the Concerts view lists concerts in any area the fan picks, not only near them. Checkout, lottery and resale screens take titles built from their names (Checkout, Lottery Entry, Lottery Entries, Resale Entry, Resale Entries), and Tickets is "Tickets" in the header as in the tab bar.
- **Every fan route spec states its address**, so the frontend can keep the list of spec names and addresses as one constant, and a unit test fails when the route table drifts from it.
- **Analytics values follow the names.** The `source` values sent to the analytics service (`dashboard`, `discovery_orb`, `all_nearby`, `dashboard_prompt`, `all_nearby_prompt`, `event_page`) take the new names (design D5); continuity with events already recorded is not kept.
- Not changed: the callback addresses registered with the identity and verification providers (`/auth/callback`, `/auth/passkeys-callback`, `/verify/callback`), `/tickets`, `/orders/:id`, `/resale-entries`, `/notifications`, `/settings/**`, `/my-artists`, `/discovery`, `/legal/*`, `/verify-email`, and the admin, organizer and reception apps.

## Capabilities

### New Capabilities

None. (`route/resale-entries` was split out of the resale entry spec in the rename commit before this change.)

### Modified Capabilities

- `components/infrastructure/fan/web/route/timetable`: its address is `/timetable`; the sheet's address is `/timetable?concert=:id`; a first-party concert opens `/concerts/:id`.
- `components/infrastructure/fan/web/route/concert`: its address is `/concerts/:id` (Purpose edited directly).
- `components/infrastructure/fan/web/route/checkout`, `route/new-lottery-entry`, `route/new-resale-entry`: their new addresses.
- `components/infrastructure/fan/web/route/welcome`, `route/my-artists`, `route/tickets`, `route/settings`, `route/delete-account`, `route/resale-entries`, `route/verify-email`: their address, stated for the first time (unchanged).
- `components/infrastructure/fan/web/route/discovery`: the Concerts view's address is `view=concerts`, the swap tile's name, and a first-party concert card opens `/concerts/:id`.
- `components/infrastructure/fan/web/route/sign-in-help`, `route/welcome`, `route/settings`: the sign-in help address is `/sign-in-help`.
- `components/infrastructure/fan/web/global/page-header`: each screen has one English title, shown in the header and the browser tab.
- `components/infrastructure/fan/web/global/page-help`: Discovery's help names the Concerts view.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: the Timetable tab's path.
- `components/infrastructure/fan/web/global/link-preview`: concert page addresses carry the concert's preview.
- `components/infrastructure/fan/web/global/analytics`: the error report's exception names the timetable's address.
- `components/infrastructure/fan/web/global/post-signup-dialog`: the timetable's address after sign-up.
- `components/entity/notification`: the link of each type uses the new addresses.
- `components/usecase/notification/notify-new-concerts`: the message links to the new addresses. The operations it relies on are unchanged.
- `stories/open-a-shared-event-link`, `stories/attribute-a-purchase-to-a-referral-link`, `stories/roam-app-as-guest`: the addresses they open.

## Impact

- **frontend**: file, folder, class, element and i18n renames across the fan web (approximately 265 files); the route table; the analytics source values; a new constant of route spec names and addresses with a unit test; `@spec` paths and scenario names in tests.
- **backend**: `Notification` link building, the link preview's route and `og:url`, and the passkey-change email's link; `@spec` scenario names in tests whose scenarios were renamed.
- **specification**: none beyond this change (the main specs were renamed in the commit before it).
- **Analytics**: insights that filter on the old `source` values need the new values.
- No proto, database or infrastructure change.
