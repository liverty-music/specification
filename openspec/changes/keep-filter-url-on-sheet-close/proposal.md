## Why

Closing a concert's detail sheet always rewrites the URL to a bare `/dashboard`, even when the dashboard behind it is filtered. The filter stays on screen but leaves the URL, so a reload, a bookmark or a shared link drops it and shows a different timetable than the one the fan was looking at. It happens after a manual card tap on a filtered dashboard and after every `/concerts/:id` deep-link, whose whole purpose is to leave the fan on that artist's filtered timetable.

## What Changes

- Closing the detail sheet (light dismiss, swipe down, or its close control) returns the URL to the dashboard URL the fan was on when the sheet opened, query parameters included.
- A deep-linked sheet closes to `/dashboard?artists=<concert.artistId>`, the filter the deep-link derived.
- The browser-back path is unchanged: the browser already returns to the entry before the sheet's push.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `components/infrastructure/fan/web/route/dashboard`: "Concert Detail View" (dismiss scenarios revert to the URL the fan was on; new scenario for keeping filters in the URL) and "Deep-link auto-open of a concert detail sheet" (closing reverts to the filtered dashboard URL).

## Impact

- **Frontend only**: `event-detail-sheet` (remember the URL at open and restore it on close), plus unit and E2E tests. No API, proto or backend change.
