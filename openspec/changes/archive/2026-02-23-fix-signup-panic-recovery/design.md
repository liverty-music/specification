## Context

When `UserService.Create` panics during signup, three compounding failures occur:

1. **Backend panic** — A nil pointer dereference (or similar) in the handler causes a panic. The `recoverHandler` catches it and returns `connect.CodeInternal`.
2. **No observability** — The access log interceptor sits inside the recover handler. When a panic unwinds the stack, the access log's post-`next()` code is bypassed, producing zero access log entries for the request. The panic log itself lacks `trace_id` because the recover handler sits outside the tracing interceptor.
3. **Frontend error swallow** — `provisionUser()` catches the `CodeInternal` error, logs it, but does not throw. The auth flow continues as if provisioning succeeded, leaving the user without a backend record.

The root cause of the observability failures is incorrect interceptor chain ordering. The root cause of the user-facing breakage is the frontend's silent error handling.

## Goals / Non-Goals

**Goals:**

- Fix interceptor chain ordering so that all logs (access, error, panic) include trace context and correct status codes.
- Add a nil guard in `userUseCase.Create` to prevent nil pointer dereference from interface contract violations.
- Fix frontend `provisionUser()` to halt the auth flow and surface errors when provisioning fails.
- Document the interceptor ordering rationale in code comments for future maintainability.

**Non-Goals:**

- Adding streaming support to `errorHandlingInterceptor` or `accessLogInterceptor` (separate concern).
- Implementing retry logic or lazy provisioning in the frontend (future improvement).
- Finding the exact root cause of the backend panic (the nil guard and improved observability will make future panics diagnosable).

## Decisions

### Decision 1: Interceptor Chain Ordering

**Current order** (outermost → innermost):

```
[1] recoverHandler              ← defer recover() here
[2] errorHandlingInterceptor    ← AppErr → *connect.Error
[3] tracingInterceptor          ← OTel span start
[4] claimsBridgeInterceptor     ← authn info → auth.Claims
[5] accessLogInterceptor        ← logs after next() returns
[6] validationInterceptor       ← protovalidate
[7] handler
```

**Problems with current order:**

| # | Problem | Cause |
|---|---------|-------|
| 1 | Panic logs have no `trace_id` | recoverHandler [1] is outside tracingInterceptor [3] |
| 2 | Error logs have no `trace_id` | errorHandlingInterceptor [2] is outside tracingInterceptor [3] |
| 3 | Access log status shows `"unknown"` for AppErr | accessLogInterceptor [5] is inside errorHandlingInterceptor [2], sees unconverted AppErr |
| 4 | OTel span records raw AppErr message | tracingInterceptor [3] is inside errorHandlingInterceptor [2], leaks internal error details |
| 5 | Access log missing during panics | accessLogInterceptor [5] is inside recoverHandler [1], post-`next()` code is bypassed by stack unwind |

**New order** (outermost → innermost):

```
[1] tracingInterceptor          ← OTel span start; ALL inner layers get trace context
[2] accessLogInterceptor        ← sees *connect.Error (converted by [3]); has trace context
[3] errorHandlingInterceptor    ← AppErr → *connect.Error conversion; has trace context
[4] recoverHandler              ← panic recovery; has trace context; returns *connect.Error
[5] claimsBridgeInterceptor     ← authn info → auth.Claims
[6] validationInterceptor       ← protovalidate
[7] handler
```

**Why this order satisfies all constraints:**

- **Tracing outermost [1]**: `tracingInterceptor` starts an OTel span and passes an enriched `ctx` inward via `next(enrichedCtx, req)`. Every inner interceptor receives this `ctx` as a function argument, so all loggers calling `traceFromContext(ctx)` get `trace_id`/`span_id`. This resolves problems #1 and #2.
- **Access log at [2]**: On the response path (inner → outer), errors flow outward through [4] recoverHandler → [3] errorHandlingInterceptor (which converts `AppErr` to `*connect.Error`) → [2] accessLogInterceptor. By the time `accessLogInterceptor` sees the error, it is already a `*connect.Error` with a proper gRPC status code. This resolves problem #3. Being outside recoverHandler also means it is not bypassed during panics — the recover handler catches the panic and returns normally, so `accessLogInterceptor`'s post-`next()` code executes. This resolves problem #5.
- **Error handling at [3]**: Converts `AppErr` to `*connect.Error` before the response reaches `tracingInterceptor` [1], so span status records the sanitized gRPC code instead of raw internal error messages. This resolves problem #4.
- **Recover handler at [4]**: Inside tracing, so panic logs have trace context. Returns `*connect.Error(CodeInternal)` which flows normally through [3] and [2].
- **ClaimsBridge at [5]**: Depends only on `authn.Middleware` (HTTP layer, always runs first). No ordering constraint with tracing/logging.
- **Validation at [6]**: Innermost — validates before handler runs. Returns `*connect.Error(CodeInvalidArgument)` which flows through the full chain correctly.

**Alternative considered**: Moving `accessLogInterceptor` inside `errorHandlingInterceptor` but using `defer` for logging. Rejected because it requires modifying the external `go-logging` library, while reordering is a local change.

### Decision 2: Nil Guard in `userUseCase.Create`

Add a nil check on the `user` return value before accessing `user.ID`:

```go
if user == nil {
    return nil, apperr.New(codes.Internal, "repository returned nil user without error")
}
```

The concrete `rdb.UserRepository.Create` cannot return `(nil, nil)` (it pre-allocates the struct before SQL), but the use case depends on the `entity.UserRepository` interface. Any alternative implementation or mock could violate the contract. Defensive programming at the use case boundary prevents panics regardless of repo implementation.

### Decision 3: Frontend Error Handling

Change `provisionUser()` to re-throw non-`AlreadyExists` errors. The outer `catch` in `loading()` already handles errors by showing a message to the user. The current `// Do not throw` comment and behavior is the bug.

## Risks / Trade-offs

- **[Risk] Interceptor reorder changes error response shape for edge cases** → Mitigation: `errorHandlingInterceptor` and `recoverHandler` both produce `*connect.Error`, so the wire format is unchanged. The only difference is in log content (trace IDs added, status codes corrected).
- **[Risk] Frontend throwing on provisioning failure blocks signup for transient errors** → Mitigation: The user can retry by navigating back to the signup flow. Retry with backoff is a future improvement, not in scope here.
- **[Risk] `newRecoverHandler` position change may interact with `connect.WithRecover` internals** → Mitigation: `WithRecover` is just `WithInterceptors(&recoverHandlerInterceptor{...})`. Placing it as a separate `HandlerOption` after `WithInterceptors(...)` makes it the innermost interceptor via `chainWith` prepend semantics. Verified against connect-go v1.19.1 source.
