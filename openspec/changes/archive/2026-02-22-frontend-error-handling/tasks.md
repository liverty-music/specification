## 1. Error Boundary Infrastructure

- [x] 1.1 Create `ErrorBoundaryService` with `@observable currentError`, error history buffer (20), breadcrumb buffer (30), `captureError()` and `dismiss()` methods
- [x] 1.2 Create `AppError` model class with Error ID generation (`ERR-{8-char-hex}`), message, stack, timestamp, source context, and route URL
- [x] 1.3 Create `GlobalErrorHandlingTask` using `AppTask.creating()` to register `window.onerror` and `unhandledrejection` handlers that feed into `ErrorBoundaryService`
- [x] 1.4 Register `GlobalErrorHandlingTask` and `ErrorBoundaryService` in `main.ts` Aurelia configuration

## 2. Error UI Components

- [x] 2.1 Create error banner component with Error ID display, "Copy Error Details", "Report to GitHub", "Dismiss", and "Reload Page" buttons
- [x] 2.2 Implement "Copy Error Details" — generate Markdown report (Error ID, timestamp, URL, message, stack trace, user agent, breadcrumbs, network errors) with auth token redaction, copy to clipboard
- [x] 2.3 Implement "Report to GitHub" — open `github.com/liverty-music/frontend/issues/new` with pre-filled title/body/labels query params, rate-limit to 1 per 60 seconds
- [x] 2.4 Add error banner binding to `my-app.html` using `if.bind="errorBoundary.currentError"`
- [x] 2.5 Create reusable inline error state component for use inside `promise.bind` catch blocks (error message + retry button)
- [x] 2.6 Create "Not Found" page component for router 404 fallback

## 3. Router Error Handling

- [x] 3.1 Configure `RouterConfiguration.customize()` with `restorePreviousRouteTreeOnError` (true for prod, false for dev)
- [x] 3.2 Subscribe to `IRouterEvents` `au:router:navigation-error` in root component, forward to `ErrorBoundaryService`
- [x] 3.3 Add fallback route configuration pointing to Not Found component
- [x] 3.4 Add breadcrumb tracking for route navigations via `au:router:navigation-end` event

## 4. Dashboard Error Handling

- [x] 4.1 Refactor `Dashboard` route to expose data loading as a bindable promise instead of imperative `loading()` hook
- [x] 4.2 Update `dashboard.html` template to use `promise.bind` with pending (skeleton), then (lane layout), and catch (error + retry) states
- [x] 4.3 Add empty state UI distinct from error state (no events found vs load failure)
- [x] 4.4 Implement stale-data display pattern — show previously loaded data with "Data may be outdated" warning banner on refresh failure
- [x] 4.5 Update `DashboardService.fetchFollowedArtists()` to throw on error instead of silently returning empty array

## 5. Onboarding Flow Error Handling

- [x] 5.1 Add try/catch to `ArtistDiscoveryPage.loading()` and refactor to use `promise.bind` in template for initial artist loading
- [x] 5.2 Add toast notification for similar artist API failure in `ArtistDiscoveryPage`
- [x] 5.3 Add toast notification and optimistic UI rollback for artist follow RPC failure
- [x] 5.4 Update `LoadingSequence` to display toast on partial data aggregation failure
- [x] 5.5 Update `LoadingSequence` to display error banner on complete data aggregation failure with retry action

## 6. Landing Page & Auth Error Handling

- [x] 6.1 Add error handling to `WelcomePage.canLoad()` — catch redirect target check failure, show error toast, allow manual navigation
- [x] 6.2 Verify `AuthCallback` error display is working (already has error UI) — ensure post-auth redirect failure is caught with fallback navigation

## 7. Service Error Cleanup

- [x] 7.1 Update `OnboardingService.isOnboardingCompleted()` to throw on error instead of silently returning `false`
- [x] 7.2 Update `LoadingSequenceService.aggregateData()` to return partial/full failure status instead of swallowing errors
- [x] 7.3 Add error handling to `SettingsPage` for push notification subscribe/unsubscribe calls
- [x] 7.4 Add error handling to `SettingsPage` for sign-out failure

## 8. OpenTelemetry Integration

- [x] 8.1 Install OTEL dependencies: `@opentelemetry/sdk-trace-web`, `@opentelemetry/instrumentation-fetch`, `@opentelemetry/exporter-trace-otlp-http`, `@opentelemetry/resources`, `@opentelemetry/semantic-conventions`
- [x] 8.2 Create OTEL initialization module — `WebTracerProvider`, `BatchSpanProcessor`, OTLP/HTTP exporter, resource attributes (service name, version)
- [x] 8.3 Configure `FetchInstrumentation` with `propagateTraceHeaderCorsUrls` matching backend API domain
- [x] 8.4 Register OTEL initialization in `main.ts` (before Aurelia startup)

## 9. Connect-RPC Instrumentation

- [x] 9.1 Create Connect-RPC transport interceptor that creates OTEL spans with `rpc.system`, `rpc.service`, `rpc.method` attributes
- [x] 9.2 Capture `ConnectError` code and message as span attributes on failure, call `span.recordException()`
- [x] 9.3 Register interceptor in `grpc-transport.ts` transport configuration

## 10. ILogger OTEL Sink

- [x] 10.1 Create `OtelLogSink` implementing `ISink` — create OTEL spans for `error`/`fatal` log events with scope, severity, and exception recording
- [x] 10.2 Register `OtelLogSink` alongside `ConsoleSink` in `LoggerConfiguration`

## 11. Verification

- [x] 11.1 Verify no white-screen crash on backend API failure (dashboard, artist discovery, loading sequence)
- [x] 11.2 Verify "Copy Error Details" produces valid Markdown with no auth tokens leaked
- [x] 11.3 Verify "Report to GitHub" opens pre-filled issue with correct repo URL
- [x] 11.4 Verify OTEL `traceparent` header is injected into Connect-RPC requests to backend
- [x] 11.5 Verify router 404 fallback displays Not Found page
- [x] 11.6 Run linter and fix any issues
