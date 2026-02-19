## 1. GitHub Issues

- [x] 1.1 Create backend GitHub issue for CI optimization (liverty-music/backend)
- [x] 1.2 Create frontend GitHub issue for gemini.yml reusable workflow (liverty-music/frontend, separate change)

## 2. Frontend: ci.yaml

- [x] 2.1 Add `concurrency` group with `cancel-in-progress: true`
- [x] 2.2 Add `permissions: contents: read, pull-requests: write` at workflow level
- [x] 2.3 Add `paths-ignore` for docs/markdown-only changes
- [x] 2.4 Add `timeout-minutes` to lint job (5 min) and test job (10 min)
- [x] 2.5 Add `typecheck` job (`npx tsc --noEmit`)
- [x] 2.6 Add format check step to lint job (`npm run format -- --check` or biome equivalent)
- [x] 2.7 Add security audit job (`npm audit --audit-level=moderate`)
- [x] 2.8 Add coverage thresholds to vitest config (statements: 20, branches: 70, functions: 30, lines: 20)
- [x] 2.9 Add PR coverage comment step using `davelosert/vitest-coverage-report-action@v2`
- [x] 2.10 Add `ci-success` gate job depending on all required jobs

## 3. Frontend: push-image.yaml

- [x] 3.1 Add `concurrency` group with `cancel-in-progress: false` (deploy workflow)

## 4. Backend: lint.yml

- [x] 4.1 Add `concurrency` group with `cancel-in-progress: true`
- [x] 4.2 Add `permissions: contents: read` at workflow level
- [x] 4.3 Add `timeout-minutes` to golangci-lint job (10 min)
- [x] 4.4 Add `gofmt` check job (fail if any file differs from `gofmt` output)

## 5. Backend: test.yml

- [x] 5.1 Add `concurrency` group with `cancel-in-progress: true`
- [x] 5.2 Add `permissions: contents: read` at workflow level
- [x] 5.3 Add `timeout-minutes` to test job (15 min) and vulnerability-check job (10 min)
- [x] 5.4 Add `ci-success` gate job depending on test and vulnerability-check

## 6. Backend: benchmark.yml

- [x] 6.1 Add `concurrency` group with `cancel-in-progress: true`
- [x] 6.2 Add `permissions: contents: read` at workflow level
- [x] 6.3 Fix Postgres service image from `postgres:15` to `postgres:18`

## 7. Backend: atlas-ci.yml

- [x] 7.1 Remove commented-out `ATLAS_CLOUD_TOKEN` env var
- [x] 7.2 Replace commented-out `ariga/atlas-action/migrate/lint` step with `atlas migrate lint --dev-url "${{ env.DATABASE_URL }}" --dir "file://internal/infrastructure/database/rdb/migrations/versions"`
- [x] 7.3 Add `permissions: contents: read` at workflow level
- [x] 7.4 Add `concurrency` group with `cancel-in-progress: true`

## 8. Backend: deploy.yml

- [x] 8.1 Add `concurrency` group with `cancel-in-progress: false` (deploy workflow)
