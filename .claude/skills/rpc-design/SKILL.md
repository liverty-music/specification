---
name: rpc-design
description: Naming rules for RPC services, methods and request messages in this repository's proto (rpc/**/v1) and adapter specs. Use when adding, renaming or reviewing a service or an rpc, choosing between Get/List/ListBy/Set/Update or a custom verb, deciding which service a method belongs to, or writing an adapter spec that names RPCs. Where it differs from the user-scope protobuf skill (Google AIP-132/136), this skill wins.
---

# RPC design rules (liverty-music)

The goal: a developer predicts a method's input and behavior from its name alone, and every service follows the same rules. These rules override the AIP guidance in the user-scope `protobuf` skill where they differ; everything else in that skill (wrapper messages, protovalidate, comments, field numbering) still applies.

## Services

- A service is named after an entity in `openspec/specs/components/entity/` (`TicketSaleService`, `IdentityVerificationService`). A service with no entity behind it is not created; put its methods on the entity they act on, or remove them.
- A service's standard methods take and return only its own resource. A read of another resource goes to that resource's service (`OrderService.Get`, not `TicketService.GetOrder`).
  - A read may carry related resources as side lists (`ConcertService` responses carry `series` and `artists`).
  - A create may carry child resources created with the parent (`TicketSaleService.Create` with its ticket types).
- Packages name the caller: `rpc.<entity>.v1` is the fan API; `rpc.admin.`, `rpc.organizer.` and `rpc.scanner.` are the admin console, organizer console and venue scanner device. The same method name in two packages narrows by the same Key; the payload may differ.

## Methods

| Form | Use | Example |
|---|---|---|
| `Get(<own id or natural key>)` | read one resource | `CheckoutService.Get(checkout_id)`, `PushSubscriptionService.Get(endpoint)` |
| `Get()` | the one resource the caller has | `OrganizerService.Get()`, `IdentityVerificationService.Get()` |
| `List()` | every resource the caller can see; optional narrowing (state, period) is a field | `TicketService.List()`, `SettlementService.List(status)` |
| `ListBy<Key>` | narrowed by one required request field | `TicketSaleService.ListByEvent(event_id)`, `ConcertService.ListByArtists(artist_ids, home)` |
| `List<Qualifier>` | a computed set no request field selects | `ArtistService.ListTop`, `ListSimilar`, `ConcertService.ListFollowed` |
| `Create`, `Delete` | the resource's own create and delete | `OfficialSiteService.Create` |
| `Update` | the whole resource, or the fields of a field mask | `TicketTypeService.Update` |
| `Set<Attribute>` | one attribute replaced | `UserService.SetHome`, `TicketSaleService.SetVerificationRequirement` |
| domain verb | a state change, a relation made or ended, an idempotent registration, or any other operation | `Publish`, `Withdraw`, `Dismiss`, `Confirm`, `Follow`/`Unfollow`, `AssociateArtist`, `Register`, `Search`, `Start` |

Rules behind the table:

- **Natural key** means a value that identifies the resource outside this system (a browser push endpoint). Another entity's id is not a natural key: `SettlementService.Get(order_id)` is wrong; the Order read carries its Settlement.
- **A Key in a `ListBy` name is always a field in the request.** The caller's relation is never a Key: a list of the concerts of artists the caller follows is `ListFollowed()`, not `ListByFollower()`. Otherwise the same name would take an id on the admin API and nothing on the organizer API.
- Key is an entity (singular for one id, plural for several) or a value object (`ListByLocation`). The singular and the plural are separate methods and may return different shapes (`ListByArtist` a flat list, `ListByArtists` grouped by date and proximity).
- Not used: `Get<Noun>` (`GetStatus`, `GetResult`, `GetOrder`), `Update<Field>` (`UpdateHome`), `List<Resource>` (`ListTickets`), `GetMy*`.
- **The caller is never named.** When the caller owns the resource, neither the method name nor the request names them; the server takes the user from the sign-in (`User.GetByProviderUserID`). No `user_id` on a fan's own request. A request names a user or an Organizer only when an admin acts on another one.
- A multi-step purchase uses the same verbs everywhere: `Start` (create or resume a draft resource), `AuthorizeCard` (open the resource's CardAuthorization, return the `card_authorization_secret`), `Confirm` (finalize). `CheckoutService` and `LotteryEntryService` both follow it. The CardAuthorization is an entity the purchase resource references (`card_authorization_id`); it has no fan service of its own.
- Request fields with the same meaning have the same name across services (`ticket_count` on both `Start` methods).

## Identifiers

- A reference to an entity of this domain is `<entity>_id` (`order_id`, `card_authorization_id`).
- An ID that an outside provider assigns is `provider_<concept>_id`, where the concept is this domain's noun, not the provider's object name: `provider_payment_id` (not `payment_intent_ref`), `provider_user_id` (not `external_id`, `pocket_sign_user_id`), `provider_organizer_id` (not `zitadel_org_id`). The entity spec says which provider assigns it.
- No `_ref` suffix and no vendor names (Stripe, Zitadel, Pocket Sign) in proto, specs or domain code; they stay inside the provider adapters.

## Deviation from Google AIP

AIP-132 narrows a `List` with `parent` plus `filter`, and AIP-136 forbids standard verbs (`List`) in custom methods. `ListBy<Key>` and `List<Qualifier>` break both on purpose: the name then states what it filters on. Rejected: `List(parent)` with typed filter fields, because `List(series_id, event_id?)` does not say what it narrows by. Request and response messages are `<Method>Request` / `<Method>Response` (`ListByEventRequest`), not AIP's `ListBooksRequest`.

## Vocabulary traps

- Bare "identity" means the account at the identity provider (Zitadel). The result of a fan's 本人確認 is the entity `IdentityVerification`; the payment provider's check of an Organizer's account is "payout account verification". "KYC" is only the legal term "AML-KYC".
- The amount reserved on a fan's card is a "card authorization", never bare "authorization" (access control) or "hold" (which names only the Checkout's tickets held for the fan and Settlement's Held status). Stripe's "client secret" is the `card_authorization_secret`.
- "holder", "buyer", "applicant" and "seller" are not entities. A ticketing record's User is `user`; the Organizer's 販売業者 business details are plain Organizer fields.
- "Organizer" is the business, in any letter case; the audience name `organizer` (spec paths, `rpc.organizer.v1`, the organizer console) is the Organizer's. A person who uses the organizer console for an Organizer is a **member** of that Organizer, and **owner** is a member's role (the only one today). A member's account is an **identity** in the Organizer's **Organization**. Liverty Music staff are **admins**.
- "tenant", "operator", "seller", "buyer" and "applicant" are not entities: use the Organizer's Organization, member, owner, identity, admin, the Organizer, the User or the fan who entered. `scripts/check-forbidden-words.py` rejects them in `proto/`, `docs/`, `openspec/specs/` and `openspec/schemas/` (`make words`, `CI Success`).

## Before you finish

- Each method name passes the table; each service name is an entity name.
- No fan request has a `user_id`; no `Get` takes another entity's id.
- Every ID field is `<entity>_id` or `provider_<concept>_id`.
- The adapter spec under `openspec/specs/components/adapter/<audience>/api/rpc/<handler>/` uses the same method names as the proto.
