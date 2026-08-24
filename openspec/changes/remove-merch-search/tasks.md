## 1. cloud-provisioning — stop the workload first

- [ ] 1.1 Delete the CronJob dirs `k8s/namespaces/backend/{base,overlays/dev,overlays/prod}/cronjob/merch-discovery/`
- [ ] 1.2 Remove `- cronjob/merch-discovery` from `base/kustomization.yaml` and the merch entries from `overlays/dev/kustomization.yaml` (schedule patch + `merch-discovery-job-config` generator) and `overlays/prod/kustomization.yaml` (config generator + images pin lines)
- [ ] 1.3 Remove the `Merch Discovery` workload entry from `src/gcp/components/monitoring.ts` (drops the `alert-error-log-merch-discovery` AlertPolicy)
- [ ] 1.4 Remove `merch-discovery` from the `IMAGES` list in `.github/workflows/bump-prod-pin.yml`
- [ ] 1.5 Deploy: dev ArgoCD/Pulumi sync + prod `pulumi up` (AlertPolicy deletion) and ArgoCD sync; confirm no merch-discovery CronJob remains and nothing repopulates `merch_url`

## 2. specification — proto + BSR release

- [ ] 2.1 In `proto/liverty_music/entity/v1/series.proto` delete `Url merch_url = 5;` and add `reserved 5; reserved "merch_url";`; remove its doc comment
- [ ] 2.2 Run `buf lint` + `buf breaking`; if `FIELD_NO_DELETE` still flags despite the reserve, add the `buf skip breaking` PR label
- [ ] 2.3 Delete the tombstoned merch scenarios from the main specs on archive: `event-management` (`Series owns the merch URL`, `Merch URL is optional`) and `app-error-log-alerting` (`Merch-discovery CronJob emits an ERROR log`); sync all delta specs into `openspec/specs/`
- [ ] 2.4 Merge the specification PR, cut a GitHub Release (tag `vX.Y.Z`), and watch `buf-release.yml` until BSR gen succeeds

## 3. backend — code + DB column

- [ ] 3.1 Delete whole files: `cmd/job/merch-discovery/`, `internal/di/merch_discovery_job.go`, `internal/usecase/merch_uc.go`(+`_test.go`), `internal/infrastructure/gcp/gemini/merch_searcher.go`(+`_test.go`, `_integration_test.go`), `internal/infrastructure/gcp/gemini/grounding_probe_integration_test.go`, `internal/infrastructure/httpx/liveness.go`, `internal/infrastructure/database/rdb/series_merch_repo_test.go`, and mocks `mock_MerchSearcher.go`, `mock_MerchLivenessChecker.go`, `mock_MerchDiscoveryUseCase.go`
- [ ] 3.2 Edit `internal/entity/series.go`: remove `Series.MerchURL`, `MerchCandidate`, the `MerchSearcher`/`MerchLivenessChecker` interfaces, and the `ListSeriesInMerchWindow`/`SetMerchURL`/`ClearMerchURL` methods from `SeriesRepository`
- [ ] 3.3 Edit `internal/infrastructure/database/rdb/series_repo.go` and `concert_repo.go`: drop `merch_url` from all INSERT/SELECT queries (8 SELECTs in concert_repo), scan vars, and the merch-window/set/clear methods
- [ ] 3.4 Edit `internal/adapter/rpc/mapper/concert.go`: remove the `proto.MerchUrl` emit; fix `concert_test.go` and `concert_creation_uc_test.go` (fakeSeriesRepo stubs) and `export_test.go`
- [ ] 3.5 Edit `pkg/config/config.go`(+`_test.go`): remove `GeminiMerchModel`/`GeminiMerchThinkingLevel`/`MerchDiscoveryWindow` fields, defaults, accessors, and `Validate()` checks; remove merch entries from `.mockery.yml`, `Dockerfile`, `.github/workflows/deploy.yml`
- [ ] 3.6 Add forward Atlas migration `ALTER TABLE series DROP COLUMN merch_url` (via `atlas migrate diff --env local drop_merch_url_from_series`), remove `merch_url` from `schema/schema.sql`, add the file to `k8s/atlas/base/kustomization.yaml`, run `atlas migrate hash`; do NOT edit historical migrations
- [ ] 3.7 Upgrade to the new BSR types (`go get ...@vX.Y.Z`), run `mockery`, then `make check` (build + lint + tests green)
- [ ] 3.8 Merge/deploy so the read-path removal and `DROP COLUMN` land together

## 4. frontend — UI cleanup

- [ ] 4.1 Upgrade the generated schema package to the released version
- [ ] 4.2 Remove merch usages: `services/concert-store.ts` mapping, `entities/concert.ts` field, `components/live-highway/event-detail-utils.ts` (`eventHasMerchUrl`), `event-detail-sheet.ts`/`.html` (`hasMerchUrl` getter + `merch-link`), `routes/welcome/welcome-route.ts` demo factory, and the `concert-highway.spec.ts` fixture
- [ ] 4.3 Remove the `eventDetail.viewMerch` keys from `locales/{en,ja}/translation.json` and reconcile the `sheetHint` copy; run the frontend build + tests

## 5. Verification

- [ ] 5.1 Confirm no `merch` references remain across the four repos (`grep -ri merch`), excluding the archived OpenSpec change
- [ ] 5.2 Confirm prod: no merch-discovery CronJob, no merch AlertPolicy, `series.merch_url` column dropped, fan concert-detail renders without a merch link
- [ ] 5.3 Archive the OpenSpec change once all PRs are merged and released
