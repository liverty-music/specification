## Context

See proposal.md - Why. The current frontend (`main` on 2026-11-29, Aurelia 2.0.0-rc.2):

- `SearchController` (`src/routes/discovery/search-controller.ts`) debounces with its own `setTimeout` of 300 ms and sends any non-empty query. The route forwards query changes to it with `@watch('search.searchQuery')`.
- It drops a stale **success** by comparing the query, but not a stale **failure**: the `catch` publishes a snack and sets `searchResults = []`. No request is cancelled. In production at 22:39 JST on 2026-11-28 the search for `Furui` timed out 7 s after `Furui riho` had answered and erased its results.
- The result list shows the no-results message whenever it is not searching and has no results, so it would show it during any wait before the request.
- The fan snack bar already replaces a snack with the same `replaceKey` (`shared/ui/snack-bar/snack-bar.ts`).
- The RPC deadline is 10 s (`rpcTimeoutMs`); a failed call with NotFound reaches the screen as a `ConnectError`.
- The existing "stale response" test changes the query before the first request is sent, so two requests are never outstanding.

## Goals / Non-Goals

**Goals:**
- One request per query the fan stops on, and no trace of a superseded one.
- Search behaviour testable through the rendered components.

**Non-Goals:**
- The backend search latency (`verify-artist-mbid`).
- The admin console's artist search.
- The RPC deadline, the retry interceptor and the error snack's wording.

## Decisions

### D1: Debounce with `& debounce` on the input event, not on the value binding

The search bar binds `value.bind="search.searchQuery"` immediately and sends with `input.trigger="search.submit() & debounce:2000"`. The controller has two ways in:

| method | called by | sends in phase |
|---|---|---|
| `submit()` | the debounced input event | `waiting` |
| `searchNow()` | Enter in the search bar | `waiting`, `failed` |

So a failed query is sent again only on Enter, and a debounced call still pending after Enter, a failure or a clear does nothing: no flush signal is needed. Enter is ignored while `event.isComposing` is true or `keyCode` is 229. The input gets `enterkeyhint="search"`.

Alternatives: `value.bind="... & debounce:2000"` delays the query itself, so search mode, the clear button and the return to the bubbles would lag by 2 s. Keeping the controller's `setTimeout` duplicates what the framework's binding behavior does, including disposal on unbind. One `submit()` for both callers, with Enter flushing the debounce through a signal, would let a debounced input resend a failed query.

### D2: The controller observes its own query and holds one state

`searchQuery` becomes `@observable` on `SearchController`, replacing the route's `@watch`, so the bar, the controller and the list work the same in the route and in a component test. The controller holds one phase instead of `isSearching`:

| phase | meaning | the list shows |
|---|---|---|
| `idle` | empty, or a single half-width letter or digit | nothing |
| `waiting` | searchable, not sent yet | kept results, else loading |
| `searching` | request outstanding | kept results, else loading |
| `answered` | response or NotFound | results, else the no-results message |
| `failed` | any other failure | nothing |

A change of the trimmed query aborts the outstanding request and moves to `idle` (clearing results) or `waiting`. A change that leaves the trimmed query as it was does nothing. Search mode (`isSearchMode`) is on whenever the trimmed query is not empty, whatever the phase, so a single letter or digit hides the Artists view and shows an empty list. The single-character rule is `/^[A-Za-z0-9]$/` on the trimmed query. `dispose()` aborts the outstanding request. An outcome is applied only when its request's signal is not aborted.

Alternative: keeping booleans (`isSearching` plus flags for failed and below-minimum) allows combinations that mean nothing; the phase makes the list's three conditions exclusive.

### D3: Cancellation with `AbortSignal`

`SearchClient.search(query, signal)` passes the signal through `ArtistStore` to the Connect call. Cancelling also ends the request context in the Fan API. The transport already treats a cancelled call as no error.

Alternative: ignoring stale outcomes only leaves the requests running and loading the backend.

### D4: NotFound is mapped in the controller

The controller treats `ConnectError` with `Code.NotFound` as an answer with no artists, and reports it to analytics (`artist.search`, `result_count: 0`) as a completed search. Mapping it in the RPC client would put it outside the component test, which fakes the client.

### D5: One failure snack

The failure snack is published with `replaceKey: 'discovery-search-failed'`.

### D6: Component tests render the real components

A new jsdom fixture spec renders `discovery-search-bar`, `discovery-search-results` and the shared `snack-bar` around a real `SearchController`, fakes only `SearchClient` with responses the test resolves or rejects, controls time, and asserts on the input, the list, the status text and the snack. The search bar's story covers Enter and a composing Enter in a real browser (the `storybook` CI job). The controller unit spec keeps the state rules. Tests that call the removed route watch are rewritten.

## Risks / Trade-offs

- [Results appear at least 2 s after the fan stops typing] -> Enter sends at once. The delay is the owner's choice.
- [A single-letter or single-digit artist name cannot be searched] -> accepted by the owner; it stops one-letter searches registering many unrelated artists.
- [Mobile keyboards report Enter differently while composing, so the search key may be ignored or may send mid-conversion] -> the 2000 ms debounce still sends; the owner checks Japanese input on an Android phone (tasks 2.2).
- [A test clock may not drive the binding behavior's timer] -> task 1.1 settles how the fixture spec controls time before the scenarios are written.

## Migration Plan

Frontend only: merge, release, and the prod pin as usual. Rollback is the previous frontend release.
