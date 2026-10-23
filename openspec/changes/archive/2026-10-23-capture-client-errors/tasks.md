## 1. Plan

- [x] 1.1 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"), staging only `openspec/changes/capture-client-errors`; verify `CI Success` (including `openspec-checks`) passes and the PR merges

## 2. cloud-provisioning — upload key and runbook (design D7, D10)

- [x] 2.1 Issue a PostHog personal API key scoped to project 190464 with the "Source map upload" preset (`error_tracking:write`, `organization:read`; design D7, which also records why a personal key is used), and store it in Pulumi ESC `liverty-music/prod` as `pulumiConfig.posthogSourcemapApiKey` through stdin (`--file - --secret --string`); verify `pulumi env get liverty-music/prod pulumiConfig.posthogSourcemapApiKey` lists the key without printing its value
- [x] 2.2 Add `POSTHOG_SOURCEMAP_API_KEY` to the frontend's repository-level Actions secrets in the prod stack (`repositorySecrets`, as the backend's Stripe sandbox secret is), and verify `pulumi preview` for prod shows exactly one new `github.ActionsSecret`
- [x] 2.3 Write `docs/runbooks/frontend-error-tracking.md` covering:
  - the key's scope and how to rotate it, with a pointer from `docs/runbooks/posthog-secret-rotation.md`;
  - the error-tracking billing limit (0 USD);
  - the project and per-issue rate limits;
  - the two Slack alerts to `#alert-frontend-prod`;
  - building without maps while PostHog is down;
  - adding a suppression rule.

  Verify `make check` passes.
- [x] 2.4 Open the cloud-provisioning PR citing `capture-client-errors` and merge it with `CI Success` green; after the owner runs the prod `pulumi up`, verify `gh secret list --repo liverty-music/frontend` lists `POSTHOG_SOURCEMAP_API_KEY`

## 3. Frontend — capture and report (error-banner "Global Error Handler Registration", "Captured errors are reported to the team"; design D1–D6)

- [x] 3.1 In `AnalyticsService`:
  - set `capture_exceptions: false`;
  - add `captureException(error, props): boolean` and `addExceptionStep(label, props)`, with the pre-init queue, immediate init on the first queued exception, the reported callback at flush, `false` when opted out or nil-config, and `try/catch`;
  - add the `$exception` branch of `before_send`: keep `artists`, `journey` and `from` on `$current_url`, strip other addresses as before, and redact tokens in `$exception_list[].value`.

  Cover it in `analytics-service.spec.ts`, with the scenarios "Error report on a filtered dashboard", "Error report on a referral link" and "Other events keep the dashboard filter out" annotated `@spec components/infrastructure/fan/web/global/analytics`; the existing four scenarios stay annotated. Verify `make test` passes.
- [x] 3.2 In `global-error-handler.ts`:
  - chain the earlier `window.onerror` and return `false`;
  - drop `preventDefault()` on `unhandledrejection`;
  - build an error value with file, line and column when there is no `Error` object;
  - pass the original rejection reason;
  - skip errors from extension addresses.

  Add tests annotated `@spec components/infrastructure/fan/web/global/error-banner` with "Unhandled synchronous error is caught", "Unhandled promise rejection is caught", "An earlier error handler keeps working", "Error without an error object keeps its location" and "Error raised by a browser extension". Verify `make test` passes.
- [x] 3.3 In `grpc-transport.ts`, record `{ traceId, spanId }` of a failed RPC in a `WeakMap` exported as `rpcSpanOf`, and add an `rpc` step `<Service>/<Method> <Code>`; cancelled RPCs add nothing. Verify with a transport test that a failing call yields the span's trace ID and one step.
- [x] 3.4 In `ErrorBoundaryService.captureError`:
  - call `captureException` with the original value and `error_id`, `error_source`, `has_ref`, and `$trace_id`/`$span_id` from `rpcSpanOf` (falling back to `cause`);
  - set `AppError.reported` and `AppError.traceId`;
  - keep the open banner for a repeat, and do not reopen a banner closed less than 60 seconds ago for the same message and source;
  - make `addBreadcrumb` forward to `addExceptionStep` with types `navigation`, `rpc` and `action`.

  Add tests annotated with "Error is reported with its Error ID and steps", "Failed request carries its trace ID", "Analytics off sends no report", "Error with a cause", "Rejection with a plain value", "Tokens are redacted from the report", "Reporting failure does not break the banner", "Report accepted after the banner opened", "Error is captured with context", "User dismisses error", "Breadcrumb tracking", "Same error does not reopen a closed banner" and "Same error does not replace the open banner". Verify `make test` passes.
- [x] 3.5 Add `action` steps at the call sites of `follow_artist`, `unfollow_artist`, `open_event_detail`, `start_checkout`, `submit_lottery_entry`, `start_sign_in`, `start_sign_up` and `change_consent` (design D8), each with a label only; verify `make test` passes and `grep -rn "addBreadcrumb('action'" src` lists the eight names

## 4. Frontend — banner and email (error-banner "Error banner offers reload, close and an email report", "Error boundary service captures errors and builds the report email", "The banner's text comes from the app's catalog"; design D9)

- [x] 4.1 Replace `generateReport` and `buildGitHubIssueUrl` with `buildReportMailto(appError)`:
  - the subject and body templates from translation keys;
  - the `調査用の情報` block only when the error was not reported;
  - `encodeURIComponent`, and a cap of 2,000 characters.

  Update `error-boundary-service.spec.ts` with "Capture error adds to history", "History is capped", "Sanitize redacts sensitive tokens", "Report email link is constructed correctly" and "Dismiss clears current error". Verify `make test` passes.
- [x] 4.2 Rewrite `error-banner.html` / `error-banner.ts`:
  - the title, the sent or not-sent message from `AppError.reported`, and お問い合わせ番号 with the Error ID;
  - ページを読み込み直す as the primary button, and 閉じる;
  - メールで状況を伝える as a link (sent) or a button (not sent), assigning the `mailto:` link to `window.location.href` with the 60-second cooldown;
  - remove the copy and GitHub buttons.

  Replace the `errorBanner` keys in `src/locales/{ja,en}/translation.json` with the copy in the spec and design D9, and add `errorReportEmail.*`. Verify `make lint` passes, including the i18n key check.
- [x] 4.3 Update `error-banner.spec.ts` with "Error banner renders with error details", "Email report is a link when the report was sent", "Email report is a button when the report was not sent", "Email report opens a pre-filled message", "Not-sent email carries the investigation details", "Sent email carries no technical details", "Unhandled error shows fixed copy", "English labels" and "Not-sent copy when analytics is off". No test may assert a GitHub URL. Verify `make test` passes.
- [x] 4.4 Update `error-banner.stories.ts` with named stories "Sent" and "Not sent" (no GitHub URL in the mocks), and a `play` function that clicks every button and link, annotated "Error banner buttons are interactive"; verify the Storybook component tests and visual baselines pass in the pinned Playwright container (`visual-baselines` skill)

## 5. Frontend — privacy policy and settings copy (legal-document "Privacy Policy discloses the actual data practices")

- [x] 5.1 In `legal.privacy` (`ja` and `en`):
  - add エラー情報（発生した不具合の内容、画面、その直前の操作） to section 2;
  - add 不具合の検出と修正 to section 3;
  - add error reports to the PostHog lines of sections 5 and 6, as data and purpose;
  - state in section 7 that turning off 使い心地の改善に協力する also stops error reports.

  Add one line on error reports to the product-analytics toggle description in Settings. Update the legal-document tests with the four scenarios of the requirement. Verify `make test` passes.

## 6. Frontend — source maps (design D7)

- [x] 6.1 Add `@posthog/rollup-plugin` (exact version) to `devDependencies` and to `vite.config.ts`, enabled only when `POSTHOG_SOURCEMAP_API_KEY` is set, with host `https://eu.posthog.com`, project `190464`, release name `liverty-music-frontend`, release version from `GIT_SHA` and `deleteAfterUpload: true`. Verify `npm run build` without the variable produces the same output as before and no `.map` file.
- [x] 6.2 In `Dockerfile`, take `GIT_SHA` as a build-arg and mount the key as a BuildKit secret for `npm run build`. In `push-image.yaml`, pass `secrets: posthog_sourcemap_key=${{ secrets.POSTHOG_SOURCEMAP_API_KEY }}` and `build-args: GIT_SHA=${{ github.sha }}`. Verify locally with `docker build --secret` that the image contains no `.map` file and `docker history` shows no key.

## 7. Ship and configure

- [x] 7.1 Open the frontend PR citing `capture-client-errors` and merge it with `CI Success` green; verify the main-push `push-image.yaml` run logs a successful source-map upload for the merge SHA
- [x] 7.2 Ask the owner to create the Slack channel `#alert-frontend-prod` and invite the PostHog app. In cloud-provisioning, declare the "issue created" and "issue reopened" alerts to that channel and exception autocapture off with the bridged PostHog provider (design D10), store the management key in ESC `liverty-music/prod` as `pulumiConfig.posthogManagementApiKey`, and merge the PR once the prod preview shows only the provider, the project settings and the two alerts; after the owner's prod `pulumi up`, verify both alerts with the PostHog MCP `error-tracking-alerts-list`. Set the error-tracking billing limit and the project and per-issue rate limits by hand per the runbook and record them there.
- [x] 7.3 After the next frontend release reaches prod, throw an error from the browser console on liverty-music.app with analytics on, and verify:
  - a new PostHog issue with a source-resolved stack, `error_id` equal to the banner's inquiry number, navigation steps and the release SHA;
  - a post in `#alert-frontend-prod`;
  - メールで状況を伝える opens a `mailto:pannpers@pannpers.dev` message;
  - with analytics turned off, the banner shows the not-sent copy and no `$exception` request leaves the browser.
- [x] 7.4 Apply the owner's banner copy and layout from the first prod check (design D9): title ⚡️ライブ中にアクシデント発生⚡️ and one message for both cases, メールで状況を伝える as the first primary button, no Error ID on the banner, and the contact address shown after the first tap. Update `errorBanner.*` in `ja` and `en`, the banner, `error-banner.spec.ts` and `error-banner.stories.ts` for the changed scenarios; verify `make check`, the Storybook tests, and after the release, that the prod banner shows the new copy and the address line
