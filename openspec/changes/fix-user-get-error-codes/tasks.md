# Tasks

No proto/schema change — this change only removes a stale known-defect note from five existing specs; no BSR/specification-release coordination is required.

## 1. Specs (this repo)

- [ ] 1.1 Remove the `Known defect: liverty-music/backend#471` note from `components/usecase/user/get`, verified by `openspec validate fix-user-get-error-codes --strict`
- [ ] 1.2 Remove the `Known defect: liverty-music/backend#471` note from `components/usecase/user/get-by-external-id`, verified by `openspec validate fix-user-get-error-codes --strict`
- [ ] 1.3 Remove the `Known defect: liverty-music/backend#471` note from `components/adapter/fan/api/rpc/ticket`, verified by `openspec validate fix-user-get-error-codes --strict`
- [ ] 1.4 Remove the `Known defect: liverty-music/backend#471` note from `components/adapter/fan/api/rpc/concert`, verified by `openspec validate fix-user-get-error-codes --strict`
- [ ] 1.5 Remove the `Known defect: liverty-music/backend#471` note from `components/adapter/fan/api/rpc/lottery`, verified by `openspec validate fix-user-get-error-codes --strict`

## 2. Backend fix (liverty-music/backend#471, tracked and merged in the backend repo)

- [ ] 2.1 `UserUseCase.Get` and `UserUseCase.GetByExternalID` add context with `fmt.Errorf("...: %w", err)` instead of `apperr.Wrap(err, codes.NotFound, ...)`, preserving the repository's error code
- [ ] 2.2 Unit tests: repository returns Unavailable and Internal for `Get` and `GetByExternalID`, and the usecase surfaces those codes unchanged (alongside the existing NotFound case)
- [ ] 2.3 `make check` passes

## 3. Archive

- [ ] 3.1 After the backend PR merges, archive this change so the known-defect notes are cleared from the main specs
