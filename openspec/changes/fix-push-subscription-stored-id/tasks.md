# Tasks

No proto/schema change — this change only removes a stale known-defect note from two existing specs; no BSR/specification-release coordination is required.

## 1. Specs (this repo)

- [ ] 1.1 Remove the `Known defect: liverty-music/backend#474` note from `components/entity/push-subscription/create`, verified by `openspec validate fix-push-subscription-stored-id --strict`
- [ ] 1.2 Remove the `Known defect: liverty-music/backend#474` note from `components/usecase/push-subscription/create`, verified by `openspec validate fix-push-subscription-stored-id --strict`

## 2. Backend fix (liverty-music/backend#474, tracked and merged in the backend repo)

- [ ] 2.1 `PushSubscriptionRepository.Create`'s upsert query gains `RETURNING id`, and the returned id is assigned to `sub.ID` so the response always carries the stored row's id
- [ ] 2.2 Code comments on the upsert document that an existing endpoint is reassigned to the new caller's `user_id` (an endpoint belongs to a browser/device; the latest signed-in user owns it)
- [ ] 2.3 Integration test for re-registration: same user registers the same endpoint again → same id returned; a different user registers the same endpoint → same id returned, and the row's `user_id` moves to the new user
- [ ] 2.4 `make check` passes

## 3. Archive

- [ ] 3.1 After the backend PR merges, archive this change so the known-defect note is cleared from the main specs
