## Why

A ticket sale is modelled three times today: the discovered `SalesPhase` (one sale for a whole Series), the organizer's `LotterySalesPhase` (one lottery for one event) and the first-come `TicketSale` that `first-come-ticket-sales` adds (one sale for one event). They share the method, the window and the result time, but they cannot express a real Japanese tour: one fan-club presale and one general sale, each covering several dates. A second phase on the same event is also accepted silently. The first-come `TicketSale` merged into backend and frontend on 2026-10-10, but no fan has bought through it, and the lottery has no production users. This is the cheapest moment to settle one sale model before the pilot Organizer sells its first presale.

The same review found names that confuse readers, and RPC method names that do not say what the method does. `TicketApplication` sits in `lottery_application.proto`. The same User is called applicant, buyer and holder. "Seller" means the Organizer in one place and the reselling fan in another. A fan's name and phone number are stored up to four times (application, checkout, User, every Ticket). Across the services, `Get` takes another entity's id (`TicketSaleService.Get(event_id)`), `List` hides what it filters on (`ConcertService.List(artist_id)`), methods return another service's resource (`TicketService.GetOrder`), and some requests name the caller (`user_id`) while others do not. All of these are breaking proto changes, so they ship in this change's one breaking release (decided with the user).

## What Changes

- **New `TicketSale`**: one sale opportunity (受付) for some or all events of a Series. It has a name such as "ファンクラブ先行", a method, a window, an identity-verification requirement and a drawn time. It has two methods: `Lottery`, which this change adds, and `FirstCome`, which `first-come-ticket-sales` shipped as a sale for one event and which this change moves onto the new model. Discovered sales move into this entity in a later change.
- **New `TicketType`**: what a sale offers for one event. It has a price (税込, tax-inclusive), a quantity and a per-account limit. A sale has at most one ticket type per event.
- **An event can have several sales.** The windows of two sales that share an event must not overlap. A fan's per-account limit counts the tickets the fan already holds for the event, so a presale winner cannot add a full second allowance in the general sale.
- **BREAKING** `LotterySalesPhase` is removed. Its window, capacity, group size, price, verification requirement and drawn time move to `TicketSale` and `TicketType`.
- **BREAKING** `TicketApplication` is renamed `LotteryEntry`. A fan enters one ticket type. The state `Applied` becomes `Entered`.
- **BREAKING** A lottery entry is made the way a first-come checkout is: the fan starts a Draft entry, authorizes the card hold on it, and confirms it. The hold that `CreateAuthorization` opened with no record behind it now belongs to the entry. A Draft left unconfirmed when the window closes is withdrawn at the draw and its hold released. The usecase methods become `Start`, `Authorize`, `Confirm`, `Withdraw`, `ListByTicketType` and `DrawDueSales`; `GetResult` goes, because the entry's state already says Won or Lost.
- **BREAKING** A fan's full name and phone number are stored only on the `User`. A lottery entry no longer stores them. A Ticket shows the User's current name and phone on its face. The fan can change them at any time.
- **BREAKING** Every reference to the User in a ticketing record is named `user`: Order `buyer`, Ticket `holder` and the applicant become `user`. Order and Ticket operations are renamed to match.
- **BREAKING** The organizer lottery RPCs (`Configure`, `GetStatus`, `SetVerificationRequirement`) are replaced by an organizer ticket sale service. The fan lottery RPCs become `LotteryEntryService` with `Start`, `Authorize`, `Confirm`, `Withdraw` and `ListByTicketType`.
- **BREAKING** RPC method names follow one rule across every service (design D11): every service is named after an entity, `Get` takes the resource's own id, `ListBy<Key>` names a required request field, one-attribute writes are `Set<Attribute>`, a service's standard methods return only its own resource, and a request never names the calling user. Outside ticketing this renames methods of Concert, Artist, Follow, TicketJourney, Settlement, Order, push subscription, User, Notification, Series and the admin Concert and Organizer services, folds `IdentityVerificationService` into `VerifiedIdentityService`, and removes the unused `IssuanceService`.
- **BREAKING** One name per concept in every layer (design D16, D17), shipped in a second release after v0.78.0:
  - Entities get natural English names: `IdentityVerification` (本人確認; v0.78.0 shipped `Kyc`), `PayoutAccount`, `ConcertCandidate`, `RejectedConcert`, `SeriesImage` (the Series cover image, was `Media`) and `ConcertSearch`.
  - The card authorization becomes the entity `CardAuthorization`, which LotteryEntry and Checkout reference; the middle purchase step is `AuthorizeCard`, returning the card authorization secret.
  - IDs that a provider assigns are `provider_<concept>_id` (`provider_payment_id`, `provider_user_id`, `provider_organizer_id`, …); `_ref`, `external_id` and vendor names (`zitadel_org_id`, `pocket_sign_user_id`, `payment_intent_ref`) leave the domain.
  - Usecases, Go and TS names, time-field stems, and the lottery `ticket_count` match the spec and proto; unused fields and methods are removed.
- The organizer console's lottery editor creates a lottery `TicketSale` for one event.
- **BREAKING** The first-come sale that `first-come-ticket-sales` shipped moves onto the new model without new behavior:
  - Each existing first-come sale becomes one `FirstCome` `TicketSale` named "一般発売" with one `TicketType`.
  - The sold count, the held count, the sale state, LowStock and the price lock move from the sale to its `TicketType`, because they count one event's stock.
  - The organizer `Configure`/`Get` RPCs become `Create`, `ListByEvent` and `SetWindow` on the organizer ticket sale service and `Update` on a new organizer ticket type service. A Lottery sale can be changed until its window opens; a `FirstCome` sale keeps its shipped edit rules. The fan `TicketSaleService.Get(event_id)` becomes `ListByEvent`.
  - `Reservation` becomes `Checkout`.
  - The holder name and phone leave `Checkout` and `User`, in favour of the User's full name and phone number.
  - The Organizer's seller details become plain Organizer fields (legal name, representative name, business address, business phone number, contact email). The word "seller" leaves code identifiers.

## Capabilities

### New Capabilities

- `components/entity/ticket-sale`: the sale opportunity (受付), its window, method, verification requirement and drawn state
- `components/entity/ticket-sale/create`: stores a sale together with its ticket types
- `components/entity/ticket-sale/get`: reads one sale with its ticket types
- `components/entity/ticket-sale/list-by-event`: lists the sales that offer a ticket type for one event
- `components/entity/ticket-sale/list-due-for-draw`: lists the lottery sales whose window has closed and that are not drawn
- `components/entity/ticket-sale/set-verification-requirement`: changes a sale's verification requirement
- `components/entity/ticket-type`: what a sale offers for one event: price, quantity and per-account limit
- `components/entity/ticket-type/get`: reads one ticket type with its sale
- `components/entity/lottery-entry`: one fan's entry into a lottery ticket type
- `components/entity/lottery-entry/get-or-create-draft`, `set-authorization`, `get`, `list-by-ticket-type-and-user`, `list-undrawn-for-ticket-type`, `get-ticket-type-stats`, `run-lottery-draw`, `persist-draw-outcome`, `update-state`, `create-authorization`, `verify-authorization`, `capture-authorization`, `cancel-authorization`: the operations of `TicketApplication`, renamed and keyed by ticket type, plus the Draft operations
- `components/entity/order/get-by-lottery-entry-id`, `components/entity/order/list-lottery-entry-ids-awaiting-issuance`, `components/entity/order/list-by-user`: the renamed Order operations
- `components/entity/ticket/list-by-user`, `components/entity/ticket/list-by-user-and-event`: the renamed Ticket operations
- `components/entity/user/update-personal-details`: stores a User's full name and phone number
- `components/usecase/ticket-sale/create`: an Organizer creates a lottery sale for its published events
- `components/usecase/ticket-sale/list-own-by-event`: an Organizer reads the sales of one event with their tallies
- `components/usecase/ticket-sale/set-verification-requirement`: an Organizer changes a sale's verification requirement
- `components/usecase/lottery-entry/start`, `authorize-card`, `confirm`, `draw-due-sales`, `run-draw`, `list-by-ticket-type`, `withdraw`: the lottery usecase methods, keyed by ticket type
- `components/adapter/organizer/api/rpc/ticket-sale`: the organizer ticket sale service boundary
- `components/adapter/fan/api/rpc/lottery-entry`: the fan lottery entry service boundary
- `components/entity/ticket-sale/{list-by-event,set-window}`, `components/entity/ticket-type/update`, `components/usecase/ticket-sale/{list-by-event,set-window}`, `components/usecase/ticket-type/update`, `components/adapter/organizer/api/rpc/ticket-type`: the sale and ticket type edits (design D11)
- `components/entity/checkout` and its operations, `components/usecase/checkout/*`, `components/adapter/fan/api/rpc/checkout`, `components/entity/order/get-by-checkout-id`, `components/usecase/order/{issue-from-checkout,issue-due-checkouts}`, `components/entity/lottery-entry/get-by-payment-intent-ref`: the renamed first-come checkout (design D7)
- `components/entity/organizer/set-business-details`, `components/usecase/organizer/set-business-details`: the renamed seller details operations

### Modified Capabilities

- `components/entity/order` (Purpose): `buyer` becomes `user`, `application` becomes `lottery entry`
- `components/entity/ticket` (Purpose and requirement): `holder` becomes `user`, the holder full name and phone attributes leave, and the covered-ticket face reads the User's name and phone
- `components/entity/user` (Purpose and requirement): gains full name and phone number with their validation
- `components/usecase/order/issue-from-captured-win`: issues from a won lottery entry and its ticket type, binds tickets to the user, and copies no name or phone
- `components/usecase/order/issue-due-wins`: lists won lottery entries without an Order
- `components/usecase/order/get` (moved from `get-order`): the caller is the Order's user
- `components/usecase/ticket/list` (moved from `get-my-tickets`): lists by user
- `components/adapter/fan/api/rpc/lottery`: REMOVED; the boundary moves to the new `components/adapter/fan/api/rpc/lottery-entry` (`LotteryEntryService` with Start, Authorize, Confirm, Withdraw and ListByTicketType), and the identity rule is the User's
- `components/infrastructure/fan/web/route/lottery-entry` (moved from `lottery-apply`): the screen enters a ticket type and prefills the fan's saved name and phone
- `components/infrastructure/organizer/web/route/lottery-sale-editor` (moved from `lottery-phase-editor`): the editor creates a named lottery sale for one event
- `stories/win-tickets-in-a-lottery`: the story runs on a lottery ticket sale
- `components/entity/concert/delete-and-suppress`, `components/entity/organizer/delete`, `components/entity/user/delete`: the deleted or kept records are named TicketSale, TicketType and LotteryEntry, and a deleted User takes its full name and phone number with it
- `components/usecase/user/delete`: reads `Ticket.ListByUser` and `Order.ListByUser`

### Removed Capabilities

These are written as REMOVED deltas:
- `components/entity/lottery-sales-phase` and its operations `create`, `get`, `list-phases-due-for-draw` and `update-verification-requirement`
- `components/usecase/lottery-sales-phase/*`
- `components/entity/ticket-application` and its 12 operations
- `components/usecase/ticket-application/*`
- `components/entity/order/get-by-application-id`, `components/entity/order/list-application-ids-awaiting-issuance`, `components/entity/order/list-by-buyer`
- `components/entity/ticket/list-by-holder`
- `components/adapter/organizer/api/rpc/lottery`

### Capabilities of `first-come-ticket-sales`

`first-come-ticket-sales` adds these specs when it archives, before this change syncs (design D13). The deltas below are rewritten then (task 1.2):
- `components/entity/ticket-sale`, `ticket-sale/create`, `ticket-sale/get` and `components/adapter/organizer/api/rpc/ticket-sale`: this change's ADDED blocks become MODIFIED and REMOVED blocks on them, and the first-come rules (sold count, held count, sale state, LowStock, price lock) move to `components/entity/ticket-type`.
- `components/entity/user`: the holder identity requirement is replaced by the personal details requirement.
- Modified: `ticket-sale/get-by-event` (becomes `list-by-event`), `ticket-sale/update`, `usecase/ticket-sale/{configure,get,get-own}`, `usecase/order/{issue-from-reservation,issue-due-reservations,fulfill-payment}`, `usecase/order/issue-from-captured-win` (the Paid-journey requirement that `first-come-ticket-sales` removes), `entity/organizer`, `entity/order` (the Reservation source), `adapter/fan/api/rpc/ticket-sale`, `adapter/fan/api/rpc/user`, `adapter/admin/api/rpc/organizer`, `adapter/fan/api/webhook/payment-events`, and the routes `fan/web/route/event`, `fan/web/route/checkout` and `organizer/web/route/ticket-sale-editor`.
- Replaced (REMOVED at the old path, ADDED at the new one, design D12): `entity/reservation/*` and `usecase/reservation/*` → `checkout/*`; `adapter/fan/api/rpc/reservation` → `rpc/checkout`; `entity/ticket-application/get-by-payment-intent-ref` → `entity/lottery-entry/get-by-payment-intent-ref`; `entity/order/get-by-reservation-id` → `get-by-checkout-id`; `entity/organizer/set-seller-details` and `usecase/organizer/update-seller-details` → operations named after the Organizer fields.
- Removed: `entity/user/update-holder-identity`, replaced by `user/update-personal-details`.

### Capabilities added or moved by one name per concept (design D16, D17)

- New: `components/entity/card-authorization` with `create`, `get`, `capture` and `release`; `components/adapter/organizer/api/rpc/series-image`; fan `global/{i18n,bottom-sheet,user-home-selector}` MODIFIED for renamed RPCs.
- Removed: `components/entity/order/get-captured-payment` (CardAuthorization.Get replaces it), `components/usecase/concert/list-by-follower` (unused), `components/usecase/organizer/list-own-artists` (ArtistUseCase.ListByOrganizer serves both callers); this change's own `*-authorization` operations of LotteryEntry and Checkout.
- Moved directly on the main specs as pure renames (no change, schema rule), each with a mapping table in its commit: the six entity renames of D17 with their operations and usecases; usecases renamed after their RPCs (`follow/list`, `ticket-journey/list`, `notification/dismiss`, `user/set-home`, `user/set-preferred-language`, `concert/list-followed`, `ticket/list`, `order/get`, `order/refund`, `artist/list-by-organizer`, `series/{create,update,list,regenerate-share-url,set-cover-image}`, `concert-candidate/{list,approve,reject}`, `official-site/create`, `payout-account/get`); the routes `lottery-entry` and `lottery-sale-editor`; the provider ID operations.

### Capabilities renamed by the RPC naming rule

These adapter and route specs are MODIFIED to the new method names (task 1.4); their behavior does not change, except that a request no longer names the calling user:
- `components/adapter/fan/api/rpc/{concert,artist,follow,ticket,ticket-journey,user,notification,push-notification}`
- `components/adapter/admin/api/rpc/{concert,organizer,artist,user,order}`
- `components/adapter/organizer/api/rpc/organizer`
- the routes and surfaces that name them: `fan/web/route/{discovery,dashboard,settings}`, `fan/web/global/{post-signup-dialog,app-shell,live-highway}`, `admin/web/route/approval-queue`
- new boundaries, one per service: `adapter/fan/api/rpc/{official-site,order,push-subscription}`, `adapter/admin/api/rpc/{notification,concert-candidate}`, `adapter/organizer/api/rpc/artist`; the moved requirements are REMOVED from the old boundary
- `usecase/user/{resolve-caller,resend-email-verification}`: the request no longer names a User id (design D15)

`ReceptionLinkService.List` is renamed in `rename-reception-to-scanner` (`ScannerService.ListByEvent`), which renames the service.

Entity operations that this change relies on and does not change: `Event.IsEventPublished`, `Event.Get`, `Event.GetOrganizerID`, `Event.GetEventStartTime`, `Series.GetAuthored`, `VerifiedIdentity.GetByUserID` (renamed `IdentityVerification.GetByUserID`), `Order.GetCapturedPayment` (replaced by `CardAuthorization.Capture`, D17), `Order.Issue`, `TicketJourney.Upsert`, `User.GetByExternalID` (renamed `GetByProviderUserID`, D17), `OrganizerUseCase.ResolveCaller`. `restructure-event-publishing` later makes `Event.IsEventPublished` answer per Event instead of per Series. The rule here, that a sale needs a published event, holds under both answers.

## Impact

- **specification**:
  - Entity protos: `ticket_sale.proto` (rewritten), new `ticket_type.proto`, `lottery_entry.proto` (from `lottery_application.proto`), `checkout.proto` (from `reservation.proto`), `user.proto`, `order.proto`, `ticket.proto`, `organizer.proto` (seller details flattened, also inside the Organizer embedded in `series.proto`).
  - RPC protos for the naming rule: `rpc/concert/v1`, `rpc/artist/v1`, `rpc/follow/v1`, `rpc/ticket/v1` (`GetOrder` → new `rpc/order/v1`), `rpc/ticket_journey/v1`, `rpc/user/v1`, `rpc/notification/v1`, `rpc/push_notification/v1`, `rpc/identity/v1` (into `rpc/verified_identity/v1`), `rpc/issuance/v1` (removed), `rpc/admin/{concert,organizer,settlement,order,notification}/v1`, `rpc/organizer/v1`, `rpc/organizer/series/v1`, new `rpc/organizer/ticket_type/v1`.
  - RPC protos: `rpc/organizer/ticket_sale/v1` (rewritten), `rpc/organizer/lottery/v1` (removed), `rpc/lottery/v1` (fan, replaced), `rpc/reservation/v1` (replaced by `rpc/checkout/v1`), `rpc/ticket_sale/v1` (fan), `rpc/admin/organizer/v1` (`UpdateSellerDetails`).
  - The D16 and D17 renames: entity protos and their RPC packages, in a second breaking release (task 11.2).
  - These are breaking changes on BSR. No client outside this product consumes them.
- **backend**:
  - Migration:
    - `lottery_sales_phases` and the existing first-come `ticket_sales` → `ticket_sales` + `ticket_types`;
    - `ticket_applications` → `lottery_entries`; `reservations` → `checkouts`;
    - `users.holder_*` → `users.full_name` / `phone_number`, and `applicant_*` / `tickets.holder_*` dropped after their values move to `users`;
    - `orders.buyer_id`, `application_id`, `reservation_id` and `tickets.holder_id` renamed;
    - `organizers.seller_*` renamed;
    - the column grants of `organizer-console-api` on `ticket_sales` redone.
  - Lottery, first-come sale, checkout, draw and issuance code.
  - Organizer, fan and admin handlers, including the renamed methods and the removed `user_id` checks (`RequireUserIDMatch`).
- **frontend**:
  - Fan lottery entry screen (route params, prefill), checkout route and event page ticket section.
  - Organizer lottery editor, lottery status screen and first-come ticket sale editor.
  - Admin Organizer screen (seller details form) and every client of a renamed method. The client-side cache of the internal user id that `standardize-user-scoped-rpc-auth` added goes if nothing else reads it (task 9.4 checks).
  - Generated clients.
- **Other in-flight changes** (design D13):
  - `first-come-ticket-sales` finishes and archives first, as shipped.
  - `identity-ekyc-jpki` moves its lottery deltas onto the new specs.
  - `split-concert-from-event` rewrites this change's artifacts to its new names (its task 11.1), including the "performers" of an Event in the delete deltas.
  - `official-resale` renames `ResaleListing.seller` to `user`.
  - `rename-reception-to-scanner`, `redesign-organizer-console`, `restructure-event-publishing` and `migrate-discovered-sales` build on this change.
- **Production data**: only test data exists. The lottery has no production users (`CLAUDE.md`, current operating state). Row counts are checked read-only before the migration.
