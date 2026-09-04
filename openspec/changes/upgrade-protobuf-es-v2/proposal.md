## Why

The frontend is pinned to protobuf-es **v1** (`@bufbuild/protobuf@^1`) and Connect-ES **v1**, while BSR already publishes protobuf-es **v2.14** builds of our schema. Every schema bump has to be manually pinned back to the v1 plugin build (BSR's `@latest` resolves to the v2 build and breaks `npm install` with an ERESOLVE peer conflict) — a recurring, error-prone tax. Staying on v1 also forgoes v2.14's serialization/bundle improvements and, more importantly, the migration cost only grows the longer the gap widens. Doing it now, while the protobuf surface is still small and cleanly isolable, is the cheapest this migration will ever be.

## What Changes

This change is executed in two phases inside a single change.

**Phase 1 — Isolate the RPC adapter boundary (non-breaking, still on v1)**
- Introduce a domain `entities/ticket-email.ts` type (plus TS-union equivalents for the email-type/journey-status enums) so no consumer depends on generated proto types.
- Add `adapter/rpc/client/ticket-email-client.ts` and `adapter/rpc/mapper/ticket-email-mapper.ts`, mirroring the existing ticket-journey client/mapper pattern.
- Refactor `services/ticket-email-service.ts` to delegate to the new adapter client and stop importing `@buf/*` generated types.
- Refactor `routes/import-ticket-email/import-ticket-email-route.ts` to consume `entities/*` domain types instead of proto `Concert` / `TicketEmail` / `TicketJourneyStatus`.
- Result: `@buf/*` generated-type imports stay confined to `adapter/rpc/{client,mapper}` with 0 leaks outside the adapter layer. (File count is net-neutral: Phase 1 removes 2 `@buf/*`-importing files outside the boundary and adds 2 new ones inside it — 12 files before, 12 after, all within `adapter/rpc`.)

**Phase 2 — Upgrade protobuf-es / Connect-ES v1 → v2 (**BREAKING**)**
- Repin `@buf/liverty-music_schema.bufbuild_es` to its v2 (`2.14.x-…`) BSR build and **drop** `@buf/liverty-music_schema.connectrpc_es` entirely (Connect-ES v2 folds the connect codegen into `protoc-gen-es` v2, so there is no v2 `connectrpc_es` build to pin to — service definitions come from the `bufbuild_es` `*_pb.js` output); bump `@bufbuild/protobuf` to `^2`, `@connectrpc/connect` and `@connectrpc/connect-web` to `^2`. **BREAKING** (dependency majors).
- Migrate message construction from class-based `new Msg({…})` to schema-based `create(MsgSchema, {…})` (~23 sites, all within `adapter/rpc`). **BREAKING** (generated API).
- Replace `createPromiseClient` with `createClient` (2 files: artist, follow).
- Adjust Connect-ES v2 service-definition imports (the separate connect-es codegen is folded into `protoc-gen-es` v2 output in v2).
- Revisit the BSR pin/`@latest` workflow and documentation now that the app is on the v2 major, removing the manual v1-pin dance.
- Verify Vite build (including the `date-impl` alias) and all RPC paths via CI + E2E/Visual.

## Capabilities

### New Capabilities
<!-- None. This change introduces no new product capability; it is a frontend refactor + dependency upgrade with no spec-level behavior change. -->

### Modified Capabilities
<!-- None. Protobuf schema, RPC contracts, and wire behavior are unchanged. This change opts out of specs via `skip_specs: true`. -->

## Impact

- **Scope**: Frontend repository only. Backend (Go `google.golang.org/protobuf`) is a different implementation and is unaffected. Protobuf `.proto` schema is unchanged.
- **Dependencies**: `@bufbuild/protobuf` ^1→^2, `@connectrpc/connect` ^1→^2, `@connectrpc/connect-web` ^1→^2, `@buf/*bufbuild_es` v1→v2 BSR build, and `@buf/*connectrpc_es` removed (no v2 equivalent — see Phase 2).
- **Code**: New files `entities/ticket-email.ts`, `adapter/rpc/client/ticket-email-client.ts`, `adapter/rpc/mapper/ticket-email-mapper.ts`; modified `services/ticket-email-service.ts`, `routes/import-ticket-email/import-ticket-email-route.ts`, plus all files under `adapter/rpc/{client,mapper}` for the API migration; `package.json`, `package-lock.json`, `.npmrc`/BSR pin docs.
- **Runtime**: No manual `toBinary`/`fromBinary`/`toJson` calls exist in app code — v2.14's serialization gains accrue automatically inside the Connect-Web transport. Because Connect-Web uses JSON transport in browsers by default, the material wins are JSON parse/serialize and the ~5% bundle-size reduction, not the binary-path speedups.
- **Risk**: Breaking dependency and generated-API migration, but the blast radius is confined to `adapter/rpc` after Phase 1. No user-facing behavior change intended; regressions would surface as RPC (de)serialization failures, caught by E2E/Visual.
