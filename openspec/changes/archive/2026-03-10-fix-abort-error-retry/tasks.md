## 1. Verify delay() behavior

- [x] 1.1 Read `delay()` method in `loading-sequence-service.ts` and confirm whether it sets `err.name = 'AbortError'` on the thrown error when the signal aborts
- [x] 1.2 If `delay()` does not set `err.name = 'AbortError'`, update it to throw an error with `name: 'AbortError'` for consistency with browser conventions

## 2. Add cancellation guard to getFollowedArtistsWithRetry

- [x] 2.1 Add `ConnectError` and `Code` imports from `@connectrpc/connect` to `loading-sequence-service.ts`
- [x] 2.2 Add cancellation check as the first statement in the catch block (before `attempt++`): re-throw immediately if `err.name === 'AbortError'` or `ConnectError` with `Code.Canceled`

## 3. Testing

- [x] 3.1 Add unit test: verify that `AbortError` is re-thrown immediately without retry
- [x] 3.2 Add unit test: verify that `ConnectError(Code.Canceled)` is re-thrown immediately without retry
- [x] 3.3 Add unit test: verify that retriable errors (e.g., `ConnectError(Code.Unavailable)`) still trigger retry with delay
- [x] 3.4 Run `make check` to verify lint and existing tests pass
