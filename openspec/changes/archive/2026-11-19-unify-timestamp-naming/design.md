## Context

See proposal.md for why. Facts that shape the approach:

- Prod DB migrations are applied by the Atlas Operator. ArgoCD's `backend-migrations` app tracks backend `main` (`cloud-provisioning/k8s/argocd-apps/prod/backend-migrations.yaml`), so a migration reaches prod as soon as its backend PR merges. The backend images in prod change only when cloud-provisioning bumps the pinned release tag (`k8s/namespaces/backend/overlays/prod/kustomization.yaml`).
- The backend maps rows to entities by hand with pgx; there is no sqlc. A column rename changes no Go code by itself: every query naming the column changes by hand.
- The frontend talks to the backend with `createConnectTransport` and its default JSON format (`frontend/src/services/grpc-transport.ts`). A proto field rename keeps the field number, so binary clients do not notice it, but the JSON key changes (`soldTime` to `sellTime`).
- watermill-sql v4.1.5's `PostgreSQLQueueSchema` names `created_at` only in its table-creating DDL, which the backend never runs (Atlas creates the table). Its INSERT lists `uuid, payload, metadata` and its SELECT reads `"offset", uuid, payload, metadata`. The only reader of the column is the backend's own query in `internal/infrastructure/messaging/outbox.go` (the oldest undelivered announcement).

## Goals / Non-Goals

**Goals:**

- One rule, stated once per repository's AGENTS.md and enforced for the DB by `make lint-schema`.
- Every timestamp name in proto, DB, Go, TS and specs follows it on the day the cutover finishes.

**Non-Goals:**

- Names another system defines stay on the wire: the JSON keys of Zitadel webhook payloads (`created_at`), Stripe objects (`expires_at`), PostHog exports read by the analytics SQL in cloud-provisioning, and the files `abeval.go` reads (`captured_at`). The Go fields that hold them follow the rule (`CreateTime time.Time \`json:"created_at"\``).
- Local variables that hold a clock reading for a duration (`const startedAt = performance.now()`) are not fields and are left as they are.
- No other renames. Two names noticed on the way stay as they are: `ended_email_send_time` and `loss_email_send_time` name their emails differently, and the event-level "resale deadline" in the resell-a-ticket story stays (a listing's close time is that deadline).

## Decisions

### The rule

A timestamp's name is the present-tense verb of the moment it records, followed by `time` in the layer's case: spec `sign time`, proto and DB `sign_time`, Go `SignTime`, TS `signTime`. Only the last word before `time` is the verb. Words before it name what the moment is about and keep their own form: `sold_email_send_time` is the send time of the "sold" email, `hold_expire_time` the expire time of the hold. When the present tense reads badly, the concept takes another verb that reads well and means the same: `discover` becomes `find`, and `sold` becomes `sell`. The creation moment is `create_time` (AIP-148).

`_time` over `_at`: proto must follow AIP-142, and proto is the language-independent form of the entity spec, so the DB, which no other system reads, follows proto rather than the other way round. `_at` also expects a past participle (`paid_at`), which brings back the second verb form this change removes. A DB reader could take `start_time` for SQL's `TIME` type, but `lint-schema` allows only `TIMESTAMPTZ`, date-only columns end in `_date`, and every column has a `COMMENT ON`.

### Column renames

| table | old | new |
|---|---|---|
| `users` | `last_login_at` | `last_login_time` |
| `artists` | `fanart_synced_at` | `fanart_sync_time` |
| `artists` | `official_site_checked_at` | `official_site_check_time` |
| `events`, `concert_candidates`, `rejected_concerts`, `suppressed_concerts` | `start_at` | `start_time` |
| `events`, `concert_candidates`, `rejected_concerts` | `open_at` | `open_time` |
| `concert_searches`, `ticket_sale_searches` | `searched_at` | `search_time` |
| `concert_searches` | `last_found_at` | `last_find_time` |
| `notifications`, `resale_entries`, `resale_listings`, `settlements`, `passkeys`, `watermill_events_outbox` | `created_at` | `create_time` |
| `notifications` | `read_at` | `read_time` |
| `concert_candidates`, `ticket_sales` | `discovered_at` | `find_time` |
| `rejected_concerts` | `rejected_at` | `reject_time` |
| `suppressed_concerts` | `suppressed_at` | `suppress_time` |
| `identity_verifications` | `verify_at` | `verify_time` |
| `ticket_sales` | `sale_start_at`, `sale_end_at` | `sale_start_time`, `sale_end_time` |
| `ticket_sale_reminders` | `sent_at` | `send_time` |
| `card_authorizations` | `expire_at` | `expire_time` |
| `orders` | `pay_at`, `confirmation_send_at` | `pay_time`, `confirmation_send_time` |
| `order_refunds`, `resale_listings` | `refund_at` | `refund_time` |
| `lottery_entries` | `loss_email_send_at` | `loss_email_send_time` |
| `resale_entries` | `draw_at`, `ended_email_send_at` | `draw_time`, `ended_email_send_time` |
| `resale_entries`, `resale_listings` | `withdraw_at` | `withdraw_time` |
| `checkouts` | `hold_expire_at`, `commit_at`, `capture_at` | `hold_expire_time`, `commit_time`, `capture_time` |
| `tickets` | `issue_at`, `admit_at` | `issue_time`, `admit_time` |
| `resale_listings` | `sold_at`, `sold_email_send_at` | `sell_time`, `sold_email_send_time` |
| `payout_accounts` | `provisioned_at`, `status_synced_at` | `provision_time`, `status_sync_time` |
| `settlements` | `release_at` | `release_time` |
| `processed_webhook_events` | `processed_at` | `process_time` |
| `wallet_public_keys` | `registered_at` | `register_time` |
| `scanners` | `bound_at`, `revoked_at` | `bind_time`, `revoke_time` |
| `admissions` | `admitted_at` | `admit_time` |
| `rejected_scans` | `scanned_at` | `scan_time` |

The migration is written by hand as `ALTER TABLE ... RENAME COLUMN`: `atlas migrate diff` sees a rename as a drop and an add and would lose the data. PostgreSQL carries indexes, constraints and partial-index predicates over a rename; index names that contain an old column name are renamed too, so `schema.sql` and the database agree. Each `COMMENT ON COLUMN` moves with the column; the comments are rewritten only where they quote the old name.

### Proto renames

| message | old | new |
|---|---|---|
| `entity.v1.ResaleListing` | `sold_time` | `sell_time` |
| `entity.v1.ResaleListing` | `deadline_time` | `close_time` |
| admin `ConcertCandidate` (`rpc/admin/concert_candidate/v1`) | `discovered_time` | `find_time` |

Field numbers stay. The proto PR carries the `buf skip breaking` label.

### Go, TS and log keys

Go entity fields: `DiscoveredTime` to `FindTime`, `LastFoundTime` to `LastFindTime`, `SoldTime` to `SellTime`, `RejectedTime` to `RejectTime`, `SuppressedTime` to `SuppressTime`, `ScannedTime` to `ScanTime`, `SearchedTime` to `SearchTime`, `SignedTime` to `SignTime`, `BoundTime` to `BindTime`, `RevokedTime` to `RevokeTime`, `RegisteredTime` to `RegisterTime`, and the deadline of a ResaleListing to `CloseTime`. Outside `entity`: `CreatedAt` to `CreateTime` in the Zitadel webhook payloads (JSON keys kept), `ReceivedAt` to `ReceiveTime` in the Stripe webhook input. `slog` keys follow the column names (`start_time`, `last_find_time`).

TS: the ResaleListing entity and mapper (`sellTime`, `closeTime`), the wallet snapshot kept on the device (`savedAt` to `saveTime`), and the referral record in local storage (`expiresAt` to `expireTime`). A referral record saved under the old key fails the reader's shape check and is dropped like a missing one. A wallet snapshot has no shape check: one saved under the old key is still shown offline, with its load time blank, until the next online load overwrites it; dropping it would hide the fan's tickets at the door. No user has saves worth migrating.

### Spec renames

Requirement text goes through the delta specs. Attribute tables in entity Purposes are renamed in the main specs when the change archives. Five scenario titles name a renamed timestamp; OpenSpec cannot rename a scenario through a delta (a MODIFIED block must keep every scenario name), so the plan PR renames those titles directly in the main specs, and the backend PR updates the `@spec` annotations that cite them (`ticket_sale_test.go`, `ticket_sale_discovered_repo_test.go`, `ticket_sale_reminder_test.go`, `resale_listing_test.go`). Until it merges those annotations cite titles that no longer exist; nothing checks them before archive.

### Lint

`scripts/lint-schema.sh` gains a check that fails on any column whose name ends in `_at`. The audit-column check then rejects `update_time` and `delete_time` instead of `updated_at` and `deleted_at`, which the new check already rejects.

## Risks / Trade-offs

- [The migration reaches prod when the backend PR merges, while prod still runs the release that reads old names] → Accepted outage. Cut the backend release and the cloud-provisioning tag bump right after the merge, so the outage lasts one release and one sync.
- [An old frontend reads JSON keys the new backend no longer sends (`soldTime`, `deadlineTime`)] → Deploy the frontend in the same window. The fan's resale listings and the admin approval queue read these keys.
- [A durable workflow or outbox row written before the cutover carries a renamed field] → Outbox payloads are binary protobuf, which a field rename does not affect. DBOS stores workflow inputs, step results and outputs as JSON, so a renamed Go field without a `json` tag would lose its value; no type a registered workflow stores holds a renamed field, so a pending workflow resumes unchanged.
- [Between the migration and the new release, the old worker's every-minute schedules (DrawDueSales, DrawResale) read renamed columns] → They fail with undefined_column, which is not retried, and end ERROR, raising `workflow.needs_admin`. Accepted (no users): delete those runs after the rollout.
- [A query the hand edit misses fails only at run time] → The repository integration tests run every query against a migrated database; `grep -rnE '\b[a-z_]+_at\b'` over `internal/` must find only the external JSON keys listed in Non-Goals.

## Migration Plan

1. specification: merge the proto PR, publish the release, wait for BSR generation.
2. backend and frontend: prepare both PRs against the new generated types; push only after BSR generation (workspace dependency order).
3. Check that no type a registered workflow stores holds a renamed field.
4. Merge the backend PR (the migration applies), publish the backend release, merge the cloud-provisioning tag bump; merge and release the frontend in the same window.
5. Verify: the AtlasMigration status is applied, the rollout is complete, and the logs show no `column ... does not exist` error.

Rollback: a reverse migration (`RENAME COLUMN` back) and the previous release tag. Nothing is dropped, so no data is lost either way.
