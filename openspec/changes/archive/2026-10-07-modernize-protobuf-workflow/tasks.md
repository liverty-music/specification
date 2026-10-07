## 1. Schema and Buf toolchain (specification)

- [x] 1.1 In `proto/liverty_music/entity/v1/lottery_application.proto`, change `ApplicantIdentity.phone_number` to `pattern: "^\\+[1-9][0-9]{1,14}$"` with `max_len: 16` (drop `min_len`), keeping the E.164 field comment (D7). Verify `make lint` passes (lint, format, breaking against `origin/main`).
- [x] 1.2 Remove the `breaking.ignore` entries for `artist.proto` and `artist_service.proto` from `buf.yaml` (D5). Verify `buf breaking --against '.git#branch=origin/main'` passes.
- [x] 1.3 Delete `buf.gen.yaml`, remove it from the `dorny/paths-filter` list in `.github/workflows/buf-pr-checks.yml`, and remove or update any reference in `AGENTS.md`, `CLAUDE.md`, `README.md` and `proto/CLAUDE.md` (D3). Verify `grep -rn "buf.gen.yaml" --exclude-dir=openspec .` returns nothing.
- [x] 1.4 Replace the `setup_only` + manual steps in the `buf-checks` job with buf-action native mode (`lint`, `format`, `breaking` on; `push: false`; `archive: false`; `pr_comment: true`), keeping the `changes`, `buf-checks-skip` and `ci-success` jobs (D4). Verify on the PR that the buf-action summary comment appears, and that a test commit with a breaking edit fails until the `buf skip breaking` label is added (revert the test commit afterwards).
- [x] 1.5 Delete the machine-specific `.vscode/settings.json` and add `.vscode/extensions.json` recommending `bufbuild.vscode-buf` (served by `buf lsp serve` from the mise-managed buf). Verify `git ls-files .vscode` lists only `extensions.json` and the file contains no absolute path.
- [x] 1.6 Open the specification PR (OpenSpec-Change `modernize-protobuf-workflow`), merge, and publish GitHub Release `vX.Y.Z`. Verify `gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 1` shows success and the new commit is on `buf.build/liverty-music/schema`.

## 2. Frontend lottery-apply screen (components/infrastructure/fan/web/route/lottery-apply)

- [x] 2.1 Upgrade `@buf/liverty-music_schema.bufbuild_es` to the `vX.Y.Z` build. Verify `npm ci`, `npm run typecheck` and `npm run build` succeed.
- [x] 2.2 Add the pure `toE164` normalizer (D7) and unit tests annotated `// @spec components/infrastructure/fan/web/route/lottery-apply "<scenario>"` for "Domestic number with hyphens", "Landline number", "E.164 number with spaces" and "Number fits neither form". Verify the tests pass.
- [x] 2.3 Make `isIdentityValid` require a non-blank name and `toE164(phone) !== null`, send the normalized number in the Apply payload, and show an invalid-number message under the phone field (new ja/en i18n key) when the input is non-empty and invalid. Update `lottery-apply-route.spec.ts` so its existing identity cases plus a payload assertion cover the four scenarios. Verify `npm test` passes and the message renders in both locales in Storybook or the dev server.

## 3. Frontend contract validation (D6)

- [x] 3.1 Add `@bufbuild/protovalidate` `^1.3.0`. Implement the validation interceptor: dynamic `import()` started at transport creation, one validator instance reused, unary requests only, `ConnectError(Code.InvalidArgument)` with the violations on an invalid result, pass-through while the module is still loading. Register it in `grpc-transport.ts` between logging and auth. Verify unit tests pass for: invalid request rejected without calling `next`, valid request forwarded, request forwarded before the module has loaded.
- [x] 3.2 Audit hand-written restatements of proto rules (`src/util/change-locale.ts`, `src/services/user-hydration-task.ts`, lottery route). Remove pure duplicates and update "mirrors the backend protovalidate constraint" comments to reference the interceptor. Keep `isCountValid` and `normalizeToSupportedLanguage` (D6). Verify `npm test` and `make check` pass.
- [x] 3.3 Build production and record the size of the protovalidate chunk and the initial entry chunk before and after in the PR description. Verify the entry chunk does not include protovalidate or CEL modules and `npm run verify:bundle-isolation` passes.
- [x] 3.4 Open the frontend PR, merge and deploy to production. Verify that an Apply in production stores an E.164 number (read-only query on the newest `ticket_applications` row, or a dev-environment run).

## 4. Backend entity and boundary (components/entity/ticket-application, components/adapter/fan/api/rpc/lottery)

- [x] 4.1 Upgrade both `buf.build/gen/go/liverty-music/schema/*` modules to the `vX.Y.Z` build and `connectrpc.com/validate` to v0.7.0 (pulls `buf.build/go/protovalidate` v1.4.0) (D1). Verify `go mod tidy` leaves `protovalidate v1.4.0` in `go.mod`, and `go build ./...` and `make test` pass.
- [x] 4.2 Add a protovalidate test on `entityv1.ApplicantIdentity` annotated `// @spec components/entity/ticket-application "<scenario>"` for "Identity complete", "Missing name or phone", "Domestic-format phone number" and "Phone number too long". Update the `ApplicantIdentity.PhoneNumber` doc comment in `internal/entity/lottery_sales_phase.go` to E.164 only. Verify the tests pass.
- [x] 4.3 Add handler-level tests through the Connect server with the validation interceptor, annotated `// @spec components/adapter/fan/api/rpc/lottery "<scenario>"`, for "Domestic-format phone number" (InvalidArgument, usecase not called) and "E.164 phone number" (usecase called). Keep "Zero tickets" passing. Verify `make test` passes.
- [x] 4.4 Add the `lint.yml` step that fails when the commit segments of the `buf.build/gen/go/liverty-music/schema/*` versions in `go.mod` differ (D2). Verify it passes on this branch and fails locally when one module is edited to another commit.

## 5. Phone number data migration (backend)

- [x] 5.1 Run a read-only production query counting `ticket_applications.applicant_phone_number` and `tickets.holder_phone_number` values that, after stripping spaces, hyphens and parentheses, match neither `^0[0-9]{9,10}$` nor `^\+[1-9][0-9]{1,14}$`. Verify the count is recorded in the PR, and any non-zero rows are fixed by hand or listed for a decision before 5.2 merges.
- [x] 5.2 Add the Atlas backfill migration normalizing both columns to E.164 (D7), mirrored in `internal/infrastructure/database/rdb/schema/schema.sql` if it affects the schema. Verify `atlas migrate apply --env local` on a database seeded with `090-1234-5678`, `03 1234 5678` and `+819012345678` yields `+819012345678`, `+81312345678` and `+819012345678`.
- [x] 5.3 Add the migration adding `CHECK (... ~ '^\+[1-9][0-9]{1,14}$')` to both columns as `NOT VALID` followed by `VALIDATE CONSTRAINT`, and mirror it in `schema.sql`. Verify `atlas migrate diff --env local` reports no drift, Atlas CI passes, and inserting `09012345678` locally fails.
- [x] 5.4 Open the backend PR at least 24 hours after 3.4 is live in production, merge, release and deploy. Verify the migrations applied in production and a re-run of the 5.1 query returns zero rows with no remaining domestic-format values.

## 6. Rollout verification

- [x] 6.1 Verify backend and frontend reference the same schema commit: the commit segment in both backend `go.mod` schema versions equals the one in frontend `package.json` `@buf/liverty-music_schema.bufbuild_es`.
