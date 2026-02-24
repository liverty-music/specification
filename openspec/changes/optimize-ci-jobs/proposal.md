## Why

CI workflows across frontend and backend repos lack basic optimizations: no concurrency controls, missing permissions hardening, and absent quality gates. This results in wasted CI minutes from redundant runs, security exposure from over-permissioned jobs, and slow developer feedback loops.

## What Changes

- Add `concurrency` groups to all workflows (frontend: ci.yaml, push-image.yaml; backend: lint.yml, test.yml, benchmark.yml, deploy.yml) to cancel superseded runs
- Add `permissions` minimization to all workflows that lack it
- Add `paths-ignore` to frontend ci.yaml to skip CI on doc-only changes
- Add `timeout-minutes` to all jobs
- Add `gofmt` format check job to backend lint.yml
- Add coverage threshold enforcement to frontend ci.yaml
- Add typecheck job to frontend ci.yaml
- Add security audit job (`npm audit`) to frontend ci.yaml
- Add PR coverage comment to frontend ci.yaml (vitest-coverage-report-action)
- Add CI success gate job to both repos
- Fix benchmark.yml: Postgres version 15 → 18 (align with test.yml)
- Fix atlas-ci.yml: replace commented-out Atlas Cloud lint with `atlas migrate lint --dev-url` (cloud-free)
- Add `gofmt` format check to backend lint.yml

## Capabilities

### New Capabilities
- `ci-optimization`: CI workflow improvements for performance, security, and developer experience across frontend and backend repositories

### Modified Capabilities

## Impact

- `.github/workflows/ci.yaml` (frontend) — modified
- `.github/workflows/push-image.yaml` (frontend) — modified
- `.github/workflows/lint.yml` (backend) — modified
- `.github/workflows/test.yml` (backend) — modified
- `.github/workflows/benchmark.yml` (backend) — modified
- `.github/workflows/deploy.yml` (backend) — modified
- `.github/workflows/atlas-ci.yml` (backend) — modified
- No application code changes; CI-only
