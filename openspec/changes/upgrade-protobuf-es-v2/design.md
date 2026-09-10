## Context

See `proposal.md` — Why. This document covers *how* the frontend moves from protobuf-es v1 (class-based) to v2 (schema-based), and why we isolate the RPC adapter boundary first.

Current relevant state (frontend repo):
- `@bufbuild/protobuf@^1.10.1`, `@connectrpc/connect@^1.7`, `@connectrpc/connect-web@^1.7`, `@buf/*_es` v1 BSR builds.
- Generated `@buf/*` types are imported by 12 files: 10 inside `adapter/rpc/{client,mapper}` (intended boundary) and 2 outside it (`services/ticket-email-service.ts`, `routes/import-ticket-email/import-ticket-email-route.ts`) — a layering violation.
- No app code calls `toBinary`/`fromBinary`/`toJson`/`fromJson` directly (0 sites); (de)serialization happens inside the Connect-Web transport.
- Mixed Connect client-factory usage already exists: 2 files use v1's `createPromiseClient` (`artist-client`, `follow-client`), 5 use `createClient` (`concert-client`, `push-client`, `ticket-journey-client`, `user-client`, `services/ticket-email-service`) — 7 client-factory files total, a subset of the 12 `@buf/*`-importing files.
- BSR publishes v2.14.x `bufbuild_es` builds of our schema, keyed per commit; upstream `@connectrpc/connect{,-web}` is at v2.

## Goals / Non-Goals

**Goals:**
- Every `@buf/*` generated-type import is confined to `adapter/rpc/{client,mapper}` before the upgrade.
- Frontend runs protobuf-es v2 + Connect-ES v2 with no user-facing behavior change.
- Eliminate the recurring manual "pin back to the v1 build" step on schema bumps.

**Non-Goals:**
- No backend change (Go uses a different protobuf implementation).
- No `.proto` schema change; wire format and RPC contracts are untouched.
- Not committing to binary transport in this change — JSON stays the default; whether to enable `useBinaryFormat` (which is where the binary-path speedups would apply) is measured and decided separately (see D5), not assumed.
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

### D2.1 — Phase 1 scope also covers lottery-application (discovered during apply)

Since this change was drafted, the `lottery-application` and `identity-verification`
features shipped, adding new generated-type leaks outside the adapter boundary that
the original two-file estimate (`ticket-email-service`, `import-ticket-email-route`)
did not anticipate. To keep task 1.7's invariant ("no `@buf/*` import outside
`adapter/rpc/{client,mapper}`") actually satisfiable, Phase 1 now also isolates the
lottery path:
- `entities/lottery.ts` — domain `TicketApplication` + `TicketApplicationState`
  union (+ `ApplicantIdentity` value), so the route stops importing the proto enum.
- `adapter/rpc/mapper/lottery-mapper.ts` — proto ⇄ entity.
- `adapter/rpc/client/lottery-client.ts` returns the domain `TicketApplication`
  (was returning the proto message); `routes/lottery-application/*` (route + spec)
  consume the domain union. `lottery-apply-route` already ignores `apply()`'s
  return, so widening the client to domain types does not touch it.

*Note on the import-ticket-email route's Concert dependency:* the route's template
reads the **proto** `Concert` shape (`concert.series.title.value`,
`concert.localDate?.value`) and `IConcertStore.listConcerts` returns `ProtoConcert`,
so the flattened domain `entities/concert.ts` `Concert` is the wrong shape here.
Rather than build a new proto→domain Concert mapper (out of scope), the route
imports the `ProtoConcert` type **re-exported by `adapter/rpc/client/concert-client.ts`**.
That removes the direct `@buf/*` import (satisfying task 1.7) while keeping the
proto shape the template needs — the type crosses the boundary through the adapter,
not straight from `@buf/*`.

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

Field access on messages is largely unchanged; the churn is construction (`new X` → `create(XSchema, …)`) and imports (`X` → `XSchema`).

**Refinements found during Phase 2 implementation:**
- **Scope was larger than "~23 sites in `adapter/rpc`".** Since the change was
  drafted, the `admin/` and `organizer/` apps (each its own Vite entry, consuming
  generated types *directly*, not via the `src/adapter/rpc` boundary) and their
  `test/` fixtures shipped. The v2 dependency bump is repo-wide, so they had to
  migrate too — not optional. Final surface: `src/adapter/rpc/*`, all of `admin/`
  and `organizer/` services/routes, plus 8 `test/**` fixture files. `src`+`admin`
  are covered by `tsc` (tsconfig `include`); `organizer` is not in `tsc` but is
  built by `vite build` (3 entries) and its fixtures run under Vitest — so the
  build + unit suite are the real green gate for it.
- **Request construction uses plain init, not `create()`.** For a message passed
  *as a client method argument or a nested field*, v2 accepts the plain init
  object directly, so `new EventId({ value: id })` became `{ value: id }` (not
  `create(EventIdSchema, …)`) — fewer imports, idiomatic v2. `create(XSchema, …)`
  is used only where a *standalone* message value is needed (test fixtures, the
  organizer draft marshallers).
- **Well-known `Timestamp` lost its methods.** v1 `ts.toDate()` /
  `Timestamp.fromDate(d)` → v2 `timestampDate(ts)` / `timestampFromDate(d)` from
  `@bufbuild/protobuf/wkt`. This hit `ticket-email-mapper` and several admin/
  organizer date formatters/fixtures. Enums are unchanged (still TS `enum`).

### D4 — BSR pin strategy on v2

Repin `@buf/*bufbuild_es` to the v2 build at the current schema commit, and **drop** `@buf/*connectrpc_es`: Connect-ES v2 removes the separate connect codegen (see D3), so service definitions come from the `bufbuild_es` `*_pb.js` output and there is no v2 `connectrpc_es` build to pin to. Keeping the v1 `connectrpc_es` pin would drag in its `@connectrpc/connect@^1` peer and reintroduce the exact ERESOLVE conflict this migration removes. Update `.npmrc`/docs so future bumps stay on the v2 major (v2 becomes the default expectation; `@latest` no longer conflicts once the app is `@bufbuild/protobuf@^2`).

**Pins applied (reproducible):** `@buf/liverty-music_schema.bufbuild_es` →
`2.14.1-20260902095528-98cf6c870a23.3` (v2 build at the *same* schema commit
`98cf6c870a23` as the outgoing v1 pin `1.10.0-…`); `@bufbuild/protobuf` `^1`→`^2`
(resolved 2.14.1), `@connectrpc/connect` and `@connectrpc/connect-web` `^1`→`^2`;
`@buf/*connectrpc_es` removed. `package-lock.json` was regenerated from scratch
(a plain `npm install` kept the stale `connectrpc_es` lock entry and its
`bufbuild_es@1` peer, which reproduced the ERESOLVE — deleting the lock +
`node_modules` and reinstalling resolved cleanly). `.npmrc` needed no change (it
only sets the BSR registry). The frontend `AGENTS.md` "Consuming New Proto Types"
section was rewritten for the v2 major (install `bufbuild_es@latest`, no v1-pin
dance) plus a v2 codegen-conventions block.

### D5 — Evaluate switching the browser transport to binary format (measure, then decide)

The transport (`createConnectTransport` in `services/grpc-transport.ts`) currently runs without `useBinaryFormat`, so the browser uses JSON — the default, chosen for DevTools readability. The Connect protocol also supports binary (protobuf) encoding, toggled by `useBinaryFormat: true` (or by switching to `createGrpcWebTransport`, which is always binary). Connect-Go negotiates encoding from the request Content-Type, so **no backend change is required** either way.

Binary is where protobuf-es v2.14's headline gains actually land: `toBinary` up to 5× / `fromBinary` up to 2× (JSON paths are 2–3×), plus a smaller wire payload (varint, no field names) that helps most on slow mobile networks. This is the natural pairing with the v2 upgrade.

Decision: **do not hard-code binary in this change.** Keep JSON as the default through Phase 2, then in the verification phase measure JSON vs. binary on *compressed* wire size (gzip/brotli narrows the raw-byte gap) and on (de)serialize timing, and flip `useBinaryFormat` only if the data justifies it. Deciding by measurement avoids trading away DevTools observability for a win that HTTP compression may have already captured.

**Measured outcome (Phase 2 verification — keep JSON).** Measured against the
public, no-cost `ConcertService.ListByLocation` RPC (prod, a representative ~39 KB
JSON list response of real data), comparing the two encodings of the *same*
response:

| encoding | raw | gzip | brotli | decode (incl. `JSON.parse`) |
|---|---|---|---|---|
| JSON | 39,234 B | 6,986 B | 5,649 B | 640 µs/op |
| binary | 20,442 B | 7,105 B | 6,015 B | 287 µs/op |

Binary is 47.9 % smaller **raw**, but after HTTP compression it is **1.7 % larger
gzipped and 6.5 % larger brotli'd** — JSON's repetitive field names compress away,
while protobuf's already-dense varints have higher entropy and compress less. The
raw-size advantage inverts under the compression every production response already
uses. Binary decodes ~2.2× faster, but the absolute saving is sub-millisecond
(~0.35 ms per response, off the interaction critical path). Since the compressed
wire size is a (small) regression and the decode win is negligible in absolute
terms, the data does **not** justify losing DevTools network-tab readability.
**Final decision: keep JSON (`useBinaryFormat` stays off).** This confirms the
hypothesis that HTTP compression already captured the payload win. Task 5.4 (the
interceptor/E2E re-check that a flip would require) is therefore not applicable and
is deliberately skipped.

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
