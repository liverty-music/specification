## Context

See proposal.md (Why). Current state, observed in frontend `9d80c5f`:

- **Global handlers.** `GlobalErrorHandlingTask` (`AppTask.creating`) sets `window.onerror` and listens for `unhandledrejection` (`src/services/global-error-handler.ts`). It replaces any earlier `onerror`, returns `true` and calls `preventDefault()`, so the browser logs nothing. When there is no `Error` object it passes only the message string, so the file and line are lost.
- **Capture.** `ErrorBoundaryService.captureError` builds an `AppError` (`ERR-xxxxxxxx`), stores it and logs it. `logger.error` ends in `OtelLogSink`, which only records a span; the frontend exports no spans or logs (`src/services/otel-init.ts`: "No spans are exported"). Nothing reaches the team.
- **Breadcrumbs.** `addBreadcrumb` exists but has one caller, navigation in `app-shell.ts:330`.
- **Analytics.** `AnalyticsService` (`src/lib/analytics/analytics-service.ts`) is the single place that touches posthog-js (`^1.390.2`; 1.438 in current worktrees).
  - It loads PostHog lazily, on idle within 2 s, with a pre-init queue of 100.
  - It applies the analytics opt-out through `opt_out_capturing`.
  - It strips own-origin query strings in `before_send` (`stripOwnUrlQuery`).
  - `capture_exceptions` is not set, so a project-side toggle could turn exception autocapture on.
- **RPC tracing.** `otelInterceptor` (`src/services/grpc-transport.ts`) starts a span per RPC and records the `ConnectError`. `FetchInstrumentation` propagates `traceparent` to the API, and the backend's `otelconnect` interceptor exports the trace to Cloud Trace. So a frontend trace ID leads to the backend's trace and logs.
- **Image build.** The image is built once per main push in `push-image.yaml` (job environment `dev`) and retagged into prod on release. The bundle is env-agnostic.
- **PostHog.** EU project 190464 ("liverty-music-prod"). A Slack integration already exists (id 83774). The free tier covers 100k exceptions a month.

## Goals / Non-Goals

**Goals:**
- Each captured error reaches the team with enough context to act without the fan's help: source-resolved stack, steps, trace ID, release.
- The fan sees an honest statement of whether the team got it, and a one-tap email for the rest.
- The team is notified once per new or reopened problem, not once per occurrence.

**Non-Goals:**
- **Session replay.** It stays hard-disabled (analytics design Decision 12).
- **A support form or ticket system.** The email goes to the contact address in the terms.
- **Backend error tracking.** The backend already logs to Cloud Logging.
- **Capturing handled errors.** Errors that the `IConnectErrorRouter` or a component handles and shows to the fan are not sent; only what reaches `captureError` is.
- **A reverse proxy for PostHog ingestion.** See Risks.

## Decisions

### D1. PostHog Error Tracking, fed by `captureError`, with exception autocapture off

`ErrorBoundaryService.captureError` stays the single entry point. After building the `AppError` it calls `IAnalyticsService.captureException`. `AnalyticsService.init` sets `capture_exceptions: false` explicitly, so the PostHog project setting "exception autocapture" cannot add a second, Error-ID-less capture path.

Alternatives considered:
- **Sentry**, or another error tracker. It would add a second processor to the privacy policy and a second SDK to the bundle. PostHog is already a disclosed processor, and its Error Tracking groups issues, resolves source maps and alerts.
- **Exporting the frontend's OTel logs and spans** to Cloud Logging and Cloud Trace. That needs a public ingestion endpoint and gives no issue grouping, source-map resolution or "new issue" alert.
- **PostHog exception autocapture.** It bypasses `ErrorBoundaryService`, so the banner's Error ID would not be on the event, and it would double-capture what the handlers already catch.

### D2. `AnalyticsService.captureException` and the sent / not-sent state

`AnalyticsService` gains `captureException(error: unknown, props): boolean`.
- It returns `true` only when PostHog accepted the event: `posthog.captureException` returned a result. That result is `undefined` when capture is opted out, rate-limited by the SDK, or when the error was dropped as coming from an extension.
- In nil-config mode or when opted out, it returns `false`.
- Before init with analytics on, it queues the call in the existing pre-init queue and starts init right away, without waiting for idle. When the queued capture is accepted at flush, it calls back to mark the `AppError` reported.
- The whole method is wrapped in `try/catch`. A throwing SDK returns `false` and logs a warning.

`AppError` gains an `@observable reported: boolean`. The report email reads it to decide whether to carry the `調査用の情報` block, so an email built after a queued report is accepted carries no technical details. The banner shows the same copy either way (owner's decision, 2026-10-23, after the first prod check).

"Sent" means PostHog took the event into its send queue, not that the server stored it. That is as far as the browser can know without an acknowledgement round-trip (see Risks).

### D3. Handler and capture changes learned from posthog-js internals

These follow what posthog-js's own exception autocapture does:
- **Chain the earlier handler.** `window.onerror` keeps the previous handler and calls it first, then returns `false`. The `unhandledrejection` listener no longer calls `preventDefault()`. Both keep the browser console output that developers and the fan's devtools rely on.
- **Keep the location.** With no `Error` object, the handler builds an `ErrorEvent`-like value from message, filename, line and column, so PostHog gets a frame.
- **Pass the original value.** `captureException` receives the original value, not the stringified `AppError.message`. PostHog then walks `cause` chains and `AggregateError`, and records non-`Error` rejection values as they are.
- **Record the source.** Each event carries `error_source`: `unhandled_error`, `unhandled_rejection`, `router_navigation_error`, or the context string given to `captureError`.
- **Skip extension errors.** An error whose filename or top stack frame starts with `chrome-extension://`, `moz-extension://`, `safari-extension:` or `safari-web-extension:` is dropped before capture. PostHog also drops these, but the banner would still open without this check.
- **Do not reopen for a repeat.** `captureError` remembers the last banner error's message and source. A repeat while the banner is open does not replace it. A repeat within 60 s of the fan closing the banner does not reopen it. Both repeats are still stored and reported; the SDK's own limiter (bucket 10, refill 1 per second) bounds a loop.

### D4. Event properties

`$exception` events carry:
- `error_id`: the banner's Error ID, so an emailed inquiry number finds the issue by searching that property.
- `error_source`: see D3.
- `$trace_id` and `$span_id`: from the failing RPC (D6). PostHog links these to its trace view; for us they are the Cloud Trace ID.
- `has_ref`: `true` when the current address had a `ref` query key.

The release comes from the source-map plugin's injected chunk metadata (D7).

### D5. Query handling for `$exception` (spec analytics exception)

`before_send` branches on `event.event === '$exception'`. For `$current_url` only, it keeps the `artists`, `journey` and `from` keys and their values and removes the rest and the fragment. Every other address property (`$initial_current_url`, `$referrer`, `$pathname`) goes through the existing `stripOwnUrlQuery`. `has_ref` is computed in `captureError` from `window.location.search` before the URL is stripped.

These three keys are the dashboard's filter state (selected artists, journey stage, entry point). They are not personal and not referral data, and an error on a filtered dashboard cannot be reproduced without them. The same `before_send` branch also runs the existing token redaction (`ErrorBoundaryService.sanitize`, moved to a shared module) over each `$exception_list[].value`.

### D6. Trace ID of the failing RPC

`otelInterceptor` already holds the span when the RPC fails. In its `catch`, it records `{ traceId, spanId }` for the thrown error in a module-level `WeakMap<object, SpanIds>`, exported as `rpcSpanOf(err)`.
- `captureError` looks the error up, falls back to its `cause`, and puts the IDs on the event and on `AppError.traceId`.
- The same `catch` adds a failed-request step (D8) with the method (`<Service>/<Method>`) and the Connect code name.
- A `WeakMap` is used rather than a property on the error, so a frozen or foreign error object still works and nothing leaks into serialisation.

The active span at capture time is not used. An unhandled rejection runs outside the RPC's span context.

### D7. Source maps with `@posthog/rollup-plugin`

The Vite build adds `@posthog/rollup-plugin` (1.6.x) only when `POSTHOG_SOURCEMAP_API_KEY` is set. Local builds and PR CI builds are unchanged. Plugin settings:
- `host: 'https://eu.posthog.com'`
- `projectId: '190464'`
- `sourcemaps.releaseName: 'liverty-music-frontend'`
- `sourcemaps.releaseVersion`: the commit SHA, from the `GIT_SHA` build-arg
- `deleteAfterUpload: true`

With `deleteAfterUpload`, the maps are emitted as hidden and removed after upload, so the served image contains none. The SHA is not environment-specific, so the bundle stays env-agnostic. A prod release retags the same digest whose maps were uploaded at the main push. An "inherit" run reuses an earlier digest whose maps already exist.

The key is passed as a BuildKit secret (`secrets:` on `docker/build-push-action`, `RUN --mount=type=secret,id=posthog_sourcemap_key`), never a build-arg. A build-arg would remain in the image history. The key is a PostHog personal API key scoped to project 190464, with the key dialog's "Source map upload" preset: `error_tracking:write` and `organization:read`. posthog-cli's README lists only `error_tracking:write` for `sourcemap`, but PostHog's upload guides and the preset both include `organization:read`.

A personal key is a workaround, not the preferred credential. A CI credential should not depend on a user account, and PostHog's project secret API keys are built for that: project-scoped, not tied to a user, granted only the scopes chosen. In October 2026 they support only `feature_flag:read`, `endpoint:read` and `support_ticket:read`, and every source-map guide requires a personal key; PostHog documents no OIDC login for the CLI. Exit condition: when project secret API keys accept `error_tracking:write` for source-map upload, replace the personal key with one (runbook `frontend-error-tracking.md`). Until then, the key dies with its owner's account, which is acceptable while the owner is the only operator.

cloud-provisioning stores it as a repository-level Actions secret on `frontend`, from the prod stack's ESC environment. This is the same pattern as the backend's repository-level Stripe sandbox secret, since the key belongs to the prod PostHog project; a `dev` environment secret would place a prod credential in the dev stack.

If the upload fails, the build fails. A missing map shows up as unreadable stacks only after an error happens, so failing loudly at build time is preferred.

### D8. Steps (exception steps)

`ErrorBoundaryService.addBreadcrumb` keeps its local buffer (30) and also forwards to `IAnalyticsService.addExceptionStep(label, { type })`. The route stays in the local buffer only: a path such as `/events/<id>` holds an id, which a step must not carry, and the `$exception` event has its own `$current_url`. That calls posthog-js `addExceptionStep`; PostHog attaches its buffer to the next `$exception` (default on, 32,768-byte cap). Before init, steps go into the pre-init queue in order.

There are three step types:

| type | label | added in |
|---|---|---|
| `navigation` | screen name | `app-shell.ts` (exists) |
| `rpc` | `<Service>/<Method> <Code>` on failure | `otelInterceptor` (D6) |
| `action` | an action name | at the call site |

The action names start with: `follow_artist`, `unfollow_artist`, `open_event_detail`, `start_checkout`, `submit_lottery_entry`, `start_sign_in`, `start_sign_up`, `change_consent`. The local `click`/`custom` types are dropped. No step carries user-typed text, an id or a query string (spec).

### D9. Banner and email

- The banner drops "Copy Error Details" and the copied toast (`errorBanner.copied`, `errorBanner.copy`, `errorBanner.report`).
- `generateReport` (Markdown) is removed. `buildGitHubIssueUrl` becomes `buildReportMailto(appError)`.
- The link uses `encodeURIComponent` for subject and body. `URLSearchParams` encodes spaces as `+`, which mail apps show literally.
- The link is assigned to `window.location.href`. A `_blank` window for `mailto:` leaves an empty tab.
- The 60-second cooldown and its Snack carry over, with the new copy.
- `日時` is formatted with `Intl.DateTimeFormat` in the fan's locale and time zone, with the zone name.
- `画面` is `AppError.routeUrl` (pathname).
- In the not-sent case, the `調査用の情報` block adds `エラー：` (the sanitized message, first 200 characters) and `トレースID：` when one exists.
- The whole link is capped at 2,000 characters by shortening the error message further. Some mail apps refuse longer `mailto:` links.
- The email templates and all banner strings are translation keys (`errorBanner.*`, `errorReportEmail.*`) in `ja` and `en`.

The banner copy is the owner's (2026-10-23, after the first prod check): title ⚡️ライブ中にアクシデント発生⚡️ and one three-line message for both cases. メールで状況を伝える is the first, primary button, then ページを読み込み直す and 閉じる; the Error ID is not shown on the banner, since a fan has no use for it, and stays in the email. The email templates came from a Japanese UX writer brief (astra, `~/.cache/error-banner-copy/astra-output.md`); the not-sent technical lines are grouped under 「調査用の情報」.

On a device that opens no mail app, `mailto:` does nothing visible (observed in prod on the owner's browser, where typing the `mailto:` address into the address bar also did nothing). The page cannot detect this, so after the first tap the banner shows メールが開かない場合は、pannpers@pannpers.dev までご連絡ください。 (`errorBanner.emailFallback`).

### D10. Volume limits and alerts (PostHog project settings)

The settings the PostHog provider can hold are declared in cloud-provisioning; the rest are set by hand. `cloud-provisioning/docs/runbooks/frontend-error-tracking.md` records both and how to check them.
- **In code (prod stack, `src/posthog/components/error-tracking.ts`).** PostHog's official Terraform provider `PostHog/posthog` (1.0.25), bridged with `pulumi package add terraform-provider`, holds:
  - **Alerts.** Two `HogFunction`s (`internal_destination`, `template-slack`) send to the Slack integration (id 83774), channel `#alert-frontend-prod` by id: "issue created" (`$error_tracking_issue_created`) and "issue reopened" (`$error_tracking_issue_reopened`), with the message layout of PostHog's alert wizard. Spiking is not alerted: with no users, any recurrence is already a new or reopened issue.
  - **Exception autocapture off** at the project (`ProjectSettings.autocaptureExceptionsOptIn: false`), the project-side half of D1.
  - The provider authenticates with its own personal API key (`hog_function:write`, `project:write`, project 190464), `pulumiConfig.posthogManagementApiKey`, separate from the source-map key a CI build holds (D7's workaround note applies to it too).
- **By hand (no provider resource):**
  - **Billing limit for error tracking: 0 USD.** Ingestion stops at the free 100k a month instead of charging. With no users, a runaway loop is the only way to reach it.
  - **Rate limits.** A project-wide limit of 100 exceptions an hour, which caps a month at about 72k, under the free 100k, and a per-issue limit of 20 an hour, well below it so one looping issue cannot use the whole project budget and drop every other issue's exceptions.
- **Channel setup.** The owner creates `#alert-frontend-prod` and invites the PostHog app; this needs Slack admin rights. The Slack integration itself is made in the PostHog UI and referenced by id.

Alternative considered: alerts through the PostHog MCP or the UI, by hand. Fewer moving parts (no bridged provider, no second key), but a UI edit leaves no review trail and the runbook would be the only record of what the alerts are.

### D11. Spec deltas replace two requirements

OpenSpec 1.13.2 refuses a MODIFIED requirement that omits a scenario, and cannot rename one. So "Error Banner UI in Root Component" and "Error boundary service captures and sanitizes errors" are REMOVED and re-ADDED under new names. Unchanged scenarios are kept word for word; "Copy Error Details generates Markdown report" and the GitHub scenarios are dropped. Every ADDED or MODIFIED scenario needs an `@spec` test at archive, so the tasks annotate existing tests and add the missing ones.

## Risks / Trade-offs

- **[An ad blocker blocks `eu.i.posthog.com`]** → The SDK still accepts the event, so the report email omits the technical details while nothing arrives. The banner still offers the email. A managed reverse proxy (PostHog "managed proxy" on a subdomain of liverty-music.app) fixes this and is a follow-up proposal, not this change.
- **[An error during the first seconds of a visit]** → A report email built before PostHog loads carries the technical details. Init is started at once on the first error, so the report is normally accepted within a second.
- **[A render loop floods events]** → The SDK limiter (10 burst, 1 per second), the project and per-issue rate limits and the 0 USD billing limit cap it. The banner does not reopen for the same error within 60 s.
- **[A third-party script error with no stack]** → A "Script error." from another origin carries no frames. It is reported with `error_source` and steps only. If it becomes noise, a suppression rule in PostHog is the remedy, recorded in the runbook.
- **[An error message contains personal data]** → Messages come from code, not from the fan's input. Tokens are redacted, and the query rule removes URL values except the three dashboard keys. A message that interpolates an email would still be sent; review RPC error messages in the backend separately if one appears in PostHog.
- **[A source-map upload failure blocks a main-push build]** → Re-run the job. If PostHog is down for a long time, unset the secret to build without maps; the runbook notes this.
- **[The fan has no mail app configured]** → The button does nothing visible. After the first tap the banner shows the contact address (D9), which the terms also publish.

## Migration Plan

1. **Plan PR** (this change), then merge.
2. **cloud-provisioning PR.** Add the repository secret and the runbook. Then the owner runs the prod `pulumi up`, creates the Slack channel and invites the PostHog app.
3. **frontend PR.** Merge it; the main push builds the image and uploads the maps.
4. **Configure PostHog** per the runbook (limits, alerts), and check that an alert reaches Slack from a test exception.
5. **Release.** After the prod release, trigger an error from the browser console on liverty-music.app. Then confirm the issue in PostHog with a resolved stack, `error_id` and steps, the Slack alert, and the email link.

Rollback: revert the frontend PR. Events already sent stay in PostHog until its retention removes them.

## Open Questions

None. The rate limits were set on 2026-10-23 (D10) and the runbook records them.
