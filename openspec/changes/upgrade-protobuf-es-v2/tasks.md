## 1. Phase 1 — Isolate the RPC adapter boundary (still on v1, non-breaking)

- [x] 1.1 Add `entities/ticket-email.ts`: domain `TicketEmail` type + TS-union equivalents for `TicketEmailType` and the journey-status values consumed by the ticket-email path
- [x] 1.2 Add `adapter/rpc/mapper/ticket-email-mapper.ts` (proto ⇄ entity), following `ticket-journey-mapper.ts`/`artist-mapper.ts`
- [x] 1.3 Add `adapter/rpc/client/ticket-email-client.ts` owning the Connect client + generated request types; expose an interface returning domain entities
- [x] 1.4 Refactor `services/ticket-email-service.ts` to delegate to the new client and drop all `@buf/*` imports (keep its public interface stable)
- [x] 1.5 Refactor `routes/import-ticket-email/import-ticket-email-route.ts` (+ its `.html`) to consume `entities/ticket-email.ts`, the domain journey-status union, and the `ProtoConcert` type re-exported by `adapter/rpc/client/concert-client.ts` (the template needs the proto Concert shape; the flattened domain `entities/concert.ts` Concert does not fit — see design D2.1) instead of direct `@buf/*` imports
- [x] 1.5.1 Add `entities/lottery.ts`: domain `TicketApplication` + `TicketApplicationState` union (+ `ApplicantIdentity`) — see design D2.1
- [x] 1.5.2 Add `adapter/rpc/mapper/lottery-mapper.ts` (proto ⇄ entity); widen `adapter/rpc/client/lottery-client.ts` to return the domain `TicketApplication`
- [x] 1.5.3 Refactor `routes/lottery-application/lottery-application-route.ts` (+ its `.spec.ts`) to consume the domain `TicketApplicationState` union instead of the proto enum
- [x] 1.6 Add/extend mapper unit tests asserting entity output for representative ticket-email AND lottery fixtures (baseline before the upgrade)
- [x] 1.7 Verify no `@buf/*` import exists outside `adapter/rpc/{client,mapper}` (`grep -rlE "from ['\"]@buf" src` → only adapter/rpc paths)
- [x] 1.8 `npm run` lint + unit tests + build green; open Phase 1 PR and land it with E2E/Visual green

## 2. Phase 2 — Dependency bump to v2 (BREAKING)

- [x] 2.1 Find the v2 (`2.14.x-…`) BSR build string for `@buf/liverty-music_schema.bufbuild_es` at the current schema commit (`npm view … versions --json`). Note: there is NO v2 `connectrpc_es` build — it is dropped in 2.2, not repinned.
- [x] 2.2 Update `package.json`: repin `@buf/*bufbuild_es` → v2, **remove** `@buf/*connectrpc_es` (service defs now come from `bufbuild_es` `*_pb.js`), `@bufbuild/protobuf` → `^2`, `@connectrpc/connect` → `^2`, `@connectrpc/connect-web` → `^2`; regenerate `package-lock.json`
- [x] 2.3 Update `.npmrc`/AGENTS.md/CLAUDE.md BSR-pin guidance so future schema bumps stay on the v2 major (remove the manual v1-pin workaround note)
- [x] 2.4 Resolve `npm install` with no ERESOLVE peer conflicts (confirms the v1-pin dance is gone)

## 3. Phase 2 — Generated-API migration (repo-wide: adapter/rpc + admin + organizer + test — see design D3 scope note)

- [x] 3.1 Migrate ONE client end-to-end first (ticket-journey): imports `X` → `XSchema`, `new X({…})` → `create(XSchema, {…})`, `createPromiseClient` → `createClient`, service import path per connect-es v2
- [x] 3.2 Confirm the pilot client compiles and round-trips an RPC (dev/local) before fanning out
- [x] 3.3 Migrate remaining `adapter/rpc/client/*` (artist, concert, follow, push, user, ticket-email): construction + client-factory + service imports
- [x] 3.4 Migrate remaining `adapter/rpc/mapper/*`: proto type imports and any enum value access to v2 shape
- [x] 3.5 Replace all remaining `createPromiseClient` usages with `createClient` (2 files: `artist-client`, `follow-client`)
- [x] 3.6 Grep for stray v1 patterns: no `new [A-Z]…Request/Response/Id(` construction of generated types, no `createPromiseClient`, no `*_service_connect.js` imports left behind
- [x] 3.7 Migrate the `admin/` app (its own Vite entry, consumes generated types directly): `admin/services/*` clients (service imports + construction) and `admin/**` route date formatters (`.toDate()` → `timestampDate`) — see design D3 scope note
- [x] 3.8 Migrate the `organizer/` app (own Vite entry; NOT in `tsc` include, covered by `vite build` + Vitest): `organizer/services/*` clients + draft marshallers (`create(XSchema)` / `timestampFromDate`) and `organizer/**` route date formatters
- [x] 3.9 Migrate `test/**` fixtures that construct proto messages (`new X({…})` → `create(XSchema, {…})`, `Timestamp.fromDate`/`toDate` → wkt helpers): 6 admin/organizer route+service specs

## 4. Phase 2 — Verification

- [x] 4.1 Full Vite build green, including the `date-impl` alias and build-template/smoke checks
- [x] 4.2 Unit tests green; mapper tests from 1.6 still assert identical entity output (no enum/representation drift)
- [x] 4.3 E2E/Visual green across all RPC paths (artist, concert, follow, push, user, ticket-journey, ticket-email) — full CI (E2E/Smoke/Storybook-visual/review) green on the Phase 2 PR before merge
- [ ] 4.4 Record before/after gzipped bundle size (and optionally an INP sample) to confirm the ~5% reduction — v2 build (fan-web `main`) is **139 KB gzip**; capture the pre-merge v1 `main` gzip from CI to compute the delta
- [x] 4.5 Open Phase 2 PR; merge once CI + E2E/Visual are green — frontend Phase 2 PR merged (green CI); spec design/tasks updated via the paired specification PR

## 5. Phase 2 (optional) — Binary transport evaluation (D5)

- [x] 5.1 Measure representative RPCs with JSON transport (current): compressed (gzip/brotli) response size + `fromJson` decode timing — public no-cost `ConcertService.ListByLocation` (prod, ~39 KB): gzip 6,986 B / brotli 5,649 B / 640 µs decode
- [x] 5.2 Measure the same RPCs with binary encoding: compressed size + `fromBinary` decode timing (measured by encoding the same RPC both ways against the live endpoint; backend needs no change — Connect-Go negotiates from Content-Type): gzip 7,105 B / brotli 6,015 B / 287 µs decode
- [x] 5.3 Decide: **keep JSON** — binary is 47.9% smaller raw but 1.7% (gzip) / 6.5% (brotli) LARGER compressed, and the 2.2× decode win is sub-ms; not worth losing DevTools readability. Numbers + decision recorded in design D5
- [x] 5.4 N/A — not flipping (see D5), so no interceptor/error/E2E re-check for a binary switch is required (deliberate conditional skip)

## 6. Close-out

- [ ] 6.1 Sync any doc updates (BSR pin workflow) and confirm no `@buf/*` leaks reintroduced
- [ ] 6.2 Verify implementation matches the design, then archive the change
