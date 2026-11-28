## 1. specification: proto (design D1, D2, D3)

- [ ] 1.1 Add `proto/liverty_music/rpc/admin/official_site/v1/official_site_service.proto` (`OfficialSiteService` with `Create` and `Update`, each taking `artist_id` and `url` with the same validation rules as the fan service) and remove `proto/liverty_music/rpc/official_site/v1`; open the PR citing `OpenSpec-Change: restrict-official-site-to-admins` with the `buf skip breaking` label, merge it, cut the Release and verify the BSR generation workflow succeeded

## 2. backend: usecase and admin boundary (components/usecase/official-site/update, components/adapter/admin/api/rpc/official-site)

- [ ] 2.1 Add `OfficialSiteUseCase.Update` calling `Artist.UpdateOfficialSiteURL`; verify one unit test per scenario of `components/usecase/official-site/update`, annotated with `@spec`
- [ ] 2.2 Replace the fan `OfficialSiteHandler` with an admin handler of `Create` and `Update`, move its registration from `fanHandlers` to `adminHandlers` of `internal/di/api_wiring.go`, and upgrade the generated proto package; verify one handler test per scenario of `components/adapter/admin/api/rpc/official-site` (including that the role gate rejects a non-admin and a guest through the admin server), annotated with `@spec`, and that `grep` finds no use of the removed fan package

## 3. backend: release and production check

- [ ] 3.1 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: the rollout finished and fan-api logs no request to `liverty_music.rpc.official_site.v1`
