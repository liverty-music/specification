## Context

The Aurelia 2 frontend currently has no global error handling infrastructure. Errors in lifecycle hooks (`loading()`, `canLoad()`, `attached()`) propagate unhandled and crash the page to a white screen. Services silently swallow errors by returning empty arrays or `false`, leaving users with no feedback and developers with no diagnostic information.

The Go backend already uses OpenTelemetry for distributed tracing. The frontend repo is public on GitHub, making GitHub Issues a natural error reporting channel.

Current state:
- 38 try/catch blocks across 14 files, but inconsistent error recovery
- No `window.onerror` or `unhandledrejection` handlers
- No error boundary service or error UI components
- Toast service exists but is used sporadically
- `ILogger` is used for console logging but has no custom sinks

## Goals / Non-Goals

**Goals:**
- Eliminate white-screen crashes by catching all unhandled errors globally
- Provide actionable error UI with Error ID, copy-to-clipboard, and one-click GitHub Issue creation
- Establish `promise.bind` as the standard pattern for async data rendering in templates
- Integrate OpenTelemetry browser SDK for distributed tracing (trace propagation to Go backend via `traceparent`)
- Create a custom `ISink` for `ILogger` that bridges to OpenTelemetry spans
- Add Connect-RPC interceptor for gRPC error context capture
- Fix all identified silent failure points in services and route components

**Non-Goals:**
- Session replay (Sentry-like)
- Automatic error grouping or deduplication (backend observability concern)
- Source map upload pipeline (separate infrastructure task)
- Full OTEL Collector deployment (use direct OTLP/HTTP export initially)
- Sentry integration (OTEL-only for now, revisit if error reporting needs grow)
- Changing backend error response formats

## Decisions

### Decision 1: Global Error Handling via `AppTask.creating()`

Use Aurelia 2's `AppTask.creating()` lifecycle to register `window.onerror` and `window.addEventListener('unhandledrejection')` at app startup. These feed into an `ErrorBoundaryService` singleton.

**Why**: This is the officially recommended Aurelia 2 pattern. It integrates with the DI container and runs before any component renders.

**Alternative considered**: Manual setup in `main.ts` — rejected because it bypasses Aurelia's DI and lifecycle management.

### Decision 2: `ErrorBoundaryService` as Singleton with `@observable`

Create an `ErrorBoundaryService` registered as a singleton that:
- Captures errors with unique Error IDs (format: `ERR-{short-uuid}`)
- Maintains a circular buffer of recent errors (last 20)
- Uses `@observable currentError` for reactive UI binding in root component
- Tracks breadcrumbs (last 30 user interactions via click/navigation events)

**Why**: Aurelia 2's `@observable` enables reactive error display without manual subscription management. The root component (`my-app`) binds to `currentError` and conditionally renders the error banner.

### Decision 3: Error UI with GitHub Issue Integration

The error fallback UI displays:
1. Friendly error message
2. Error ID (`ERR-xxxxxxxx`)
3. "Copy Error Details" button — copies Markdown-formatted report to clipboard
4. "Report to GitHub" button — opens `github.com/liverty-music/frontend/issues/new` with pre-filled title and body containing Error ID, URL, timestamp, user agent, error message, and stack trace (redacted of auth tokens)
5. "Retry" / "Reload" buttons

**Why**: The frontend repo is public. One-click issue creation maximizes the chance developers receive actionable error reports. Markdown formatting ensures reports paste cleanly into GitHub.

**Alternative considered**: Custom error reporting endpoint — rejected as over-engineering for current scale. GitHub Issues provides built-in triage, labels, and notifications.

### Decision 4: `promise.bind` for All Async Data Loading in Templates

Replace imperative error handling in route components with Aurelia 2's declarative `promise.bind` template pattern wherever data is fetched and rendered.

```html
<div promise.bind="loadData()">
  <div pending><!-- skeleton/loading --></div>
  <div then.bind="data"><!-- render data --></div>
  <div catch.bind="error"><!-- error UI with retry --></div>
</div>
```

**Why**: This is Aurelia 2's native solution for async rendering. It handles pending/success/error states declaratively, eliminates the need for manual `isLoading`/`hasError` flags, and makes error handling visible in templates rather than buried in component code.

**Where NOT to use**: `canLoad()` guards that decide routing (these must remain imperative).

### Decision 5: Router Error Subscription via `IRouterEvents`

Subscribe to `au:router:navigation-error` in the root component to catch navigation failures. Configure `restorePreviousRouteTreeOnError: true` for production and `false` for development.

Add a fallback route for 404 handling.

**Why**: Type-safe `IRouterEvents` is the Aurelia 2 recommended approach over EventAggregator.

### Decision 6: OpenTelemetry Browser SDK with Fetch Instrumentation

Integrate:
- `@opentelemetry/sdk-trace-web` — core tracing
- `@opentelemetry/instrumentation-fetch` — auto-instrument fetch calls with `traceparent` header propagation
- `@opentelemetry/exporter-trace-otlp-http` — export spans via OTLP/HTTP

Configure `propagateTraceHeaderCorsUrls` to match the backend API domain so `traceparent` headers are injected into Connect-RPC requests.

**Why**: The Go backend already uses OTEL. Propagating `traceparent` from browser to backend enables end-to-end request tracing. Fetch instrumentation captures Connect-RPC calls automatically since Connect uses HTTP.

**Alternative considered**: Custom Connect-RPC interceptor only — rejected because fetch instrumentation provides broader coverage (any HTTP call, not just RPC).

### Decision 7: Connect-RPC Error Interceptor

Add a Connect-RPC transport interceptor that:
- Creates OTEL spans for each RPC call with `rpc.service`, `rpc.method` attributes
- Captures `ConnectError` code and message as span attributes
- Records exceptions on the span for error cases
- Feeds error context to `ErrorBoundaryService` for user-facing display

**Why**: Fetch instrumentation captures HTTP-level details but not Connect-RPC error codes or gRPC status. The interceptor adds RPC-specific context.

### Decision 8: Custom `ISink` for OpenTelemetry Bridge

Create an `OtelLogSink` implementing Aurelia 2's `ISink` interface that:
- Creates OTEL spans for `error` and `fatal` log events
- Attaches log context (scope, message, additional data) as span attributes
- Bridges Aurelia's logging system to OTEL without changing existing `ILogger` usage

Register alongside `ConsoleSink` in `LoggerConfiguration`.

**Why**: Existing code already uses `ILogger`. The sink bridge captures all logged errors into OTEL without modifying call sites.

## Risks / Trade-offs

- **Bundle size increase (~40KB gzipped)** for OTEL packages → Accept for now. Monitor with bundle analyzer. OTEL packages are tree-shakeable.
- **No error grouping without Sentry** → Accept. GitHub Issues serve as manual grouping. Revisit if error volume becomes unmanageable.
- **OTLP export requires CORS-enabled collector** → Initially export to the same backend domain via a proxy path, or use a lightweight collector sidecar in k8s.
- **`promise.bind` migration is incremental** → Not all templates need to change at once. Prioritize routes that currently white-screen (dashboard, artist discovery).
- **GitHub Issue spam** → Rate-limit the "Report to GitHub" button (debounce, max 1 per minute). Pre-fill body allows users to review before submitting.
- **Breadcrumb memory overhead** → Circular buffer of 30 entries is negligible. Entries are small (timestamp + action type + element selector).
