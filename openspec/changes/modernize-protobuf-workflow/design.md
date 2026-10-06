## Context

See proposal.md - Why. Current state that shapes the approach:

- **specification**: `buf.yaml` (v2, deps googleapis + protovalidate, lint STANDARD + COMMENTS, breaking FILE with `ignore` on `entity/v1/artist.proto` and `rpc/artist/v1/artist_service.proto` since 2026-02/03). `buf.gen.yaml` lists unpinned remote plugins including `buf.build/bufbuild/validate-go` (legacy protoc-gen-validate, which reads `validate.rules`, not `buf.validate`); `gen/` is gitignored and `buf generate` is forbidden by the workspace rules, so the file has no consumer. `buf-pr-checks.yml` uses `bufbuild/buf-action` with `setup_only: true` and runs `buf lint`, `buf format -d --exit-code` and `buf breaking` as plain steps, honouring a `buf skip breaking` label by hand. `buf-release.yml` pushes on GitHub Release. `.vscode/settings.json` is committed with macOS absolute paths (`buf.binaryPath` → buf 1.54.0, Go 1.24.4).
- **backend**: `connectrpc.com/validate v0.6.0` → `buf.build/go/protovalidate v1.0.0` (indirect). `validate.NewInterceptor()` is the innermost server interceptor; responses are not validated (unary default). Schema SDKs: `connectrpc/go …-20260913101508-7795859df477.1` and `protocolbuffers/go …-20260915050914-c470358dd62d.2` — two different schema commits. Renovate disables `buf.build/gen/go/**`; `liverty-music/schema` by policy.
- **frontend**: `@buf/liverty-music_schema.bufbuild_es …-20260913052028-ce6e594ac619.1` (a third commit). No protovalidate. Transport interceptors in `src/services/grpc-transport.ts`: otel → logging → auth → auth-retry → retry. The lottery screen sends the phone number as typed (`phoneNumber.trim()`) after a lenient 10-11 digit check.
- **Data**: `ticket_applications.applicant_phone_number` and `tickets.holder_phone_number` are `text NOT NULL` with no format constraint. Ticket holder identity reuses the `ApplicantIdentity` message (`ticket.proto` field 5), so one proto rule covers both.

## Goals / Non-Goals

**Goals:**

- Every consumer runs the faster protovalidate runtimes with unchanged rule semantics.
- One schema build per release across backend and frontend, checked mechanically inside backend.
- Phone numbers have exactly one stored and transmitted format (E.164) end to end.

**Non-Goals:**

- Response validation on either side (server `WithValidateResponses`, client response checks).
- Moving to connect-go v2 / `connectrpc.com/validate` v0.8 (release candidate only).
- A cross-repository check that backend and frontend sit on the same schema commit (each repo checks out alone in CI); the release runbook remains the control.
- Field-level violation mapping and localized violation messages in forms.
- International phone entry beyond "domestic Japanese or already-E.164".

## Decisions

### D1. Upgrade validate-go rather than pin protovalidate-go directly

Bump `connectrpc.com/validate` to v0.7.0, whose `go.mod` requires `buf.build/go/protovalidate v1.4.0`. Alternative: add `buf.build/go/protovalidate v1.4.0` as a direct requirement while keeping v0.6.0 — works through MVS but leaves an interceptor built and tested against v1.0.0, and a direct requirement we never import. v0.7.0's only change is the protovalidate bump; v0.8.0-rc requires connect-go v2 and is out of scope. Native rules are verified against the same conformance suite as CEL, so no behaviour change is expected; the existing handler tests that assert InvalidArgument are the regression net.

### D2. Schema SDK alignment is enforced by a check, not by Renovate

The Renovate policy (disabled by policy, advanced by the change that alters the schema) is right: an SDK bump usually needs code migration. What is missing is detection of skew *within* a bump. Add a backend CI step (in `lint.yml`) that extracts the 12-character commit segment from every `buf.build/gen/go/liverty-music/schema/*` version in `go.mod` and fails when they differ. Alternative: Renovate group for both modules — rejected, Renovate cannot parse BSR versions (see the backend renovate.json note) and the policy disables it anyway. This change itself re-aligns all three SDKs because the phone pattern requires a new release.

### D3. Delete `buf.gen.yaml` instead of fixing it

BSR's generated SDKs use BSR's plugin configuration, not this file; nothing in the workspace runs `buf generate`. Fixing it (pinning versions, swapping `validate-go` out) would maintain a file whose only effect is to mislead. Remove it, drop it from the `buf-pr-checks.yml` path filter, and drop any doc reference. If local generation is ever needed again, it is recreated with pinned plugins by that change.

### D4. buf-action native checks, push and archive off

Replace the `setup_only` + manual steps with buf-action's native mode: `lint`, `format`, `breaking` on, `push: false`, `archive: false`, `pr_comment: true`. buf-action compares against the PR base and honours the `buf skip breaking` label natively, so the existing contract with contributors is unchanged. Push stays in `buf-release.yml` (release-labelled pushes are what the SDK versioning relies on), so the blog's "push on merge to main" is deliberately not adopted. The `ci-success` aggregator job is kept. `make lint` stays as the local equivalent.

### D5. Breaking guard for artist: remove the ignore, no other change

The ignores were added for one-off breaking edits during early artist work. The `buf skip breaking` label already covers intentional breaks per PR, which is auditable; a file-level ignore is not. No in-flight change touches the artist proto (`refresh-artist-official-site` states "No proto change").

### D6. Frontend validation as a non-blocking transport interceptor

Add an interceptor that, for unary requests, validates `req.message` against `req.method.input` with `@bufbuild/protovalidate`'s `createValidator()` and throws `ConnectError(Code.InvalidArgument)` carrying the violations when the result is invalid. It sits after logging and before auth/retry (otel → logging → **validate** → auth → auth-retry → retry) so invalid requests are traced and logged but never authenticated or retried.

The validator module (protovalidate + its CEL runtime) is loaded with a dynamic `import()` started at transport creation; until it resolves, requests pass unvalidated. Alternatives: (a) static import — grows the initial bundle on every route for a check the server repeats; (b) dynamic import awaited on the first request — the first RPCs fire at app start, so this adds the chunk download to first paint's data path. Non-blocking keeps both the bundle and the latency unchanged at the cost of the first few requests going unchecked, which is acceptable because the server is authoritative. The validator instance is created once and reused (it caches compiled rules per message type).

Hand-written copies are removed only where they restate a proto rule and nothing else: the lottery `isIdentityValid` phone heuristic is replaced by the D7 normalizer; `isCountValid` stays (its upper bound is the phase's dynamic max, not a proto rule); `normalizeToSupportedLanguage` stays (it coerces detector output, it does not validate). Comments that say "mirrors the backend protovalidate constraint" are updated to point at the interceptor.

### D7. Phone number: proto pattern, frontend normalizer, data backfill

- **Proto**: `ApplicantIdentity.phone_number` → `string.pattern: "^\\+[1-9][0-9]{1,14}$"`, `max_len: 16`, `min_len` dropped (implied by the pattern). The field comment already says E.164. `buf breaking` does not flag validation rules, so no label is needed; the tightening is a contract change handled by rollout order.
- **Frontend**: a pure function `toE164(input)` in the lottery route's module strips spaces, hyphens and parentheses; `0` + 9-10 digits → `+81` + digits without the `0`; `+` + digits matching the pattern → as is; anything else → `null`. `isIdentityValid` becomes "name non-blank and `toE164(phone) !== null`", the payload sends the normalized value, and the field shows an invalid-number message (new i18n key in ja/en) when the input is non-empty and `toE164` returns `null`. The input keeps what the fan typed.
- **Data**: an Atlas migration normalizes both columns with the same rule in SQL (`regexp_replace` separators, then `'+81' || substr(x, 2)` for `^0[0-9]{9,10}$`). A follow-up migration adds `CHECK (col ~ '^\+[1-9][0-9]{1,14}$')` as `NOT VALID` then `VALIDATE CONSTRAINT`, so a row the backfill could not convert fails the deploy instead of hiding. Before writing the migration, a read-only production count of rows matching neither form decides whether any manual fix is needed.

## Risks / Trade-offs

- [Installed PWAs on an older build keep sending domestic numbers after the backend enforces the pattern → their Apply fails with InvalidArgument] → Deploy frontend first and hold the backend deploy for at least 24 hours so the service worker update reaches active installs; the screen already surfaces InvalidArgument as an error, so failure is visible, not silent.
- [protovalidate-es + CEL runtime chunk size] → Loaded off the critical path (D6); measure the chunk in the PR and record it. `verify:bundle-isolation` is unaffected (it guards admin/organizer leakage, not size).
- [Client and server rule drift when the frontend SDK lags a release] → The client would enforce an older rule set; the server remains authoritative and D2 plus the release runbook keep SDKs moving together.
- [A stored phone number in neither form blocks the CHECK migration] → The production count runs first; such rows are fixed by hand (or the CHECK is deferred) before the migration merges.
- [Removing the artist ignore makes a future artist PR fail breaking] → Intended; the label is the escape hatch.

## Migration Plan

1. **specification** PR: phone pattern, remove artist ignores, delete `buf.gen.yaml`, buf-action native checks, `.vscode` cleanup → merge → GitHub Release `vX.Y.Z` → BSR generation completes.
2. **frontend** PR: SDK to `vX.Y.Z`, `@bufbuild/protovalidate`, validation interceptor, phone normalizer → deploy to production.
3. Read-only production query for unconvertible phone numbers; resolve any by hand.
4. **backend** PR (opened after step 2 is live for at least 24 hours): both schema SDKs to `vX.Y.Z`, `connectrpc.com/validate` v0.7.0, backfill + CHECK migrations, SDK-commit CI check → deploy.

Rollback: backend revert restores the old SDK (pattern no longer enforced) and validate v0.6.0; the backfill is not reverted (E.164 values satisfy the old length rule). The CHECK constraint is dropped by a revert migration if needed. Frontend revert re-sends typed numbers, which a backend on the new SDK rejects — so roll back backend before frontend.
