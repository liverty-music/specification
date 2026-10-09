## Context

See proposal.md for the motivation. The approach is shaped by these facts:

- **Admin RPCs run on the admin server.** It is a separate deployment, `admin-console-api`.
  - Every call is gated by a server-wide admin-role interceptor.
  - It is the only workload that mounts the `organizer-provisioner` Zitadel machine key (`IAM_ORG_MANAGER`), used by `OrganizerProvisioner` through the Zitadel Management API (`zitadel-go/v3`).
- **Database cascades and blockers**, from the foreign keys in the current schema:
  - **Cascade:** `events → concerts, ticket_journeys, event_performers, lottery_sales_phases → ticket_applications`; `series → events, draft_events, series_media, sales_phases, staged_concerts`; `organizers → organizer_artists, organizer_connected_accounts`; `users → follows, push_subscriptions, ticket_journeys, notifications, sales_phase_reminders, verified_identities`.
  - **RESTRICT:** `tickets.event_id`, `tickets.order_id`, `orders.application_id`, `settlements.*`.
  - **NO ACTION:** `series.organizer_id` and `media.organizer_id`.
  - So an Organizer cannot be removed in one `DELETE`, and Orders and Tickets must go before the Events and Applications they reference.
- **Orders, Tickets and Applications are not keyed to `users` by a foreign key.** `User.Delete` already keeps them, which is the behaviour the spec keeps.
- **Media files live in two GCS buckets:**
  - the original in the internal bucket (`<organizer>/<media>`);
  - the variants in the served bucket (`cdn/<organizer>/<media>/{thumb,large}.webp`).
  - `ImageStorer` already exposes `DeleteOriginal` and `DeleteVariants`, and treats not-found as success.
- **Zitadel caution.** On 2026-10-08 a burst of Zitadel user events exposed a projection-trigger deadlock at `MaxParallelTriggers = 1`. It is fixed by cloud-provisioning #608, which gives two workers. Removing orgs and users writes events of the same kind.

## Goals / Non-Goals

**Goals:**
- One call per Organizer and one per User removes the record and its dependents in GCS and Zitadel.
- Nothing is removed when a precondition fails.
- A failed call is completed by repeating it.

**Non-Goals:**
- Soft delete, undo, or an audit table. The structured log line per deletion is the record.
- Deleting Zitadel users that have no backend User.
- Deleting Stripe objects.
- An admin console screen.

## Decisions

### D1 — Order of effects: external first, database last

- **Order:** OrganizerUseCase.Delete removes the GCS files, then the Zitadel tenant, then runs `Organizer.Delete` in one database transaction.
- **Why the database goes last:**
  - Its rows are what make the Organizer findable; keeping them until the end means a retry still knows the tenant id and the media ids.
  - Every external removal treats not-found as done.
- **Rejected: database first, then external best-effort.** A failure after the commit would orphan GCS files and a Zitadel org that nothing references any more.
- **Pre-check:** the usecase runs the same blocker check as `Organizer.Delete` before step 1 (D3), so a paid Order stops the call before any file is touched.
- **Race guard:** a blocker that appears between the check and the transaction is still refused inside the transaction. In that case files and tenant may already be gone while the records remain. This is accepted: the Organizer is deactivated, so it has no live surface.

### D2 — `Organizer.Delete` is one repository method, one transaction

- `OrganizerRepository.Delete(ctx, id)` runs in one transaction:
  1. Lock the organizer row (`SELECT … FOR UPDATE`).
  2. Re-check the status is deactivated and that there are no blockers; otherwise return FailedPrecondition.
  3. Delete in RESTRICT-safe order:
     - `admissions`, `rejected_scans` and `reception_links` for the Organizer's events (added by `ticket-wallet-and-checkin`, all RESTRICT on `events`; `admissions` is also RESTRICT on `tickets`);
     - the Reversed `settlements` for the Organizer's events (cascades `settlement_splits`);
     - `tickets` for the Organizer's events;
     - `orders` whose application belongs to those events' phases;
     - `series` of the Organizer (cascades events, phases, applications, journeys, `series_media`);
     - `media` of the Organizer;
     - the `organizers` row (cascades `organizer_artists`; `organizer_connected_accounts` is already guaranteed empty by the check).
- **Blocker query:**
  - an order for the Organizer's events with `status <> Refunded`;
  - a settlement for those events that is not Reversed. Issuance creates a Settlement with every Order (backend#468) and a refund only flips it to Reversed, so a Reversed settlement is deleted with its refunded Order (`settlement_splits` cascade) instead of blocking (decided during apply, 2026-10-08);
  - a row in `organizer_connected_accounts`.
- **Reception records (decided during apply, 2026-10-08):** the reception links, admissions and rejected scans of the Organizer's events are removed with them. They exist only for those events, and keeping any of them would make every Organizer with a reception link undeletable.
- **Rejected:** changing the foreign keys to CASCADE. That is a migration, and it would make a plain `DELETE` on events silently remove purchases anywhere else in the code.

### D3 — The blocker check is shared

- The usecase's pre-check and the transaction's re-check use the same SQL, exposed as `OrganizerRepository.Delete`'s precondition.
- The usecase pre-check calls a dry run: `Delete` with `dryRun=true` returns the FailedPrecondition or nil without deleting anything. This keeps a single definition and avoids a second entity operation with a near-duplicate promise.
- **Alternative considered:** a separate `Organizer.ListDeletionBlockers` operation. It was rejected as a duplicate of the guard the spec already states on `Organizer.Delete`.

### D4 — Zitadel removal

- **`Organizer.DeleteTenant`:** `OrganizerProvisioner.DeleteTenant(ctx, zitadelOrgID)` calls the Management API `RemoveOrg`, using the `x-zitadel-orgid` context like `DeactivateOperators`. A gRPC NotFound counts as success. Removing an org removes its users.
- **`User.DeleteIdentity`:**
  - It removes the product-org human user by the User's `external_id` (`RemoveUser`, or `user/v2 DeleteUser`); NotFound counts as success.
  - The interface `IdentityRemover` is declared in `internal/entity`, beside `EmailVerifier`, per the rule that interfaces are defined where consumed.
  - It is realized in `internal/infrastructure/zitadel` with the client that holds rights over product-org users.
- **Verified rights (task 1.1, 2026-10-08):** prod Zitadel is v4.15.3 (`cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/kustomization.yaml`). In its `cmd/defaults.yaml`, `IAM_ORG_MANAGER` carries `org.delete` and `user.delete`, and `ORG_USER_MANAGER` carries `user.delete`.
  - `organizer-provisioner` is an instance member with `IAM_ORG_MANAGER` (`src/zitadel/components/organizer-provisioner.ts`), so `RemoveOrg` with `x-zitadel-orgid` set to the tenant works.
  - `backend-app` is a product-org member with `ORG_USER_MANAGER` (`src/zitadel/components/machine-user.ts`). **Chosen for `User.DeleteIdentity`** as the least-privileged client: `user/v2 DeleteUser` by `external_id`, which needs no org header.
  - Both keys are already mounted in `admin-console-api` (`k8s/namespaces/backend/base/admin-console-api/deployment.yaml`; paths from `ZITADEL_MACHINE_KEY_FOR_BACKEND_APP_PATH` and `ZITADEL_MACHINE_KEY_FOR_ORGANIZER_PROVISIONER_PATH`). Nothing to add for Zitadel.
- **Rate:** the cleanup run removes one Organizer or User at a time. Each call writes at most a handful of events, which stays far from the burst that triggered the deadlock.

### D5 — Media file removal reuses `ImageStorer`

- For each Media from `MediaRepository.ListByOrganizer`, the usecase calls `ImageStorer.DeleteOriginal(internalBucket, organizerID, mediaID)` and `ImageStorer.DeleteVariants(servedBucket, organizerID, mediaID)`.
- The bucket names come from the existing config: `ORGANIZER_MEDIA_INTERNAL_BUCKET` and `ORGANIZER_MEDIA_BUCKET`. `admin-console-api` needs both, so check its ConfigMap.
- The spec names these operations `Media.DeleteOriginal` and `Media.DeleteVariants`, matching the existing method names.
- `Media.ListByOrganizer` is implemented as `MediaRepository.ListMediaByOrganizer`: `SeriesRepository` implements `MediaRepository` and already has a `ListByOrganizer` for Series, so the media method follows the interface's `InsertMedia` / `FindMediaByID` / `DeleteMedia` naming.
- **Checked (task 1.2, 2026-10-08):**
  - `ORGANIZER_MEDIA_BUCKET` reaches `admin-console-api` through the shared `fan-api-config` (prod and dev overlays).
  - `ORGANIZER_MEDIA_INTERNAL_BUCKET` is **missing** for `admin-console-api` in every overlay. It is set only for `media-consumer` and `organizer-console-api`.
  - The `admin-console-api` GSA has **no** storage role on either bucket. `src/gcp/components/organizer-media.ts` grants `objectAdmin` only to `organizer-console-api` and `media-consumer`.
  - Both are added in task 7.1: `roles/storage.objectUser` (list, get and delete; `DeleteVariants` lists a prefix) on both buckets for the `admin-console-api` GSA, and the env var in the prod and dev `admin-console-api` patches.

### D6 — RPC shape

- `liverty_music.rpc.admin.organizer.v1.OrganizerService.Delete(DeleteRequest{organizer_id}) → DeleteResponse{}`.
- New `liverty_music.rpc.admin.user.v1.UserService.Delete(DeleteRequest{user_id}) → DeleteResponse{}`, registered on the admin server only.
- Both ids are required and must be UUIDs (protovalidate).
- **No `validate_only` flag:** the deactivated precondition is the deliberate second step the admin takes, and a refused call removes nothing.

### D7 — Cleanup run (operations, not code)

1. **Deactivate:** `Deactivate` each test Organizer that is still active (13 of 15).
2. **Delete Organizers:** `Delete` each test Organizer, one at a time, checking the login probe (`docs/runbooks/zitadel-hang.md`) after each.
3. **Delete Users:** `UserService.Delete` for `pannpers+dev1`, `+3`, `+6` and `+10`.
4. **Zitadel-only users:** remove `pannpers+2`, `+4`, `+5` and `+8` in the Zitadel console.
5. **Keep:** `pepperoni9@gmail.com`, `crusher_theory_dsa@yahoo.co.jp` and the prod E2E user.
6. **Check:** confirm that the GCS prefixes for the deleted organizers are empty and that `public-event-page`'s `/events/<id>` for the deleted events returns not found.

## Risks / Trade-offs

- **[Risk] The Zitadel machine user may lack the right to remove product-org users or orgs.** → Mitigation: verify in a task before implementation (`RemoveOrg` with `IAM_ORG_MANAGER`; `RemoveUser` on the product org). If the right is missing, grant it in cloud-provisioning (Zitadel membership) as part of this change.
- **[Risk] Irreversible deletion of the wrong Organizer or User.** → Mitigation:
  - Organizers must be deactivated first (a separate call).
  - Purchases block deletion.
  - The cleanup run lists each id against the investigation in D7 before calling.
- **[Trade-off] Deleting refunded Orders and Tickets removes their database history.** Stripe keeps the payment and refund records. The user chose this to clean up test purchases.
- **[Risk] A Zitadel event burst could re-expose the trigger deadlock.** → Mitigation: run one deletion at a time and probe login between them (D7). The fix in #608 is deployed.

## Migration Plan

1. **specification:** add the two RPCs; then PR, Release and BSR generation.
2. **backend:** in one PR, add the repository operations, the Zitadel and GCS wiring and the usecases and handlers, with tests; then release.
   - Verify that `admin-console-api` has the bucket env vars and the Zitadel rights; add them in cloud-provisioning if missing.
3. **Operations:** run the cleanup in D7 against prod.

Rollback: revert the backend release. Deletions already performed are not reversible, which is why D7 runs one call at a time.

## Open Questions

- Which Zitadel client removes product-org users: the `organizer-provisioner` key (`IAM_ORG_MANAGER`) or the `backend-app` key? This is answered by the verification task; neither answer changes the specs.
