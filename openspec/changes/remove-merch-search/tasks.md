## 1. cloud-provisioning — stop the workload first

- [x] 1.1 Delete the CronJob dirs `k8s/namespaces/backend/{base,overlays/dev,overlays/prod}/cronjob/merch-discovery/`
- [x] 1.2 Remove `- cronjob/merch-discovery` from `base/kustomization.yaml` and the merch entries from `overlays/dev/kustomization.yaml` (schedule patch + `merch-discovery-job-config` generator) and `overlays/prod/kustomization.yaml` (config generator + images pin lines)
- [x] 1.3 Remove the `Merch Discovery` workload entry from `src/gcp/components/monitoring.ts` (drops the `alert-error-log-merch-discovery` AlertPolicy)
- [x] 1.4 Remove `merch-discovery` from the `IMAGES` list in `.github/workflows/bump-prod-pin.yml`
- [ ] 1.5 Deploy: dev ArgoCD/Pulumi sync + prod `pulumi up` (AlertPolicy deletion) and ArgoCD sync; confirm no merch-discovery CronJob remains and nothing repopulates `merch_url`

## 2. specification — proto + BSR release

- [x] 2.1 In `proto/liverty_music/entity/v1/series.proto` delete `Url merch_url = 5;` and add `reserved 5; reserved "merch_url";`; remove its doc comment
- [x] 2.2 Run `buf lint` + `buf breaking`; if `FIELD_NO_DELETE` still flags despite the reserve, add the `buf skip breaking` PR label
- [ ] 2.3 Merge the specification PR, cut a GitHub Release (tag `vX.Y.Z`), and watch `buf-release.yml` until BSR gen succeeds (spec-sync + tombstone deletion happen at archive — see section 6)

## 3. backend release A — remove code and read/write path (column stays)

- [ ] 3.1 Delete whole files: `cmd/job/merch-discovery/`, `internal/di/merch_discovery_job.go`, `internal/usecase/merch_uc.go`(+`_test.go`), `internal/infrastructure/gcp/gemini/merch_searcher.go`(+`_test.go`, `_integration_test.go`), `internal/infrastructure/gcp/gemini/grounding_probe_integration_test.go`, `internal/infrastructure/httpx/liveness.go`, `internal/infrastructure/database/rdb/series_merch_repo_test.go`, and mocks `mock_MerchSearcher.go`, `mock_MerchLivenessChecker.go`, `mock_MerchDiscoveryUseCase.go`
- [ ] 3.2 Edit `internal/entity/series.go`: remove `Series.MerchURL`, `MerchCandidate`, the `MerchSearcher`/`MerchLivenessChecker` interfaces, and the `ListSeriesInMerchWindow`/`SetMerchURL`/`ClearMerchURL` methods from `SeriesRepository`
- [ ] 3.3 Edit `internal/infrastructure/database/rdb/series_repo.go` and `concert_repo.go`: stop reading/writing `merch_url` — drop it from all INSERT/SELECT queries (8 SELECTs in concert_repo), scan vars, and remove the merch-window/set/clear methods. The `series.merch_url` **column stays** in this release.
- [ ] 3.4 Edit `internal/adapter/rpc/mapper/concert.go`: remove the `proto.MerchUrl` emit; fix `concert_test.go` and `concert_creation_uc_test.go` (fakeSeriesRepo stubs) and `export_test.go`
- [ ] 3.5 Edit `pkg/config/config.go`(+`_test.go`): remove `GeminiMerchModel`/`GeminiMerchThinkingLevel`/`MerchDiscoveryWindow` fields, defaults, accessors, and `Validate()` checks; remove merch entries from `.mockery.yml`, `Dockerfile`, `.github/workflows/deploy.yml`
- [ ] 3.6 Upgrade to the new BSR types (`go get ...@vX.Y.Z`), run `mockery`, then `make check` (build + lint + tests green)
- [ ] 3.7 Merge and deploy release A; confirm the fleet has fully rolled over (no pod still SELECTs `merch_url`) before section 5

## 4. frontend — UI cleanup

- [ ] 4.1 Upgrade the generated schema package to the released version
- [ ] 4.2 Remove merch usages: `services/concert-store.ts` mapping, `entities/concert.ts` field, `components/live-highway/event-detail-utils.ts` (`eventHasMerchUrl`), `event-detail-sheet.ts`/`.html` (`hasMerchUrl` getter + `merch-link`), `routes/welcome/welcome-route.ts` demo factory, and the `concert-highway.spec.ts` fixture
- [ ] 4.3 Remove the `eventDetail.viewMerch` keys from `locales/{en,ja}/translation.json` and reconcile the `sheetHint` copy; run the frontend build + tests

## 5. backend release B — drop the column (expand/contract)

- [ ] 5.1 Only after release A (§3) is fully rolled out and no pod reads `merch_url`: add a forward Atlas migration `ALTER TABLE series DROP COLUMN merch_url` (via `atlas migrate diff --env local drop_merch_url_from_series`), remove `merch_url` from `schema/schema.sql`, add the file to `k8s/atlas/base/kustomization.yaml`, run `atlas migrate hash`; do NOT edit historical migrations
- [ ] 5.2 Merge and deploy release B; the Atlas operator applies the drop ahead of the (unchanged) Deployment

## 6. Finalize & verify

- [ ] 6.1 On archive, delete the tombstoned merch scenarios from the main specs — `event-management` (`Series owns the merch URL`, `Merch URL is optional`) and `app-error-log-alerting` (`Merch-discovery CronJob emits an ERROR log`) — and sync all delta specs into `openspec/specs/`
- [ ] 6.2 Verify no unintended `merch` reference remains in application code / config / templates. Allowed residue (do NOT treat as failures): the `reserved 5; reserved "merch_url";` line in `series.proto`; the new `..._drop_merch_url_from_series.sql` migration, its body, and `atlas.sum` entry; untouched historical migrations (e.g. `20260605...rework...`); this and other archived OpenSpec changes; and unrelated `merchant`/`merchandise` text in docs. Scope the check to source/config/UI and diff against this allowlist rather than a blanket repo-wide `grep -ri merch`
- [ ] 6.3 Confirm prod: no merch-discovery CronJob, no merch AlertPolicy, `series.merch_url` column dropped, fan concert-detail renders without a merch link
- [ ] 6.4 Archive the OpenSpec change once all PRs are merged and released
