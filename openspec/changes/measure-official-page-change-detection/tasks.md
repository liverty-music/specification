## 1. backend: official-page-check mode

- [ ] 1.1 Add the page-text normalization and hashing (design D2) next to the official top page fetch in `internal/infrastructure/gcp/gemini`, and verify with table tests: two pages that differ only in script, style, noscript, template or svg content or in whitespace give the same SHA-256; a change in visible text gives a different one; the length counts characters, not bytes
- [ ] 1.2 Refactor the top-page fetch to parse the document once and return both the listed links and the page text (design D3), and verify the searcher's existing link-list tests pass unchanged
- [ ] 1.3 Add the official-page checker: for each followed Artist with an OfficialSite, fetch the top page and each listed link with the official page client, 4 Artists at a time and one page at a time per site, and log one `official_page_check` analytics line per page with the fields of design D4; verify with an `httptest` server that a top page with two listed links yields three lines with the expected `page_kind`, `status` and hashes, and that a 404 link and an unreachable link are logged as `http_error` and `fetch_error` without stopping the run
- [ ] 1.4 Add the `-mode` flag to `cmd/job/concert-discovery` (`search` default, `official-page-check`), with the run summary on the `job_result` topic; verify the default mode still runs the daily search unchanged and an unknown mode exits non-zero with a message naming the allowed values
- [ ] 1.5 Release backend once the image built from the merge exists, and confirm that `bump-prod-pin.yml` in cloud-provisioning wrote that version into every backend prod pin on main (design Migration Plan step 1)

## 2. cloud-provisioning: temporary CronJob

- [ ] 2.1 Add the `official-page-check` CronJob under `k8s/namespaces/backend/base/cronjob/` (design D1, D5): the concert-discovery image with `args: ["-mode=official-page-check"]`, the `concert-discovery-job-config` ConfigMap and `backend-secrets`, schedule `0 8 * * *`, `concurrencyPolicy: Forbid`, `backoffLimit: 0`, `activeDeadlineSeconds: 7200`; add it to the base kustomization and the overlays the same way as concert-discovery, and verify `kustomize build` of the prod and dev overlays renders it with the prod and dev images; merge only after task 1.5 confirmed the prod pins carry the release (ArgoCD syncs it to prod), and say so in the report

## 3. Production check (read-only)

- [ ] 3.1 After the first scheduled run, confirm with kubectl that the Job completed, and with a BigQuery query on `logs_analytics` that it logged one `official_page_check` line per followed Artist's top page and listed link, with failures under 10% of pages; confirm the 18:00 JST concert-discovery run of that day completed as before

## 4. Results and cleanup

- [ ] 4.1 After the 8th run (or the extension in design D6), join the `official_page_check` lines with the `daily_run` `concert.search.completed` events of the period as design D6 describes (comparable searches only, `ok` pages only, failed searches skipped as baselines), and write the aggregate results and a recommendation for the next change into the Results section of design.md (counts only, no production records)
- [ ] 4.2 Remove the `official-page-check` CronJob from cloud-provisioning, merge, and confirm with kubectl that the CronJob no longer exists in prod
- [ ] 4.3 Remove the `official-page-check` mode, the checker and the `official_page_check` topic from backend, keeping the refactor of task 1.2 only if the searcher's code is simpler with it; verify the searcher's link-list tests still pass
