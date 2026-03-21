## 1. Proto & Backend: UserService/Get empty response

- [x] ~~1.1-1.3 Backend empty response for Get~~ — Reverted: keeping NOT_FOUND behavior
- [x] 1.4 Add backend unit tests for Get handler (found + not-found cases)

## 2. Frontend: Create flow refactor

- [x] 2.1 Update `UserRpcClient.create()` in `user-client.ts` to return `User | undefined` from `CreateResponse.user`
- [x] 2.2 Update `UserServiceClient.create()` in `user-service.ts` to cache the returned user in `_current`
- [x] 2.3 Remove redundant second `ensureLoaded()` call in `auth-callback-route.ts` after provisioning (Create now caches the user)

## 3. Frontend: BSR dependency update

- [x] 3.1 Run `npm update @buf/liverty-music_schema.connectrpc_es @buf/liverty-music_schema.bufbuild_es` to pull latest BSR-generated code containing `TicketJourneyService.ListByUser`

## 4. Frontend: Console noise reduction

- [x] 4.1 Update `LoggerConfiguration` in `main.ts` to use `LogLevel.debug` in dev and `LogLevel.warn` in prod

## 5. Frontend: Hype slider visual fixes

- [x] 5.1 Add `-webkit-tap-highlight-color: transparent` to the universal reset selector in `reset.css` (`@layer reset`)
- [x] 5.2 Remove the `.hype-col:first-of-type > &::before` track line pseudo-element from `my-artists-route.css`
