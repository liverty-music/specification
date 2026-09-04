## 1. Phase 1 — Isolate the RPC adapter boundary (still on v1, non-breaking)

- [ ] 1.1 Add `entities/ticket-email.ts`: domain `TicketEmail` type + TS-union equivalents for `TicketEmailType` and the journey-status values consumed by the ticket-email path
- [ ] 1.2 Add `adapter/rpc/mapper/ticket-email-mapper.ts` (proto ⇄ entity), following `ticket-journey-mapper.ts`/`artist-mapper.ts`
- [ ] 1.3 Add `adapter/rpc/client/ticket-email-client.ts` owning the Connect client + generated request types; expose an interface returning domain entities
- [ ] 1.4 Refactor `services/ticket-email-service.ts` to delegate to the new client and drop all `@buf/*` imports (keep its public interface stable)
- [ ] 1.5 Refactor `routes/import-ticket-email/import-ticket-email-route.ts` to consume `entities/concert.ts`, `entities/ticket-email.ts`, and the domain journey-status union instead of proto types
- [ ] 1.6 Add/extend mapper unit tests asserting entity output for representative ticket-email fixtures (baseline before the upgrade)
- [ ] 1.7 Verify no `@buf/*` import exists outside `adapter/rpc/{client,mapper}` (`grep -rlE "from ['\"]@buf" src` → only adapter/rpc paths)
- [ ] 1.8 `npm run` lint + unit tests + build green; open Phase 1 PR and land it with E2E/Visual green

## 2. Phase 2 — Dependency bump to v2 (BREAKING)

- [ ] 2.1 Find the v2 (`2.14.x-…`) BSR build string for `@buf/liverty-music_schema.bufbuild_es` at the current schema commit (`npm view … versions --json`). Note: there is NO v2 `connectrpc_es` build — it is dropped in 2.2, not repinned.
- [ ] 2.2 Update `package.json`: repin `@buf/*bufbuild_es` → v2, **remove** `@buf/*connectrpc_es` (service defs now come from `bufbuild_es` `*_pb.js`), `@bufbuild/protobuf` → `^2`, `@connectrpc/connect` → `^2`, `@connectrpc/connect-web` → `^2`; regenerate `package-lock.json`
- [ ] 2.3 Update `.npmrc`/AGENTS.md/CLAUDE.md BSR-pin guidance so future schema bumps stay on the v2 major (remove the manual v1-pin workaround note)
- [ ] 2.4 Resolve `npm install` with no ERESOLVE peer conflicts (confirms the v1-pin dance is gone)

## 3. Phase 2 — Generated-API migration (adapter/rpc only)

- [ ] 3.1 Migrate ONE client end-to-end first (ticket-journey): imports `X` → `XSchema`, `new X({…})` → `create(XSchema, {…})`, `createPromiseClient` → `createClient`, service import path per connect-es v2
- [ ] 3.2 Confirm the pilot client compiles and round-trips an RPC (dev/local) before fanning out
- [ ] 3.3 Migrate remaining `adapter/rpc/client/*` (artist, concert, follow, push, user, ticket-email): construction + client-factory + service imports
- [ ] 3.4 Migrate remaining `adapter/rpc/mapper/*`: proto type imports and any enum value access to v2 shape
- [ ] 3.5 Replace all remaining `createPromiseClient` usages with `createClient` (2 files: `artist-client`, `follow-client`)
- [ ] 3.6 Grep for stray v1 patterns: no `new [A-Z]…Request/Response/Id(` construction of generated types, no `createPromiseClient`, no `*_service_connect.js` imports left behind

## 4. Phase 2 — Verification

- [ ] 4.1 Full Vite build green, including the `date-impl` alias and build-template/smoke checks
- [ ] 4.2 Unit tests green; mapper tests from 1.6 still assert identical entity output (no enum/representation drift)
- [ ] 4.3 E2E/Visual green across all RPC paths (artist, concert, follow, push, user, ticket-journey, ticket-email)
- [ ] 4.4 Record before/after gzipped bundle size (and optionally an INP sample) to confirm the ~5% reduction
- [ ] 4.5 Open Phase 2 PR; merge once CI + E2E/Visual are green

## 5. Phase 2 (optional) — Binary transport evaluation (D5)

- [ ] 5.1 Measure representative RPCs with JSON transport (current): compressed (gzip/brotli) response size + `fromJson` decode timing
- [ ] 5.2 Measure the same RPCs with `useBinaryFormat: true` in `services/grpc-transport.ts`: compressed size + `fromBinary` decode timing (backend needs no change — Connect-Go negotiates from Content-Type)
- [ ] 5.3 Decide: flip `useBinaryFormat` on only if the compressed-size / decode-time gain justifies losing DevTools network readability; record the decision and numbers in the change
- [ ] 5.4 If flipping, confirm interceptors (auth/logging/OTEL) and error handling still behave, and E2E/Visual stay green

## 6. Close-out

- [ ] 6.1 Sync any doc updates (BSR pin workflow) and confirm no `@buf/*` leaks reintroduced
- [ ] 6.2 Verify implementation matches the design, then archive the change
