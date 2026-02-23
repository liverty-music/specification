## 1. Backend: Interceptor Chain Reorder

- [x] 1.1 Reorder interceptor registration in `internal/infrastructure/server/connect.go` to: tracingInterceptor, accessLogInterceptor, errorHandlingInterceptor (in `WithInterceptors`), then `newRecoverHandler` (separate `HandlerOption`), then claimsBridgeInterceptor, validationInterceptor (in second `WithInterceptors`)
- [x] 1.2 Add inline code comments documenting the execution order (outermost to innermost), the rationale for each interceptor's position, and the context propagation model
- [x] 1.3 Verify the reorder does not change existing test results (`go test ./...`)

## 2. Backend: Nil Guard in userUseCase.Create

- [x] 2.1 Add nil check on `user` return value before accessing `user.ID` in `internal/usecase/user_uc.go`, returning `apperr.New(codes.Internal, ...)` if nil
- [x] 2.2 Add unit test case for `(nil, nil)` return from `userRepo.Create` mock in `user_uc_test.go`

## 3. Frontend: Fix provisionUser Error Handling

- [x] 3.1 Change `provisionUser()` in `src/routes/auth-callback.ts` to re-throw non-`AlreadyExists` errors so the outer `catch` in `loading()` handles them
- [x] 3.2 Verify the outer `catch` block in `loading()` correctly displays an error message to the user when provisioning fails

## 4. Verification

- [x] 4.1 Run backend linter and tests (`golangci-lint run && go test ./...`)
- [x] 4.2 Run frontend linter and type check
