## Why

`OfficialSiteService.Create` on the fan boundary accepts any signed-in fan (backend#919). It sets the official site of an artist that has none, and no call can change or delete it afterwards. The concert search reads that URL as the artist's own page, so one fan's input decides what the search finds for that artist. Only Liverty Music staff should set it, and staff must be able to correct a wrong one.

## What Changes

- Add `liverty_music.rpc.admin.official_site.v1.OfficialSiteService` with `Create` (artist id and URL) and `Update` (artist id and the corrected URL). It is served by the admin server behind the admin-role gate, like every admin service.
- **BREAKING**: remove `liverty_music.rpc.official_site.v1` (the fan `OfficialSiteService` with `Create` and the unimplemented `Delete`). No fan or organizer client calls it: the frontend and cloud-provisioning have no reference to it.
- Add `OfficialSiteUseCase.Update`, a thin call to the existing `Artist.UpdateOfficialSiteURL`.
- Stop registering the official site handler on the fan server; register an admin handler on the admin server.
- The reserved `Delete` is not carried over: no requirement reads it.

## Capabilities

### New Capabilities

- `components/adapter/admin/api/rpc/official-site`: the admin boundary of the official site calls: the admin role, request validation, Create and Update.
- `components/usecase/official-site/update`: replaces the URL of an artist's stored official site.

### Modified Capabilities

- `components/adapter/fan/api/rpc/official-site`: every requirement is removed, because the fan boundary no longer serves official site calls.

The usecase `components/usecase/official-site/create` and the entity operations `Artist.CreateOfficialSite` and `Artist.UpdateOfficialSiteURL` are unchanged: Create and Update only move to another caller.

## Impact

- specification: new proto package `rpc/admin/official_site/v1`, removal of `rpc/official_site/v1` (the PR carries the `buf skip breaking` label), one proto Release.
- backend: `internal/adapter/rpc/official_site_handler.go` becomes an admin handler, `internal/di/api_wiring.go` moves its registration from `fanHandlers` to `adminHandlers`, `OfficialSiteUseCase` gains `Update`.
- frontend and cloud-provisioning: no change.
