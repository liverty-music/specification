## 1. Discovery usecase (backend; components/usecase/sales-phase/discover-for-artist)

- [x] 1.1 Set `salesPhaseSearchInterval` to 10 days and compare Japan-time dates (design D1, D2). Verify unit tests annotated `@spec` pass for "Tracked series with nothing pending", "First-come sale until sold out has opened", "Searched recently", "Ten days counted by date", "Nine days counted by date" and "Search finds nothing", and that the other scenarios of the capability still pass.

## 2. Config cleanup (backend; design D3)

- [x] 2.1 Remove `GeminiSearchModelParse`, `GeminiSearchThinkingParse`, `GeminiSearchTemperature`, their validation, `SearchModelExtract()`, `SearchModelParse()` and their defaults from `pkg/config`, with their tests. Verify `go build ./...`, the `pkg/config` tests and `make lint` pass, and `git grep` finds no remaining reference in backend or cloud-provisioning.

## 3. Release

- [x] 3.1 Open the backend PR citing this change and the store commit, merge it with CI green, and cut a release. Verify `bump-prod-pin` pins prod to the release and ArgoCD `backend` is Synced on that commit.
- [x] 3.2 After the next 21:00 JST run, verify in the job log that it completes without errors and that a tracked series searched on 2026-10-06 is not searched before the 2026-10-16 run. (Verified with a manual run from the CronJob template on v1.61.0 at 2026-10-07 10:53 JST instead of waiting for 21:00: completed with no warning or error, and all 5 artists searched on 2026-10-06 were skipped with no Gemini call.)
