## Why

On a signed-in cold load of Discovery, the similar-artist requests wait for the fan's follow list, which seeds them. The list answers at about 2.3 s on the reference setup (Slow 4G, 4x CPU), but the first `ListSimilar` goes out only at about 3.9 s: the follow-list answer waits on the main thread behind the app's start-up and the route's first render (long animation frames of 500–900 ms each), and the seeds can be chosen only after it (frontend#801). The first artist name comes at about 5.0 s, against 1.7 s for a guest, whose request needs no follow list.

## What Changes

- Each follow-list load of a signed-in fan keeps the followed artists' identity (id, name, MBID) on the device, for that account. Sign-out removes it.
- When the app opens on Discovery and a kept list exists for the signed-in account, the start-up initial load chooses its seeds from the kept list at once, in parallel with this session's follow list, instead of after it.
- The field keeps excluding the artists in the current follow list when it is set, so an artist followed since the list was kept is still not shown once this session's list has arrived. Without a kept list (first start on the device, other account) the load waits for the follow list as now.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: "Discovery bubble pool caching on re-entry" — the start-up scenario chooses a signed-in fan's seeds from the follows kept on the device when there are any; a new scenario covers the kept list.

## Impact

- **frontend only.** No proto, backend or infrastructure change.
- `src/adapter/storage/followed-artists-storage.ts` (new), `src/services/follow-store.ts`, `src/services/artist-bubble-store.ts`, `src/services/discovery-prefetch-task.ts`.
