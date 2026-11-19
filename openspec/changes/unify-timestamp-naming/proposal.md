## Why

A timestamp has a different name in each layer: the DB column is `created_at`, while proto, Go and TS say `create_time` / `CreateTime` / `createTime`. Worse, the verb form drifts too: the DB has both `tickets.admit_at` and `admissions.admitted_at`, and entities that have no proto message took the DB's past participle into Go (`ScannedTime`, `SignedTime`, `RevokedTime`) and into the entity specs (`signed time`, `bound time`), while proto says `scan_time`, `sign_time`, `revoke_time`. Searching for one name misses the others, and every new field needs a judgement call between two rules. The product has no public users yet, so renaming now costs only the work.

## What Changes

- One naming rule for every timestamp in every layer: the present-tense verb followed by `time` (spec `create time`, proto and DB `create_time`, Go `CreateTime`, TS `createTime`). Words before the verb name what the time is about and keep their own form (`sold_email_send_time` is "when the sold email was sent").
- Where the mechanical present tense reads badly, the concept gets a natural name: `discovered` becomes `find` (`find_time`, `last_find_time`), `sold` becomes `sell` (`sell_time`).
- **BREAKING** (DB): every `*_at` column of the backend schema is renamed to its `*_time` name, `watermill_events_outbox.created_at` included. `make lint-schema` rejects any `*_at` column from then on.
- **BREAKING** (proto): `ConcertCandidate.discovered_time` (admin RPC) becomes `find_time`, `ResaleListing.sold_time` becomes `sell_time`, and `ResaleListing.deadline_time` becomes `close_time`, the instant the listing stops being open.
- Go entity fields, log attribute keys, and TS fields and on-device storage keys follow the rule (`ScannedTime` to `ScanTime`, `savedAt` to `saveTime`). Names an external system defines (the JSON keys of Zitadel and Stripe payloads) are kept on the wire.
- The rule replaces the split one in `backend/AGENTS.md` and `specification/AGENTS.md`.
- The DB rename ships as one cutover: the migration and the backend that reads the new names go out together, and a short outage is accepted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

Requirements whose text names a timestamp in the past participle, or a listing's deadline, are restated with the new name. No behaviour changes.

- `components/entity/admission-code` (Purpose): `signed time` to `sign time` in the freshness rule and the attribute table.
- `components/entity/admission-code/decode`, `components/entity/admission-code/verify`: `signed time` to `sign time`.
- `components/entity/concert-candidate` (Purpose): attribute `discovered time` to `find time`.
- `components/entity/concert-candidate/list-pending`: ordered by find time.
- `components/entity/concert-candidate/upsert`: find time.
- `components/entity/concert-search` (Purpose): `last found time` to `last find time` in "recently discovered" and the attribute table.
- `components/entity/concert-search/upsert`: last find time.
- `components/entity/concert-search/mark-found`: last find time; the requirement "Last found time set to now" becomes "Last find time set to now".
- `components/entity/rejected-concert` (Purpose): attribute `rejected time` to `reject time`.
- `components/entity/rejected-concert/append`: reject time.
- `components/entity/rejected-scan` (Purpose): attribute `scanned time` to `scan time`.
- `components/entity/resale-listing` (Purpose): attribute `sold time` to `sell time`; the requirement "Resale deadline" becomes "Close time", and "Open and expired" and "Free for a draw" use the listing's close time.
- `components/entity/scanner` (Purpose): `bound time` and `revoked time` to `bind time` and `revoke time`.
- `components/entity/scanner/bind-device`, `components/entity/scanner/revoke`: bind time, revoke time.
- `components/entity/suppressed-concert` (Purpose): attribute `suppressed time` to `suppress time`.
- `components/entity/ticket-sale` (Purpose): `discovered time` to `find time`; the requirement "The discovered time is set once" becomes "The find time is set once".
- `components/entity/ticket-sale/upsert-discovered`: find time.
- `components/entity/ticket-sale-search` (Purpose): `searched time` to `search time`; the requirement "Searched time is not in the future" becomes "Search time is not in the future".
- `components/entity/ticket-sale-search/list-by-series`, `components/entity/ticket-sale-search/record`: search time; the requirement "Record sets the searched time of every given series" becomes "Record sets the search time of every given series".
- `components/entity/wallet-public-key` (Purpose): attribute `registered time` to `register time`.
- `components/entity/wallet-public-key/register`: register time.
- `components/usecase/concert/search-new-concerts`, `components/usecase/resale-listing/list`, `components/usecase/scanner/list-by-event`, `components/usecase/scanner/open`, `components/usecase/ticket/admit`, `components/usecase/ticket-sale/scan-due-reminders`, `components/usecase/wallet-public-key/get`, `components/usecase/wallet-public-key/register`: the same renames in their text. Their sequence diagrams name no timestamps, so their Purposes are unchanged. The entity operations they rely on are listed above.
- `components/adapter/fan/api/rpc/resale-listing`: a returned listing carries its close time and sell time.
- `components/adapter/organizer/api/rpc/scanner-device`: a call carries a sign time.

Entities marked (Purpose) get their attribute tables renamed directly in the main spec when this change archives.

Five scenario titles name a renamed timestamp. OpenSpec cannot rename a scenario through a delta, so this change renames them directly in the main specs, and the backend tests that cite them update their `@spec` annotations:

| capability | old scenario title | new scenario title |
|---|---|---|
| `components/entity/concert-search/upsert` | Restart keeps last found time | Restart keeps last find time |
| `components/entity/ticket-sale` | Re-discovery keeps the discovered time | Re-discovery keeps the find time |
| `components/entity/ticket-sale-search` | Future searched time | Future search time |
| `components/entity/resale-listing` | Before the deadline | Before the close time |
| `components/entity/resale-listing` | At the deadline | At the close time |

## Impact

- **specification (proto)**: three field renames in `entity/v1/resale_listing.proto` and `rpc/admin/concert_candidate/v1/concert_candidate_service.proto`; a breaking BSR release. The field numbers stay, so only the generated names change.
- **specification (rules)**: `AGENTS.md` timestamp rule.
- **backend**: an Atlas migration renaming 54 columns; `schema.sql`; every repository query that names them; `outbox.go`'s own query on the outbox; Go entity fields and log keys; `scripts/lint-schema.sh`; `AGENTS.md`.
- **frontend**: the ResaleListing entity and mapper (`sellTime`, `closeTime`), the admin approval queue (`findTime`), the wallet snapshot (`saveTime`) and the referral record (`expireTime`). Values saved on a device under the old keys are dropped; the product has no users whose saves matter.
- **cloud-provisioning**: no change. The analytics SQL reads PostHog exports, not the backend DB, and the one DB function (`delete_ticket_stock`) names no timestamp column.
