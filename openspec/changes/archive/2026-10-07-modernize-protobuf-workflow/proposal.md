## Why

Buf's "modern Protobuf workflow" and its protovalidate performance release (protovalidate-go v1.4.0 ~3x, protovalidate-es v1.3.0 ~13x faster through native rules) describe a toolchain we mostly run already, but our setup has drifted from it: the backend validates with protovalidate-go v1.0.0, the breaking-change guard has silently skipped the artist schema since March 2026, the three consumed SDK builds point at three different schema commits, a vestigial `buf.gen.yaml` still lists the legacy PGV plugin, and the frontend restates proto constraints by hand. Auditing those hand-written copies also surfaced a real contract defect: the applicant phone number is documented as E.164 but only length-checked, while the lottery screen accepts and sends domestic-format numbers, so stored 本人確認 (identity check) contacts have no single format.

## What Changes

- **Backend validation upgrade**: move `connectrpc.com/validate` to v0.7.0 so the request interceptor runs on protovalidate-go v1.4.0 (native rules, fewer allocations). No rule semantics change.
- **Breaking guard restored for artist**: remove the `buf.yaml` breaking `ignore` entries for `artist.proto` and `artist_service.proto`; intentional breaks go through the existing `buf skip breaking` PR label.
- **Single schema build across consumers**: advance backend (Connect and protobuf Go SDKs) and frontend (ES SDK) to the same schema release in this change, and add a backend CI check that both Go SDK modules carry the same schema commit. Renovate stays disabled for the schema SDK by policy (design D7 of the Renovate change); the alignment is enforced by check, not automation.
- **Vestigial generation config removed**: delete `specification/buf.gen.yaml` (local `buf generate` is forbidden; BSR generates SDKs) and drop it from the PR-check path filter.
- **Frontend contract validation**: add `@bufbuild/protovalidate` v1.3.0 as a client transport interceptor that validates every outgoing request against the proto rules and fails locally with InvalidArgument; the validator code loads lazily so the initial bundle does not grow. Hand-written copies of proto constraints that the interceptor now covers are removed; UX-level checks stay.
- **Applicant phone number is E.164** (**BREAKING** for clients sending domestic format): the proto rule for `ApplicantIdentity.phone_number` gains an E.164 pattern; the lottery application screen accepts a Japanese domestic number (with or without separators) or an E.164 number and always sends E.164; existing stored applicant and ticket-holder numbers are backfilled to E.164.
- **Buf CI and editor hygiene**: run lint, format and breaking checks through `bufbuild/buf-action`'s native mode (PR annotations and summary comment, native `buf skip breaking` label) with push and archive disabled (push stays release-only); remove machine-specific absolute paths from the committed `specification/.vscode/settings.json`.

## Capabilities

### New Capabilities

- `components/infrastructure/fan/web/route/lottery-apply`: the fan's lottery application screen — the phone number entry rule (domestic or E.164 accepted, E.164 sent, inconvertible input blocked before submission).

### Modified Capabilities

- `components/entity/ticket-application`: "Applicant identity is required" — the applicant phone number must be E.164. (Purpose) attribute table row for the applicant phone number updated in the main spec.
- `components/entity/ticket`: (Purpose) attribute table row for the holder phone number updated in the main spec to E.164; the holder identity is copied from the won application, so no requirement text changes.
- `components/adapter/fan/api/rpc/lottery`: "Lottery requests are validated at the boundary" — Apply fails with InvalidArgument when the phone number is not E.164.

`components/usecase/ticket-application/apply` is unchanged: its identity check is "missing name or phone", and the format rule is enforced by the entity rule at the boundary before the usecase runs. TicketApplication.Create and the Ticket issuance operations are unchanged: they store what they are given.

## Impact

- **specification**: `proto/liverty_music/entity/v1/lottery_application.proto` (phone pattern), `buf.yaml`, `buf.gen.yaml` (deleted), `.github/workflows/buf-pr-checks.yml`, `.vscode/settings.json`, `AGENTS.md`/`CLAUDE.md` references to `buf.gen.yaml` if any. Requires a GitHub Release so BSR regenerates the SDKs.
- **backend**: `go.mod` (`connectrpc.com/validate` v0.7.0, `buf.build/go/protovalidate` v1.4.0, both `buf.build/gen/go/liverty-music/schema/*` modules on the new release), entity doc comment for the phone number, Atlas migration backfilling `ticket_applications.applicant_phone_number` and `tickets.holder_phone_number` plus a CHECK constraint, CI job checking the schema SDK commits match.
- **frontend**: `package.json` (`@bufbuild/protovalidate`, `@buf/liverty-music_schema.bufbuild_es` on the new release), `src/services/grpc-transport.ts` (validation interceptor), lottery-apply route (phone normalization), removal of duplicated constraint code in `src/util/change-locale.ts` / `src/services/user-hydration-task.ts` where the interceptor covers it.
- **Rollout order**: frontend sends E.164 before the backend enforces the pattern; installed PWAs on an older build sending domestic format get InvalidArgument once the backend is upgraded (see design).
