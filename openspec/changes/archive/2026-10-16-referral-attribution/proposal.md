## Why

The pilot Organizer will hand each person who spreads the event (band members, staff, partner shops) their own link to the event page, and wants to know which link sold how many tickets (specification #1074, "Referral attribution"). Today the event page ignores the query string (frontend `src/routes/event/event-route.ts:79`), and no record ties an Order to the link that brought the fan, so the Organizer console cannot show purchases per link. The pilot sells through this feature, so it has to ship before the first real sale.

## What Changes

- **Free-form referral codes.** A link to an event page can carry `?ref=<code>`. Any code of 1 to 32 letters, digits or hyphens is accepted; the fan app lowercases it, so `Member-A` and `member-a` are one code. Codes are not registered in advance, have no management screen and pay no reward. The code is not an access control and is unrelated to the UNLISTED share token.
- **The fan app keeps the code on the device for 7 days.** The event page stores the code with the Series it was opened for. A newer valid link replaces it (last link wins). The code survives the sign-up round trip and other tabs, and signing out does not remove it. The sign-up return path and the buy and entry links are unchanged: the code is read from the device, not from the address.
- **Analytics never receives the app's own query strings.** Before a usage analytics event leaves the device, the fan app removes the query and fragment from every address on its own origin, so `?ref=` (and any later link value such as an UNLISTED share token) stays on the platform.
- **The code counts only for the same Series.** When a fan starts a checkout or a lottery entry, the app sends the kept code only when the event belongs to the Series the code was kept for. The server checks only the code's format.
- **New entity `Referral`, with the value `ReferralCode`.** A Referral records that one Checkout or one LotteryEntry was started with a code. `CheckoutService.Start` and `LotteryEntryService.Start` take an optional referral code. A malformed code fails with InvalidArgument at the boundary. While the Checkout is Held or the LotteryEntry is a Draft, starting again with another code replaces the code; once the source is confirmed, its Referral never changes. A purchase without a code has no Referral. Existing tables and the Order issuance are unchanged; the purchase is found through the Order's source.
- **The Organizer console shows purchases per code.** The event page's 販売 (Sales) tab gets a section 紹介コード別の購入 (purchases per referral code): for each code, the number of Paid Orders, their tickets and the amount paid 税込 (tax-inclusive), with purchases without a code grouped as 直接 (direct). Refunded Orders are not counted. A lottery entry counts only once its Order exists, that is after it won and was charged. Organizer `TicketSaleService.ListByEvent` returns these counts.
- **The Privacy Policy lists the purchase route** (the referral code of the link the fan came from) among the collected data, together with the purchase records it is recorded with.
- **Storage names without `liverty`.** Every client-side storage name in the frontend (localStorage and sessionStorage keys, IndexedDB databases, Cache Storage names, the notification tag) drops the undefined prefix `liverty`. Legacy-migration keys are deleted instead of renamed. **BREAKING for devices:** the renamed IndexedDB databases start empty, so a fan's device loses the private key of its WalletPublicKey and a venue device loses the private key bound to its Scanner, once (design D9 states what each device does next). There are no real users yet.

## Capabilities

### New Capabilities

- `components/infrastructure/fan/web/global/analytics`: analytics events never carry the query string of the app's own addresses, so `?ref=` (and any future link value) does not reach the analytics service

- `components/entity/referral`: one Checkout's or LotteryEntry's record of the referral code it was started with, and the `ReferralCode` format rule
- `components/entity/referral/record`: stores a source's code, replacing it while the source is not confirmed
- `components/entity/referral/list-stats-by-event`: Paid Orders of one event per referral code, with purchases without a code as direct
- `stories/attribute-a-purchase-to-a-referral-link`: a fan opens a link that carries a referral code, signs up and buys; the Organizer sees the purchase under that code

### Modified Capabilities

- `components/usecase/checkout/start`: takes an optional referral code and records it with Referral.Record
- `components/usecase/lottery-entry/start`: takes an optional referral code and records it with Referral.Record
- `components/adapter/fan/api/rpc/checkout`: Start rejects a malformed referral code
- `components/adapter/fan/api/rpc/lottery-entry`: Start rejects a malformed referral code
- `components/usecase/ticket-sale/list-own-by-event`: also returns the event's purchases per referral code from Referral.ListStatsByEvent
- `components/infrastructure/fan/web/route/event`: keeps a valid `?ref=` code on the device for 7 days with the event's Series
- `components/infrastructure/fan/web/route/checkout`: sends the kept code for the same Series with Start
- `components/infrastructure/fan/web/route/lottery-entry`: sends the kept code for the same Series with Start
- `components/infrastructure/organizer/web/route/event`: the Sales tab shows purchases per referral code
- `components/infrastructure/fan/web/global/legal-document`: the Privacy Policy's collected categories include purchase records and the purchase route
- `components/infrastructure/fan/web/global/post-signup-dialog`, `components/infrastructure/fan/web/global/page-help`, `components/infrastructure/fan/web/global/fab-menu`, `stories/merge-guest-data-on-signup`: the storage keys they name lose the `liverty:` prefix (design D9); behavior is unchanged
- `components/infrastructure/fan/web/route/my-artists` and `stories/merge-guest-data-on-signup`: drop the key `liverty:guest:hypes`, which no code writes any more; a guest's hype is kept in the artist's entry of `guest.followedArtists`, as the story already says
- `components/entity/checkout` (Purpose): the erDiagram gains `Checkout ||--o| Referral`
- `components/entity/lottery-entry` (Purpose): the erDiagram gains `LotteryEntry ||--o| Referral`
- `components/usecase/checkout/start`, `components/usecase/lottery-entry/start`, `components/usecase/ticket-sale/list-own-by-event`, `components/infrastructure/organizer/web/route/event` (Purpose): one clause each naming the referral code

Unchanged, with the reason:
- `components/entity/checkout/get-or-create-held` and `components/entity/lottery-entry/get-or-create-draft`: Start records the Referral after they return, so they do not change.
- `components/entity/order` and the issuance usecases (`order/issue-from-checkout`, `order/issue-due-checkouts`, `order/issue-from-captured-win`, `order/issue-due-wins`): the Order is found through its source, so issuance stores nothing new.
- `components/adapter/organizer/api/rpc/ticket-sale`: the boundary passes the usecase's result through; its checks do not change.
- `components/entity/concert/delete-and-suppress`, `components/entity/organizer/delete`, `components/entity/user/delete`: a Referral exists only with its source (`entity/referral`), so removing a Checkout or LotteryEntry removes its Referral, and a kept source keeps it.

## Impact

- **specification:** a new `entity/v1/referral.proto` (`ReferralCode`); `referral_code = 3` on the fan `CheckoutService.Start` and `LotteryEntryService.Start` requests; `ReferralCodeStats` and `referral_code_stats` on the organizer `TicketSaleService.ListByEvent` response. All additive; one minor release.
- **backend:** an Atlas migration creating `referrals` (no change to `checkouts`, `lottery_entries` or `orders`); a `Referral` entity and `ReferralRepository` (`Record`, `ListStatsByEvent`); `CheckoutUseCase.Start`, `LotteryEntryUseCase.Start` and `TicketSaleUseCase.ListOwnByEvent`; the two fan handlers and the organizer ticket sale handler. The `organizer-console-api` role reads the new table through the existing default privileges; no grant is added (design D6).
- **frontend:** fan event page, checkout and lottery entry routes and a new referral storage adapter; organizer Sales tab; Privacy Policy text (ja and en); the storage-name clean-up across fan, organizer and reception code.
- **cloud-provisioning:** none.
- No PostHog event is added; purchases are counted from server records.
