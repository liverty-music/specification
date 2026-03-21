## Why

Post-signup console logs reveal multiple issues degrading developer experience and user functionality: a 404 console error on initial UserService/Get for new users, a redundant Get RPC after user provisioning, an outdated BSR dependency causing TicketJourney runtime errors, excessive Aurelia Router debug logs flooding the console, mobile tap highlight on hype slider cells, and visible grid lines on the hype track.

## What Changes

- **Frontend**: Refactor `UserRpcClient.create()` to return the `User` from `CreateResponse.user` and cache it in `UserServiceClient._current`, removing the redundant second `ensureLoaded()` call after provisioning.
- **Frontend**: Update BSR dependency `@buf/liverty-music_schema.connectrpc_es` to latest version to include `TicketJourneyService.ListByUser` method.
- **Frontend**: Set `LogLevel` to environment-aware values (`debug` in dev, `warn` in prod) to suppress Aurelia Router internal `isMatch()` debug logs.
- **Frontend**: Add `-webkit-tap-highlight-color: transparent` to `reset.css` (`@layer reset`) to remove mobile tap highlight on hype slider and all interactive elements.
- **Frontend**: Remove the hype track `::before` pseudo-element grid line from `my-artists-route.css`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-account-sync`: Create flow caches user from CreateResponse, removing redundant Get RPC after provisioning.

## Impact

- **backend**: `user_handler_test.go` — new unit tests for Get handler.
- **frontend**: `user-client.ts`, `user-service.ts`, `auth-callback-route.ts` — create flow refactor.
- **frontend**: `package.json` / `package-lock.json` — BSR dependency update.
- **frontend**: `main.ts` — LogLevel configuration.
- **frontend**: `reset.css` — tap highlight reset.
- **frontend**: `my-artists-route.css` — track line removal.
