## Why

The frontend web app frequently crashes to a white screen when errors occur because there is no global error handler, no error boundary, and many async operations in lifecycle hooks lack try/catch. Users get no feedback, and developers get no error context. This change establishes comprehensive error handling infrastructure following Aurelia 2 official patterns, adds a one-click GitHub Issue error reporter, and integrates OpenTelemetry for distributed tracing.

## What Changes

- Add global error handlers via `AppTask.creating()` (`window.onerror`, `unhandledrejection`)
- Create an `ErrorBoundaryService` with `@observable currentError` for reactive error display
- Add error UI in the root component (`my-app`) with Error ID, "Copy Error Details", and "Report to GitHub" buttons
- Replace silent failures in lifecycle hooks (`loading()`, `canLoad()`) with proper error states using `promise.bind` template pattern
- Subscribe to `IRouterEvents` `au:router:navigation-error` for navigation failure handling
- Configure `restorePreviousRouteTreeOnError` in router
- Add a custom `ISink` for `ILogger` to capture errors structured for OpenTelemetry export
- Integrate `@opentelemetry/sdk-trace-web` with `instrumentation-fetch` for distributed tracing with the Go backend via W3C Trace Context (`traceparent` header propagation)
- Add Connect-RPC interceptor for gRPC error context capture
- Fix all identified silent failure points in services and routes

## Capabilities

### New Capabilities
- `frontend-error-handling`: Global error boundary, error UI components, error reporting (GitHub Issue creation), and error recovery patterns for the Aurelia 2 frontend
- `frontend-observability`: OpenTelemetry browser SDK integration for distributed tracing and error telemetry, custom ILogger ISink, and Connect-RPC instrumentation

### Modified Capabilities
- `frontend-onboarding-flow`: Add error handling to onboarding lifecycle hooks (loading sequence, artist discovery) that currently fail silently
- `typography-focused-dashboard`: Add error states and stale-data indicators to dashboard data loading
- `landing-page`: Add error handling to auth callback and welcome page redirect logic

## Impact

- **Frontend repo** (`liverty-music/frontend`): Major changes across services, routes, components, and main.ts
- **New dependencies**: `@opentelemetry/sdk-trace-web`, `@opentelemetry/instrumentation-fetch`, `@opentelemetry/exporter-trace-otlp-http`
- **Backend**: No changes required; existing OTEL setup already accepts `traceparent` headers
- **Infrastructure** (`cloud-provisioning`): May need OTEL Collector CORS configuration for browser OTLP/HTTP
- **Public GitHub repo**: Error reporter will create issues with structured error context
