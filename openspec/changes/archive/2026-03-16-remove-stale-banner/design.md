## Context

The dashboard currently tracks an `isStale` flag that is set when `loadData()` fails but cached `dateGroups` exist. This drives a warning banner in the template and splits the catch block into two code paths (full error vs stale). Removing this simplifies the ViewModel, template, and styles.

## Goals / Non-Goals

**Goals:**
- Remove all stale banner UI, logic, and styles
- When a reload fails with cached data present, silently display the cached data
- Keep the full error state (inline-error) for first-load failures (no cached data)

**Non-Goals:**
- Changing the dashboard data loading strategy or caching layer
- Adding any replacement notification mechanism

## Decisions

### Silent fallback on reload failure

When `loadData()` fails and `dateGroups.length > 0`, the catch block will simply log the error and suppress the throw. The template catch branch only needs the `inline-error` path (for empty cache). The stale `<live-highway>` branch inside catch is removed because the `<live-highway>` in the `then` branch already rendered the cached data.

**Alternative considered:** Replace banner with a subtle toast notification. Rejected — even a toast implies something is wrong when the displayed data is still valid.

### Remove `retry()` method

`retry()` is only called from the stale banner's button. With the banner removed, `retry()` has no caller. The next `loading()` lifecycle call handles re-fetching automatically.

## Risks / Trade-offs

- **Truly stale data goes unnoticed** → Acceptable. Concert data changes extremely rarely. If a user needs fresh data, pull-to-refresh or page navigation triggers `loading()` again.
