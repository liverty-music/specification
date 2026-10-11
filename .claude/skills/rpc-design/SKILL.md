---
name: rpc-design
description: Naming rules for RPC services, methods and request messages in this repository's proto (rpc/**/v1) and adapter specs. Use when adding, renaming or reviewing a service or an rpc, choosing between Get/List/ListBy/Set/Update or a custom verb, deciding which service a method belongs to, or writing an adapter spec that names RPCs. Where it differs from the user-scope protobuf skill (Google AIP-132/136), this skill wins.
---

# RPC design rules (liverty-music)

The goal: a developer predicts a method's input and behavior from its name alone, and every service follows the same rules. These rules override the AIP guidance in the user-scope `protobuf` skill where they differ; everything else in that skill (wrapper messages, protovalidate, comments, field numbering) still applies.

## Services

- A service is named after an entity in `openspec/specs/components/entity/` (`TicketSaleService`, `KycService`). A service with no entity behind it is not created; put its methods on the entity they act on, or remove them.
- A service's standard methods take and return only its own resource. A read of another resource goes to that resource's service (`OrderService.Get`, not `TicketService.GetOrder`).
  - A read may carry related resources as side lists (`ConcertService` responses carry `series` and `artists`).
  - A create may carry child resources created with the parent (`TicketSaleService.Create` with its ticket types).
- Packages name the caller: `rpc.<entity>.v1` is the fan API; `rpc.admin.`, `rpc.organizer.` and `rpc.scanner.` are the admin console, organizer console and venue scanner device. The same method name in two packages narrows by the same Key; the payload may differ.

## Methods

| Form | Use | Example |
|---|---|---|
| `Get(<own id or natural key>)` | read one resource | `CheckoutService.Get(checkout_id)`, `PushSubscriptionService.Get(endpoint)` |
| `Get()` | the one resource the caller has | `OrganizerService.Get()`, `KycService.Get()` |
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
- **The caller is never named.** When the caller owns the resource, neither the method name nor the request names them; the server takes the user from the sign-in (`User.GetByExternalID`). No `user_id` on a fan's own request. A request names a user or an Organizer only when an admin acts on another one.
- A multi-step purchase uses the same verbs everywhere: `Start` (create or resume a draft resource), `Authorize` (open the card hold, return the client secret), `Confirm` (finalize). `CheckoutService` and `LotteryEntryService` both follow it. A card hold is an attribute of the resource, never a resource-less `CreateAuthorization`.
- Request fields with the same meaning have the same name across services (`ticket_count` on both `Start` methods).

## Deviation from Google AIP

AIP-132 narrows a `List` with `parent` plus `filter`, and AIP-136 forbids standard verbs (`List`) in custom methods. `ListBy<Key>` and `List<Qualifier>` break both on purpose: the name then states what it filters on. Rejected: `List(parent)` with typed filter fields, because `List(series_id, event_id?)` does not say what it narrows by. Request and response messages are `<Method>Request` / `<Method>Response` (`ListByEventRequest`), not AIP's `ListBooksRequest`.

## Vocabulary traps

- "identity" means the account at the identity provider (Zitadel). The result of a fan's 本人確認 is the entity `Kyc`; the payment provider's check of an Organizer's payout account is "payout account verification", not KYC. Do not name anything else "identity" or "Kyc".
- "holder", "buyer", "applicant" and "seller" are not entities. A ticketing record's User is `user`; the Organizer's legal seller details are plain Organizer fields.

## Before you finish

- Each method name passes the table; each service name is an entity name.
- No fan request has a `user_id`; no `Get` takes another entity's id.
- The adapter spec under `openspec/specs/components/adapter/<audience>/api/rpc/<handler>/` uses the same method names as the proto.
