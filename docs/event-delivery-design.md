# Event Delivery Design

How the backend announces a fact to other parts of the system (NATS JetStream events) and how it starts work that must happen after a fact (DBOS workflows), without losing or duplicating either. This is a design reference for people and for coding agents. It records the decision; the implementation is planned as an OpenSpec change and replaces the event id rule of `introduce-durable-workflows` (design "One id per announcement").

Status: decided 2026-10-28, not implemented yet. Facts below were checked against DBOS Transact Go v1.7.0, watermill v1.5.3, watermill-sql v4.1.5 and watermill-nats v2.2.0 on that date.

## The rules

1. **An event is written in the transaction that commits its fact.** The fact and its event are both recorded, or neither is. No code publishes to NATS directly.
2. **An event's id is made once, when the event is written** (UUIDv7), and is stored with it. Every send of the event, first or repeated, carries that id. No id is derived from a workflow step, a counter or business values.
3. **No change, no event.** An operation that finds its change already made writes nothing, so a retried request, a redelivered message or a step that runs again announces nothing a second time.
4. **The entity operation announces, not the usecase.** Its name and its Go doc tell the usecase what it announces (see "The entity operation contract").
5. **The payload is the changed entity, as its `entity/v1` proto message in binary.** There are no event-only types. The subject names the fact.
6. **Work that must follow a fact is started by the event's consumer, as a workflow whose id is the business key** (`issue:<entry>`). DBOS runs one workflow per id, so a repeated event starts nothing new.
7. **A consumer treats an event it has seen as done.** JetStream drops a repeated id for only 2 minutes; past that, the consumer's own state (a send time, a unique key, PostHog's `uuid`) drops it.

## Why

What the code did before this design:

| Problem | Where | Effect |
|---|---|---|
| The fact is committed, then the event is published in a second call | every `PublishEvent` call after a repository write (31 sites) | A failed publish is logged and the event is lost (`follow_uc.go:208-210`). A crash between the two loses it silently |
| Outside a workflow, the id is a fresh random value on every attempt | `messaging.NewEvent` | A retried API call or a redelivered message publishes the same fact with a new id: a duplicate no one can drop |
| Inside a workflow, the id comes from the step (`<workflow id>/<step id>/<n>`) | `messaging.eventID` | Correct only when the step publishes the same list in the same order on every run; a list read inside the step can shift and drop another fan's event as a duplicate |
| Fan-out by one workflow step per item | `make-lottery-draw-durable` plan (announce and start per entry) | 1,000,000 entries cost 1,000,000 sequential checkpoint writes in the parent workflow |
| Each payload is a hand-written JSON struct (`entity/event_data.go`) | every subject | Most fields repeat the entity (`LotteryEntryDrawnData` vs `LotteryEntry`); wire compatibility rests on a rule not to rename `json` tags, which no tool checks |

## Patterns compared

| Pattern | Used by | Weakness |
|---|---|---|
| Random id on every publish | the backend outside workflows | No retry can be recognised |
| Id from business values (`order-123-paid`) | NATS and Synadia examples | The same kind of fact can happen twice to one entity (follow, unfollow, follow), and the second is dropped as a duplicate |
| Id from the cause (workflow step, incoming message id) | the backend inside workflows | Works only when the same cause runs again; several events from one cause need a position |
| **Id made once with the fact and stored (transactional outbox)** | microservices.io, the Watermill forwarder example, DBOS's outbox example (a transactional step then a send step) | Needs an outbox table and a relay |

The transactional outbox is the only pattern that removes both the lost event and the duplicate everywhere, and it needs no rule about where the code runs. CloudEvents allows it explicitly: an event re-sent after a network error may keep its `id`.

## The design

```
 usecase (no messaging code)
   |
   |  entity operation = one repository method, one DB transaction
   |  +------------------------------------------------------------------+
   |  | UPDATE lottery_entries SET state = 'lost' ... WHERE state = 'won'  |  the fact
   |  | if rows changed:                                                   |
   |  |   INSERT INTO watermill_<topic> (uuid, payload, metadata, ...)     |  the event,
   |  |   uuid = UUIDv7 made here                                          |  watermill-sql
   |  |   payload = proto.Marshal(pb.FromLotteryEntry(entry))              |  Publisher on the tx
   |  +------------------------------------------------------------------+
   v                     commit: both or neither
 forwarder (watermill components/forwarder, in workflow-worker)
   |  reads committed rows in order, in batches
   |  publishes each with its stored uuid  -->  Nats-Msg-Id (TrackMsgID)
   |  crash after publish, before ack  -->  publishes again, same uuid
   v
 JetStream  (drops a repeated Nats-Msg-Id within 2 min)
   |
   +--> analytics consumer      drops a repeat by event id (PostHog uuid)
   +--> notification consumer   drops a repeat by its send time column
   +--> workflow starter        Start Issue(entry), id issue:<entry>
                                 DBOS runs one workflow per id
```

### What each provided feature does

| Need | Provided by | Our code |
|---|---|---|
| Write the event in the caller's transaction | watermill-sql `NewPublisher` accepts a transaction; `TxFromPgx(pgx.Tx)` adapts our pgx transaction; `Publish(topic, msgs...)` is one multi-row `INSERT` | A small helper that publishes on the repository's transaction |
| Store a binary payload | watermill-sql `GeneratePayloadType` (`BYTEA` instead of the default JSON) | The schema option and its Atlas migration |
| Read committed events in commit order | watermill-sql PostgreSQL schema: `transaction_id xid8` and `pg_snapshot_xmin`, so a row of a transaction still open is never skipped | None |
| Relay to NATS with the original id | watermill `forwarder`: the envelope keeps the original UUID and metadata and restores them before publishing | Wiring in `workflow-worker` |
| Drop a repeated publish | watermill-nats `TrackMsgID: true` (already set) sends the UUID as `Nats-Msg-Id` | None |
| Encode the payload | the generated `entity/v1` messages and the entity-to-proto functions | Move the functions from `internal/adapter/rpc/mapper` to `internal/adapter/pb` (see "The payload") |
| Start follow-up work once | DBOS workflow id | The consumer names the workflow id after the business key |
| Start one workflow atomically with a fact, outside a workflow | DBOS `Enqueue` with `WithEnqueueTransaction(tx)`; the DBOS tables are in the application database (schema `dbos`) | None. Use it for a command with one receiver (for example, a checkout that must be issued), not for an event |

What goes away: the UUIDv5 namespace, the step origin in the context, the per-step counter, the `EventPublisher` dependency of the usecases, the payload structs of `entity/event_data.go` (the subject constants stay), and the rule "a step publishes once".

### Commands and events

- **Event**: a fact other parts react to, any number of receivers (analytics, notifications, a workflow starter). Goes through the outbox.
- **Command**: one receiver must do one piece of work. Inside a workflow, `Flow.Start` (DBOS checkpoints it). Outside a workflow, `Enqueue` with `WithEnqueueTransaction` in the transaction of the fact, or an event whose consumer starts the workflow when the work follows a fact that is already announced.
- Rejected: one DBOS workflow per event as the outbox. DBOS v1.7.0 has only a per-workflow `Enqueue` (no bulk enqueue; `SendBulk` sends messages to workflows, not to NATS), and each event would cost a workflow row, a dequeue, a step checkpoint and a status update.

## The entity operation contract

The usecase must know what an operation announces without knowing that an outbox exists. The name and the Go doc carry it, as they already carry the rest of the contract; the return value does not change.

```go
// RevertWin makes a Won entry with no Order Lost, recording that its card
// authorization could not be charged.
//
// # Announces
//
//  - ORDER.lottery_entry_drawn with the entry, when it changes the entry.
//    Nothing when the entry is already Lost.
//
// # Possible errors
//  ...
RevertWin(ctx context.Context, id LotteryEntryID) error
```

- **Name**: a domain verb (`RevertWin`), never a suffix such as `AndPublish`. The announcement is a consequence of the fact.
- **Go doc**: an `# Announces` section next to `# Possible errors`: the subject, the entity in the payload, and when nothing is announced. "In the same transaction" is always true and is not repeated.
- **Spec**: the entity operation's scenario names the announcement ("THEN the entry is Lost and the lottery result is announced"). Usecase specs no longer announce.
- **Checks**: a comment proves nothing, so each announcing operation has a repository contract test that asserts one outbox row when the state changes and none when it does not.
- The usecase packages lose `EventPublisher`, so an announcement outside an entity operation does not compile.

Rejected:

- **An event type returned by the operation** (`RevertWin(...) (LotteryEntryDrawn, error)`): a second definition of the entity that the entity and usecase layers must know only to publish.
- **The usecase builds the event and passes it in**: it would build the event before knowing whether anything changed, and could pass one that disagrees with the change.
- **The DDD aggregate** (load the entity, call a method that changes it and records the event on the struct, save both): the guard of each change would move from the SQL condition (`WHERE state = 'won'`) to memory and need a version column for concurrent writers; set-based operations such as recording a draw for 1,000,000 entries cannot load their entities; and the usecase would make three calls for one atomic piece of work. Entities keep their pure methods with receivers for rules that need no I/O (`Checkout.StatusAt`, `ResaleListing.Fee`).

## The payload

- **The entity's own proto message.** `entity/v1` is the service-wide definition of each entity in the ubiquitous language, independent of any screen or transport, so it is also the event's schema. `buf breaking` checks its wire compatibility in CI.
- **A field is left out of an entity's proto only for personal data** (below), never because no screen reads it. `LotteryEntry` gains `referral_code`, which its mapper left out "because no screen reads it".
- **A fact that is not entity state is either made entity state or read by id.**
  - Why an entry lost (its card could not be charged) is shown to the fan in the loss email: it becomes an attribute of LotteryEntry.
  - The draw time is the TicketSale's: the consumer reads the TicketSale by id. LotteryEntry gains `ticket_sale_id` next to `ticket_type_id` (a composite foreign key keeps the two consistent), so this is one read.
  - The time the fact happened is the CloudEvents `time` attribute.
- **Encoding: binary protobuf**, `datacontenttype` `application/protobuf`. Measured for one LotteryEntry (Go 1.25, protobuf-go):

  | | binary | protojson | the old JSON struct |
  |---|---|---|---|
  | Size | 156 B | 309 B | 309 B |
  | Marshal | 0.51 µs | 4.6 µs | 1.4 µs |
  | Unmarshal | 0.88 µs | 6.1 µs | - |

  For 1,000,000 events that is 156 MB against 309 MB in the outbox and the stream. The cost is that a message is not readable as text on the wire; read it with the generated types.
- **Conversion** lives in `internal/adapter/pb` (moved from `internal/adapter/rpc/mapper`, which RPC handlers and the outbox both use): `pb.FromLotteryEntry(e)` returns the proto message, `pb.ToLotteryEntry(m)` the entity. The name `proto` is avoided because the same files import `google.golang.org/protobuf/proto`. The infrastructure layer may import the adapter layer.

### Personal data

- The email address may be in a payload. The stream stays inside the cluster with a limited retention, and the analytics consumer forwards only the fields it maps.
- The full name and phone number a fan gives for the ticket face (`users.full_name`, `users.phone_number`) are never in a payload. They are what must be protected.
- `identity_verifications` keeps storing no personal data beyond the provider's id (`schema.sql`, comment on `provider_user_id`). It records verification results; the name a fan types is a declaration, not a result.
- `users.name` (the identity provider's display name) duplicates the full name and has no business use in the backend; it is dropped unless the frontend needs it.

The rule in `entity/event_data.go` that payloads carry "ids only, never personal data" is replaced by these rules.

## Inside a workflow

A step that calls an entity operation can run again after the operation committed (a crash before the step's checkpoint). Rule 3 makes this safe: the operation finds its change made and announces nothing. So no `dbos.RunAsTransaction` and no step-derived id are needed. An operation that cannot tell whether its change was made (an append without a key) is a defect to fix in the operation, not in the workflow.

## Scale: one sale with 1,000,000 entries

| Step | Writes |
|---|---|
| Record the outcome and its 1,000,000 events | One transaction; the events go in multi-row `INSERT`s of a few thousand rows (PostgreSQL allows 65,535 parameters per statement) |
| Relay | The forwarder reads and publishes in batches (`SubscribeBatchSize`, default 100, to be tuned) and records one offset per batch |
| Charge and release | One workflow per entry, started by the consumer. This cost is inherent: each entry needs its own Stripe call |

The parent workflow (`Draw`) writes no checkpoint per entry.

## Open points for the OpenSpec change

- Retention: the PostgreSQL schema keeps forwarded rows. Choose a scheduled delete of rows older than the duplicate window plus a margin, or watermill-sql's queue schema (deletes on ack) after checking that it also never skips a row of an open transaction.
- Events with no state change behind them (if any): list them; each needs a fact to attach to or an explicit exception.
- The forwarder's failure signal: a row that is not forwarded must reach an admin, as "Workflow Needs Admin" does for workflows.
- Moving the consumers (analytics, notifications) from the JSON structs to the proto payloads, and the order of the switch.
- Compare every entity struct with its proto message and add the fields left out for no personal-data reason.
- Whether the frontend reads `users.name` before dropping it.
- The order of the work: the `internal/adapter/pb` move first as its own refactor, then this change, then `make-lottery-draw-durable` re-planned on top of it (`Draw` stops starting and announcing per entry).

## Sources

- DBOS: [Transactional outbox example](https://docs.dbos.dev/python/examples/outbox), [Architecture](https://docs.dbos.dev/architecture), [Steps (Go)](https://docs.dbos.dev/golang/tutorials/step-tutorial); v1.7.0 source `dbos/workflow.go` (`Enqueue`, `WithEnqueueTransaction`, `SendBulk`), `dbos/datasource.go` (`RunAsTransaction`).
- NATS: [Streams (duplicate window)](https://docs.nats.io/nats-concepts/jetstream/streams), [JetStream headers](https://docs.nats.io/reference/jetstream/api/headers), [Synadia: preventing duplicate messages](https://www.synadia.com/blog/prevent-existing-duplicate-messages-jetstream).
- [microservices.io: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html).
- [CloudEvents spec, `id`](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md).
- Watermill: `components/forwarder` (`envelope.go`), [transactional events forwarder example](https://github.com/ThreeDotsLabs/watermill/tree/master/_examples/real-world-examples/transactional-events-forwarder); watermill-sql v4 `pkg/sql` (`publisher.go`, `schema_adapter_postgresql.go`, `adapters_pgx.go`, `queue_schema_adapter_postgresql.go`).
