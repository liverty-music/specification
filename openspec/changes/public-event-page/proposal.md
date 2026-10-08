## Why

The pilot with an independent artist (#1074) depends on fans arriving from the artist's social posts and follower notifications. Today an organizer's event has no page of its own:

- Its detail opens only as a sheet on the dashboard, found by searching the fan's followed-artist list.
- A guest, or a fan who does not follow the artist, who opens `/concerts/:id` sees the dashboard and no event.
- A shared link shows no preview card.
- The only way into the lottery screens is a temporary route that carries the price and ticket limit in the URL.

A public, shareable event page is the entry point that ticket sales, referral attribution, check-in and resale all build on.

## What Changes

- **New fan screen `/events/:id`**, one page per Event of a first-party Series:
  - Guests can open it, and it loads without waiting for sign-in.
  - It shows the cover image, title, performers with a follow control, date with doors-open and start times, the venue with a map link and the description.
  - A share control and an add-to-calendar control.
  - A ticket section. Its sale contents come from the follow-up change `first-come-ticket-sales`; this change shows a signed-in fan's purchased tickets for the event.
  - When the Series has several Events (for example a 2-day run), the page shows a date tab per Event, and each tab is its own `/events/:id` URL. Above 4 Events the tabs become an "other dates" list.
  - The page never shows the self-reported ticket journey control.
- **Who can open the page.** This is a separate rule from whether a concert appears in the app's lists:

  | Organizer's Series | Shown in lists | `/events/:id` opens |
  |---|---|---|
  | Published, PUBLIC | yes | yes |
  | Cancelled (was PUBLIC) | no | yes, as cancelled |
  | Draft | no | no ("not found") |
  | UNLISTED | no | no ("not found") |

  Lists keep today's rule. Only the cancelled row differs, so a shared link still explains the cancellation instead of looking broken.
- **Page states:**
  - PUBLISHED and PUBLIC: the normal page.
  - CANCELLED (中止, cancellation): the page stays reachable with a cancellation banner, no sale, a refund notice and a link to the artist's other concerts.
  - Past date: the page stays reachable with an "ended" notice and no ticket section.
  - DRAFT, UNLISTED, an unknown id or a discovered (not first-party) concert: one identical "not found" page.
  - 延期 (postponement) is not supported. The follow-up `remove-event-postponement` removes its unused fields.
- **Sign-up from the event page:**
  - Sign-up is requested only when a guest starts a purchase.
  - After sign-up the fan returns to the same event page, not the dashboard.
  - Onboarding is marked complete, and neither the celebration overlay nor the post-signup dialog is shown. `first-come-ticket-sales` asks for notification permission and app install after the purchase.
- **Link previews:** `/events/:id` HTML carries Open Graph and X card tags built from the event:
  - Japanese, with dates in JST.
  - The canonical URL without query parameters.
  - The cover image, or a branded default image.
  - Site-default tags when the event is not found or the lookup fails.
- **Dashboard:**
  - Tapping a first-party concert card opens `/events/:id` instead of the detail sheet. Returning restores the timetable position.
  - A first-party card shows a "purchased" badge from the fan's tickets instead of the self-reported journey badge.
- **New-concert notification:** a first-party concert's notification links to `/events/<id>` instead of `/concerts/<id>`.
- **Fan API:**
  - New public `ConcertService.Get` returns one Concert by Event id.
  - New public `ConcertService.ListBySeries` returns the Concerts of one Series, for the date tabs.
  - Both return NotFound unless the page can be opened, per the table above.
  - Concerts returned to fans now fill their Series' existing `organizer_id`, description, cover image, visibility and publish state fields, so the app can tell first-party concerts apart.
- **Not shown: the Organizer's name.** For the pilot the artist is its own Organizer. The legally required seller details (名前, 住所, 連絡先 under 特商法) belong to the purchase flow in `first-come-ticket-sales`.

## Capabilities

### New Capabilities

- `components/usecase/concert/get`: returns one Concert whose Series has an event page, or NotFound.
- `components/usecase/concert/list-by-series`: returns the Concerts of a Series that has an event page, or NotFound.
- `components/infrastructure/fan/web/route/event`: the public event page screen, its states, the date tabs, the follow control, purchased tickets and sign-up return.
- `components/infrastructure/fan/web/global/link-preview`: the Open Graph and X card tags served with `/events/:id`, with the site-default fallback.
- `stories/open-a-shared-event-link`: a guest opens a shared event link, sees the event, follows the artist, signs up when buying and lands back on the event.

### Modified Capabilities

- `components/entity/series`: a new rule decides which Series' Events have an event page (the table above): first-party, PUBLIC, and PUBLISHED or CANCELLED. The existing list-visibility rule is unchanged.
- `components/adapter/fan/api/rpc/concert`:
  - Get and ListBySeries need no sign-in, and their requests are validated at the boundary.
  - A returned Concert's Series carries its Organizer id, description, cover image, visibility and publish state.
- `components/infrastructure/fan/web/route/dashboard`:
  - First-party cards open the event page.
  - First-party cards show the purchased badge instead of the journey badge.
- `components/usecase/notification/notify-new-concerts`: the link of a first-party concert is `/events/<id>`.
- `components/infrastructure/fan/web/global/post-signup-dialog`: a sign-up started from the event page shows neither the celebration overlay nor the dialog.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: `/events/:id` highlights the Home tab.

The entity operations Get and ListBySeries rely on already exist and do not change:

- Concert.ListByIDs, which ignores visibility so the usecases apply the event-page rule.
- Series.Get, which returns the first-party attributes and the cover.
- Concert.ListEventsBySeries.

## Impact

- **specification:**
  - `ConcertService.Get` and `ConcertService.ListBySeries` requests and responses.
  - No entity message changes; the fan Series mapping fills existing optional fields.
  - The change is additive and not breaking.
- **backend:**
  - The Get and ListBySeries usecases and handlers.
  - A public HTTP endpoint on fan-api that renders the escaped link-preview tags with a short cache.
  - The fan Series mapping.
  - The new-concert notification link.
- **frontend:**
  - The `event` route with `auth: false`.
  - Dashboard card routing and badges.
  - The bottom-nav section mapping.
  - Sign-up returning to the event page.
  - The Caddyfile `templates` block for `/events/*`.
  - Site-default Open Graph tags in `index.html`.
- **Follow-up changes:**
  - `first-come-ticket-sales` fills the ticket section and runs the purchase.
  - `referral-attribution` reads `?ref=` on this page.
  - `remove-event-postponement` removes the unused postponement fields.
  - Automatic refunds on cancellation stay with #996.
