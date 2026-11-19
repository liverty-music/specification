## Why

An admin deletes a Concert only to clean up test data: the delete button is reached only from a Concert of an Artist that an Organizer represents, discovery never searches such an Artist, and an Organizer cancels a real concert instead of deleting it. Suppression, which keeps discovery away from a deleted Concert's slot, therefore protects nothing, and it can hide a real concert: a test Event at a real Venue and date leaves a suppressed slot that discovery then skips. The delete also still has a second, lock-free path, and some of its per-record decisions live in SQL instead of the entities. The same review of the backend found four smaller leftovers in removal, rate limiting and the admin handlers.

## What Changes

- **Suppression is removed.** Deleting a Concert no longer records its slot, and discovery no longer skips a slot because a Concert was deleted there. The SuppressedConcert entity, its Exists operation and the story `delete-a-wrong-concert` are retired; the stored suppression records are dropped. **BREAKING** for nobody in practice: the admin delete is reached only for Artists that discovery never searches.
- **Concert.DeleteAndSuppress becomes Concert.Delete.** It removes the Event with the same records as today, with the same refusals; the only difference is that nothing is suppressed. The unused Delete that removed an Event without the removal's locks and checks goes (backend#700).
- **The per-record rules of a removal are the entities' own.** An Order leaves with its Event only when it is Void or Refunded; a first-party Series leaves when the removal leaves it with no Event, and a discovered Series stays. Concert.Delete and Organizer.Delete apply these rules; their outcomes do not change.
- **TicketStock.Delete removes only the Void Orders its check allowed** (backend#741). An Order that names the TicketStock and is not Void still makes the delete fail, also one created while the delete runs.
- **Leftovers with no change in what a caller sees:** the rate limiter takes its clock as an argument, so its test no longer depends on wall-clock timing (backend#739); the admin notification and order handlers leave request validation and error codes to the shared interceptors (backend#701); ConcertRepository.Create's natural-key race is re-checked against the current code and fixed or closed (backend#310).

## Capabilities

### New Capabilities

- `components/entity/concert/delete`: Concert.Delete removes an Event with every record that depends only on it, refused while a purchase is live. It takes over the requirements of `concert/delete-and-suppress` without suppression.

### Modified Capabilities

- `components/entity/concert/delete-and-suppress`: every requirement removed; the capability is retired in favour of `components/entity/concert/delete`.
- `components/entity/suppressed-concert`: every requirement removed; the entity is retired.
- `components/entity/suppressed-concert/exists`: every requirement removed; the operation is retired.
- `stories/delete-a-wrong-concert`: every requirement removed; the story is retired.
- `components/entity/order`: adds the rule that an Order leaves with its Event only when Void or Refunded.
- `components/entity/series`: adds the rule that a first-party Series leaves with its last Event and a discovered Series stays.
- `components/usecase/concert/delete`: removes the Concert with Concert.Delete; nothing is suppressed. Purpose edited at archive (Purpose).
- `components/usecase/concert/create-from-discovered`: the suppressed-slot skip is removed, a resolved event is no longer qualified as unsuppressed, and the ingest signal no longer counts suppressed events. Purpose and sequence diagram edited at archive (Purpose).
- `components/usecase/order/refund`: Refund acts at its own current time instead of taking it as an input (backend#701); the outcome is the same.
- `components/adapter/admin/api/rpc/order`: the Refund boundary passes the Order and the reason, not the time.
- `components/adapter/fan/api/webhook/payment-events`: a dispute calls Refund with the Order and the reason Dispute, not the time the notice was received; Refund takes its own current time.
- `components/usecase/concert/search-new-concerts`: drops the mention of SuppressedConcerts.
- `components/usecase/concert-candidate/approve`: the requirement that approval does not check suppression is removed.
- `components/usecase/series/publish`: drops the sentence and scenario about a slot where an admin deleted a Concert.
- `components/entity/series/publish-events`: drops the sentence and scenario about a SuppressedConcert at the slot.
- `components/entity/series/update`: drops the mention of a SuppressedConcert at the new slot.

Unchanged: `components/entity/ticket-stock/delete` already requires the behaviour backend#741 restores. `components/entity/organizer/delete` keeps its requirements; it shares the removal with Concert.Delete. `components/entity/rejected-concert` keeps "The log never suppresses", which states that a rejected entry affects no later discovery and stays true.

## Impact

- backend: `internal/entity` (concert, event removal, order, series, suppressed concert), `internal/infrastructure/database/rdb` (concert, event removal, suppressed concert, ticket stock), `internal/usecase` (concert, concert creation), `internal/di`, `internal/infrastructure/server/ratelimit`, `internal/adapter/rpc` (admin notification and order handlers), mocks and tests; an Atlas migration that drops `suppressed_concerts` and replaces `delete_ticket_stock`.
- No proto, frontend or cloud-provisioning change: the admin RPC `ConcertService.Delete` keeps its name and its errors.
