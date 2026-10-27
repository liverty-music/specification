## Why

A LotteryEntry is created as a Draft at Start, before the fan has authorized their card, and that early row is the source of most of the lottery's rules: the Draft state, the withdrawal, the replacement of a Draft with another count, the release of Drafts at the draw, and the Referral that changes while its source is open. The replacement also breaks payments: a card authorization opened for a Draft is keyed by the entry's id, so a count change either leaves the first card authorization held (today) or collides at the payment provider (the in-place change that `remove-lottery-entry-withdrawal` planned, found in its Stripe sandbox test). The product decision is that an entry exists only once the fan confirms it: the fan authorizes their card for a ticket count, confirms, and only then is the entry made, Entered. A card authorization becomes an entry, or is released, as soon as the fan completes card authentication; the payment provider's notice of that moment makes it happen even when the fan's browser never calls Confirm.

This change replaces `remove-lottery-entry-withdrawal`, whose proto step (v0.98.0, liverty-music/specification#1262: `LotteryEntryService.Withdraw` removed, `LOTTERY_ENTRY_STATE_WITHDRAWN` reserved) has shipped and stays.

## What Changes

- **BREAKING** A LotteryEntry is created at Confirm, Entered, with its card authorization. Its states are Entered, Won and Lost. Draft and Withdrawn are gone, and a fan cannot withdraw an entry.
- **BREAKING** `LotteryEntryService.Start` is removed. `AuthorizeCard` takes the TicketType, the ticket count, the 本人確認 details and the referral code, stores nothing, and returns the card authorization's id with its secret. `Confirm` takes the card authorization and returns the new entry. To change the count, the fan authorizes again; an authorization whose card authentication was never completed holds nothing.
- A CardAuthorization knows what it pays for: the fan, the TicketType, the ticket count and the referral code, and whether it is for a Checkout or a lottery entry.
- `LotteryEntryUseCase.Confirm` also runs when the payment provider reports that a lottery card authorization is Authorized, so an authorization whose fan closed the browser after card authentication still becomes an entry. A rejected Authorized authorization (another fan's, wrong amount, American Express, a second entry, after the end time) is released at once.
- Only an entry made before the sale's end time counts, and the draw starts 1 minute after the end time.
- **BREAKING** (organizer data only) The Referral entity is folded into a `referral code` attribute of Checkout and LotteryEntry. A Checkout's code is set at Start and replaced by a later Start while Held; a LotteryEntry's code is set when it is created. The Organizer's purchases per referral code are unchanged.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/create`: stores a new Entered entry; one per account and TicketType; only before the sale's end time.
- `components/entity/checkout/set-referral-code`: sets the referral code of a Held Checkout.
- `components/entity/order/list-referral-stats-by-event`: the Paid Orders of an event per referral code (moved from Referral).

### Modified Capabilities

- `components/entity/lottery-entry` (Purpose): states Entered, Won, Lost; card authorization required; referral code added; relations without Referral. "A new entry starts as a Draft" becomes "A new entry starts Entered"; the Draft-only requirements are removed.
- `components/entity/card-authorization` (Purpose): purchase, user, ticket type, ticket count and referral code added; relations.
- `components/entity/card-authorization/create`: takes the purchase, and for a lottery entry its fan, TicketType, count and referral code; repeating it returns the same card authorization for a Checkout only.
- `components/entity/card-authorization/get`: returns the purchase, user, ticket type, ticket count and referral code.
- `components/entity/checkout` (Purpose): referral code added; relations without Referral.
- `components/entity/referral` (Purpose): only the ReferralCode value remains; the source, the create time and their rules are removed.
- `components/entity/referral/record`, `components/entity/referral/list-stats-by-event`: removed (replaced by `checkout/set-referral-code`, `lottery-entry/create` and `order/list-referral-stats-by-event`).
- `components/entity/lottery-entry/get-or-create-draft`, `set-card-authorization`, `update-state`: removed.
- `components/entity/lottery-entry/get`: returns an entry in any state (no Withdrawn).
- `components/entity/lottery-entry/list-by-ticket-type-and-user`: at most one entry.
- `components/entity/lottery-entry/list-undrawn-for-ticket-type`: Entered entries only.
- `components/entity/lottery-entry/get-stats-by-ticket-type`: every entry counts.
- `components/entity/lottery-entry/persist-draw-outcome`: no Drafts.
- `components/entity/order/list-lottery-entry-ids-awaiting-issuance`: "not won" names Entered and Lost.
- `components/entity/ticket-sale/list-due-for-draw`: due 1 minute after the end time.
- `components/entity/concert/delete-and-suppress`: the Draft case of a purchase in progress is removed.
- `components/entity/organizer/delete`: the same Draft case is removed.
- `components/usecase/order/issue-from-captured-win`: the "entry not won" scenario names Entered and Lost.
- `components/usecase/lottery-entry/start`, `withdraw`: removed.
- `components/usecase/lottery-entry/authorize-card`: takes the TicketType, count and referral code; the checks of Start move here; stores nothing.
- `components/usecase/lottery-entry/confirm`: creates the entry from the card authorization, or releases it; also run by the payment provider's notice.
- `components/usecase/lottery-entry/run-draw`: no Drafts.
- `components/usecase/checkout/start`: records the code with `Checkout.SetReferralCode`.
- `components/usecase/ticket-sale/list-own-by-event`: reads `Order.ListReferralStatsByEvent`.
- `components/adapter/fan/api/rpc/lottery-entry`: the calls and their boundary checks.
- `components/adapter/fan/api/rpc/checkout`: a malformed referral code sets no code (no Referral).
- `components/adapter/fan/api/webhook/payment-events`: a notice that a card authorization is Authorized runs `LotteryEntryUseCase.Confirm`.
- `components/infrastructure/fan/web/route/lottery-entry`: AuthorizeCard and Confirm only; the kept code goes with AuthorizeCard; a refused entry is explained.
- `stories/win-tickets-in-a-lottery` (Purpose): the usecase diagram without Start and Withdraw. The withdrawal requirement is replaced by the count change and the browser closed after card authentication; the timing follows the draw's start.
- `stories/attribute-a-purchase-to-a-referral-link`: a lottery entry carries the code it was authorized with.

Unchanged and why: `card-authorization/capture` and `release` already succeed again for a repeated call; `lottery-entry/get-by-card-authorization-id` and `run-lottery-draw` keep their promises; `usecase/lottery-entry/list-by-ticket-type` and `draw-due-sales` keep theirs (the latter only reads `ListDueForDraw`); `checkout/get-or-create-held` keeps its; `order/issue` reads the entry, not its Referral; `card-authorization/release` already serves the immediate release.

## Impact

- **specification**: proto `rpc/lottery_entry/v1` (Start removed; AuthorizeCard and Confirm requests and responses), `entity/v1/lottery_entry.proto` (DRAFT reserved, card_authorization_id required), `entity/v1/referral.proto` (comment). No RPC returns a referral code, so none is added to the proto messages. Breaking; `buf skip breaking`. The `rpc-design` skill's multi-step purchase rule.
- **backend**: lottery entry entity, repository and usecase; CardAuthorization metadata; Checkout referral code; Order referral stats; the webhook's new notice; an Atlas migration (Draft rows deleted, referrals moved into two columns and dropped, constraints).
- **cloud-provisioning**: the payment provider webhook endpoint subscribes to the card-authentication-completed notice.
- **frontend**: the lottery entry screen (no Start; the count and the kept code go with AuthorizeCard), the status screen without Draft, the generated package.
- **Follow-ups**: `make-lottery-draw-durable` builds on the 1-minute draw start and on entries that are always Entered.
