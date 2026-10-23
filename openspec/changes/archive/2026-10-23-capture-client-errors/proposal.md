## Why

An error in the fan app reaches the team today only if the fan copies the details or opens a GitHub issue. `ErrorBoundaryService.captureError` logs to the browser console, and the frontend exports no spans or logs, so the team never sees the error. The banner's "Report to GitHub" button sends a fan to the public `liverty-music/frontend` tracker. A fan rarely has a GitHub account, and the report they post (route, user agent, anything they add) becomes public. The button would also open a 404 once the repository turns private, which liverty-music/cloud-provisioning#665 prepares for.

## What Changes

- **Errors reach the team without the fan doing anything.** Every error the fan app captures (unhandled errors, unhandled promise rejections, navigation errors) is sent to the error-reporting service the app already uses for product analytics. Each report carries:
  - the Error ID and where the error came from;
  - the steps before it: screens visited, failed requests by method and code, and key actions by name;
  - the trace ID of the failing request, which leads to the backend's own logs;
  - minified stack frames resolved to source, using source maps uploaded at build time.

  The fan's analytics opt-out still applies: when analytics is off, nothing is sent.
- **The banner asks for one line by email.** It replaces the fixed copy 「問題が発生しました」 with the title 「⚡️ライブ中にアクシデント発生⚡️」 and a message saying the engineering team will look into it and an email would help. 「メールで状況を伝える」 is the first button and opens the fan's mail app; once tapped, the banner also shows the contact address for a device with no mail app. The Error ID is not shown on the banner.

  The email goes to the contact address the terms already publish. It is pre-filled with the Error ID (as お問い合わせ番号, inquiry number), the time and the screen. When the report was not sent, it also carries the error message and trace ID under 「調査用の情報」.
- **BREAKING (UI)**: the banner loses "Copy Error Details" and "Report to GitHub". The fan app no longer links to any public tracker.
- **Capture is more robust**:
  - another `window.onerror` handler keeps working, and the browser still logs the error;
  - an error with no `Error` object keeps its file and line;
  - an error's cause and non-`Error` rejection values are kept;
  - capturing never throws;
  - errors from browser extensions open no banner and are not reported;
  - the same error does not reopen a closed banner within 60 seconds.
- **Error reports follow the query rule with one exception.**
  - They keep the dashboard's `artists`, `journey` and `from` query values, which are needed to reproduce a filtered dashboard.
  - They still never carry a `ref` referral code; they say only whether one was present.
- **The team is told about new and returning problems.**
  - Each new or reopened problem posts to the Slack channel `#alert-frontend-prod`.
  - Ingestion is capped by project and per-problem rate limits and a billing limit.
- **The privacy policy names the new purpose**: 不具合の検出と修正 (detecting and fixing defects), and error reports as transferred data.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/error-banner`:
  - **Replaced**: "Error Banner UI in Root Component" becomes "Error banner offers reload, close and an email report", and "Error boundary service captures and sanitizes errors" becomes "Error boundary service captures errors and builds the report email". OpenSpec cannot drop or rename a scenario inside a MODIFIED requirement.
  - **Modified**: "Global Error Handler Registration" (no longer suppresses the browser's own error log, chains an earlier handler, skips browser-extension errors, keeps file and line), "Captured errors are stored and exposed for display" (the steps recorded, a repeated error does not reopen the banner) and "The banner's text comes from the app's catalog" (new title and the two messages).
  - **Added**: "Captured errors are reported to the team".
  - **Unchanged**: "Router Error Handling" and the cancelled-fetch requirement.
- `components/infrastructure/fan/web/global/analytics`: "Analytics events carry no query string of the app's own addresses" gains the error-report exception for `artists`, `journey` and `from` and the presence-only `ref`.
- `components/infrastructure/fan/web/global/legal-document`: "Privacy Policy discloses the actual data practices" adds error reports to the collected and transferred data, and 不具合の検出と修正 to the purposes.

## Impact

- **frontend**:
  - `src/services/global-error-handler.ts` and `src/services/error-boundary-service.ts`: capture, report and the email link.
  - `src/lib/analytics/analytics-service.ts`: exception capture and exception steps, and the query handling of exception events.
  - `src/services/grpc-transport.ts`: the trace ID of a failed RPC, and an RPC failure as a step.
  - `src/components/error-banner/`: the two banner variants.
  - `src/locales/{ja,en}/translation.json`: banner copy, email template, privacy policy and the analytics toggle description.
  - The `Dockerfile` and `.github/workflows/push-image.yaml`: source-map upload with `@posthog/rollup-plugin`.
- **cloud-provisioning**: a frontend Actions secret for the source-map upload key, and a runbook for the PostHog error-tracking settings and alerts.
- **PostHog project 190464** (configured by hand and documented in the runbook): rate limits, the billing limit, and two alerts to Slack.
- **Slack**: the new channel `#alert-frontend-prod`, with the PostHog app invited.
- **No backend or proto change.**
