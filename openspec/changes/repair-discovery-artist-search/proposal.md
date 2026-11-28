## Why

On 2026-11-28 artist search on Discovery stopped returning results in production and filled the screen with error snacks. The backend timeouts that triggered it belong to the `verify-artist-mbid` change, but the screen turns them into a broken search on its own: every superseded search that fails still shows a snack and erases the newer results, a search with no match is reported as a network problem, and a search is sent 300 ms into a pause, even for a single letter.

## What Changes

- A search is sent 2000 ms after the fan's last input, or at once when the fan presses Enter (the keyboard's search key). The Enter that confirms a Japanese conversion does not send.
- A query of a single half-width letter or digit is not searched. Any other query of one character or more is (嵐, for example).
- A search the fan has moved past is cancelled, and nothing it returns or fails with reaches the screen. Clearing the query or leaving Discovery cancels it too.
- A search that finds nothing (NotFound) shows the no-results message, not an error.
- At most one search-failure snack is visible or waiting.
- While a search is waiting to be sent or is being answered, the screen shows a loading state, never the no-results message.
- Component tests drive the search through the rendered search bar, result list and snack bar, with only the search request faked.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: when a search is sent, which searches are sent, what happens to superseded ones, and what the fan sees while waiting, on no match and on failure.

`components/usecase/artist/search` and `components/entity/artist/search` are unchanged: the screen only changes how it calls the search and shows its outcome.

## Impact

- frontend: Discovery's search controller, search bar and result list; the artist search client (passes an abort signal); their tests and stories. The admin console's artist search is not touched.
- No proto, backend, database or infrastructure change. The backend timeout fix is made in `verify-artist-mbid` and this change does not depend on it.
