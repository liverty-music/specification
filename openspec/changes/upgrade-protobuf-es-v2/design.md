## Context

See `proposal.md` — Why. This document covers *how* the frontend moves from protobuf-es v1 (class-based) to v2 (schema-based), and why we isolate the RPC adapter boundary first.

Current relevant state (frontend repo):
- `@bufbuild/protobuf@^1.10.1`, `@connectrpc/connect@^1.7`, `@connectrpc/connect-web@^1.7`, `@buf/*_es` v1 BSR builds.
- Generated `@buf/*` types are imported by 12 files: 10 inside `adapter/rpc/{client,mapper}` (intended boundary) and 2 outside it (`services/ticket-email-service.ts`, `routes/import-ticket-email/import-ticket-email-route.ts`) — a layering violation.
- No app code calls `toBinary`/`fromBinary`/`toJson`/`fromJson` directly (0 sites); (de)serialization happens inside the Connect-Web transport.
- Mixed Connect client-factory usage already exists: 4 files use v1's `createPromiseClient`, 10 use `createClient`.
- BSR publishes v2.14.x `bufbuild_es` builds of our schema, keyed per commit; upstream `@connectrpc/connect{,-web}` is at v2.

## Goals / Non-Goals

**Goals:**
- Every `@buf/*` generated-type import is confined to `adapter/rpc/{client,mapper}` before the upgrade.
- Frontend runs protobuf-es v2 + Connect-ES v2 with no user-facing behavior change.
- Eliminate the recurring manual "pin back to the v1 build" step on schema bumps.

**Non-Goals:**
- No backend change (Go uses a different protobuf implementation).
- No `.proto` schema change; wire format and RPC contracts are untouched.
- Not chasing the binary-path speedups — Connect-Web uses JSON transport in the browser, so those do not apply.
- No integer-type (`int64`→`bigint`) redesign; that is a separate consideration.

## Decisions

### D1 — Two phases in one change; isolation strictly first

Phase 1 (refactor, still v1) lands and goes green before Phase 2 (upgrade) begins. Rationale: once no consumer outside `adapter/rpc` touches generated types, Phase 2 becomes a mechanical, contained transformation. Doing them together would entangle a behavior-neutral refactor with a breaking upgrade and enlarge the review/debug surface.

*Alternative considered:* two separate changes. Rejected — the refactor has no independent product value and is only meaningful as the enabler for the upgrade; keeping them in one change keeps the intent legible. (Phases still ship as separate PRs.)

### D2 — Ticket-email gets a client + mapper + domain entity, mirroring ticket-journey

`services/ticket-email-service.ts` currently *is* an ad-hoc RPC client (calls `createClient`, returns proto `TicketEmail`). We add:
- `entities/ticket-email.ts` — domain type + TS-union equivalents for the proto enums (`TicketEmailType`, journey status) so consumers never import proto enums.
- `adapter/rpc/client/ticket-email-client.ts` — owns the Connect client and generated request types.
- `adapter/rpc/mapper/ticket-email-mapper.ts` — proto ⇄ entity, following `artist-mapper.ts`/`ticket-journey-mapper.ts`.

The service keeps its public interface but delegates to the new client. `routes/import-ticket-email` switches to `entities/concert.ts` (already exists), `entities/ticket-email.ts`, and the domain journey-status union.

*Alternative considered:* leave the service as-is and only re-type the route. Rejected — it would keep a generated-type leak in the service layer and leave the ticket-email path asymmetric with ticket-journey.

### D3 — v1→v2 API migration mapping

The core generated-API changes, all confined to `adapter/rpc` after Phase 1:

| v1 (class-based) | v2 (schema-based) |
|---|---|
| `import { Foo } from "…/foo_pb.js"` then `new Foo({…})` | `import { FooSchema } from "…/foo_pb.js"` then `create(FooSchema, {…})` |
| `msg` is a class instance | `msg` is a plain object bound to its schema |
| `new EventId({ value: id })` | `create(EventIdSchema, { value: id })` |
| `createPromiseClient(Service, transport)` | `createClient(Service, transport)` |
| service from `*_service_connect.js` (`connectrpc_es`) | service exported from `*_pb.js` (`protoc-gen-es` v2) |
| enums as TS `enum` | v2 enums (verify import path / value shape in mapper) |

Field access on messages is largely unchanged; the churn is construction (`new X` → `create(XSchema, …)`) and imports (`X` → `XSchema`). ~23 construction sites.

### D4 — BSR pin strategy on v2

Repin both `@buf/*_es` packages to the v2 build at the current schema commit, and update `.npmrc`/docs so future bumps stay on the v2 major (v2 becomes the default expectation; `@latest` no longer conflicts once the app is `@bufbuild/protobuf@^2`). Record the exact v2 pin strings in the change so the upgrade is reproducible.

### D5 — Evaluate switching the browser transport to binary format (measure, then decide)

The transport (`createConnectTransport` in `services/grpc-transport.ts`) currently runs without `useBinaryFormat`, so the browser uses JSON — the default, chosen for DevTools readability. The Connect protocol also supports binary (protobuf) encoding, toggled by `useBinaryFormat: true` (or by switching to `createGrpcWebTransport`, which is always binary). Connect-Go negotiates encoding from the request Content-Type, so **no backend change is required** either way.

Binary is where protobuf-es v2.14's headline gains actually land: `toBinary` up to 5× / `fromBinary` up to 2× (JSON paths are 2–3×), plus a smaller wire payload (varint, no field names) that helps most on slow mobile networks. This is the natural pairing with the v2 upgrade.

Decision: **do not hard-code binary in this change.** Keep JSON as the default through Phase 2, then in the verification phase measure JSON vs. binary on *compressed* wire size (gzip/brotli narrows the raw-byte gap) and on (de)serialize timing, and flip `useBinaryFormat` only if the data justifies it. Deciding by measurement avoids trading away DevTools observability for a win that HTTP compression may have already captured.

*Alternatives considered:* (a) flip to binary immediately with v2 — rejected, couples an unmeasured perf bet to the breaking upgrade and removes network-tab readability with no data. (b) never consider binary — rejected, it forgoes v2's biggest lever without evidence.

## Risks / Trade-offs

- **Connect-ES v2 restructures service definitions** (connect codegen folded into `protoc-gen-es` v2) → import paths for services change and may not be a pure find-replace. Mitigation: migrate one client end-to-end first (e.g. ticket-journey), confirm it compiles and the RPC round-trips, then apply the pattern to the rest.
- **Perceived payoff may be modest** — browser JSON transport means the visible win is JSON (de)serialize + ~5% bundle, not binary 2–5×. Mitigation: frame success as "current + de-risked + bundle", and optionally capture a before/after bundle-size and INP number to confirm.
- **Vite `date-impl` alias / build integration** could interact with the dependency bump. Mitigation: run the full Vite build + existing build-template/smoke checks in Phase 2.
- **Enum representation drift** between v1 and v2 could silently change mapper output. Mitigation: mapper unit tests assert entity output for representative fixtures before and after.
- **Regression surfaces as (de)serialization failure**, not a compile error, if a construction site is missed. Mitigation: E2E/Visual across all RPC paths must be green before merge.

## Migration Plan

1. **Phase 1 PR** — isolation refactor (D2), still on v1. Green CI + E2E/Visual → merge. `@buf/*` imports now only in `adapter/rpc`.
2. **Phase 2 PR** — bump deps to v2 (D4), migrate one client fully (D3), then the rest; run full Vite build + E2E/Visual.
3. **Rollback** — Phase 2 is a single dependency+codegen PR; revert restores v1. Phase 1 is behavior-neutral and can stay regardless.
