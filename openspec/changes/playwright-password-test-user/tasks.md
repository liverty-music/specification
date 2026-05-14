## 1. Pulumi — provision password-based test user (cloud-provisioning)

- [ ] 1.1 Add an ESC secret for the test user's password targeting the dev environment only (`esc env set liverty-music/dev pulumiConfig.zitadel.e2eTestUser.password <value> --secret`); do NOT set it on `liverty-music/staging` or `liverty-music/prod`. Use `esc env set`, NOT `pulumi config set` — the project's ESC-vs-Pulumi-config protocol is documented in `cloud-provisioning/CLAUDE.md` (writing to the stack YAML risks committing the secret name to git history).
- [ ] 1.2 In `cloud-provisioning/src/zitadel/`, add a new component (e.g., `e2e-test-user.ts`) that creates a `zitadel.HumanUser` resource with `userName`, `firstName`, `lastName`, `email` (under the dev-only domain), `initialPassword` from the ESC secret, and `isEmailVerified: true` — without this flag Zitadel defaults to `false`, sends a verification email, and injects an email-verification step into the OIDC flow that the headless capture script cannot handle
- [ ] 1.3 In the same component, add a `pulumi.getStack() !== "dev"` synthesis-time guard that throws a clear `"E2E test user is dev-only"` error if the component is instantiated outside dev
- [ ] 1.4 Wire `ignoreChanges: ["initialPassword"]` on the resource so casual edits do not silently trigger replacement; document the `--replace` requirement for intentional rotation
- [ ] 1.5 In `cloud-provisioning/src/zitadel/components/frontend.ts`, expand the comment block adjacent to `LoginPolicy.userLogin: true` to cross-reference (a) the OpenSpec change `playwright-password-test-user`, (b) the dependency contract that the e2e-test-user's password sign-in works ONLY while this flag is `true`, and (c) the three revert-PR options from the design.md Risks table (remove `E2eTestUserComponent`, move user to a third org with its own LoginPolicy, or defer revert). Without the cross-reference, a future engineer reverting `userLogin` per Zitadel issue #11682's upstream fix has no visible warning that it silently breaks the headless capture path
- [ ] 1.6 Wire the component into the dev stack's Zitadel composition; verify `pulumi preview` shows the expected single create
- [ ] 1.7 Apply on dev (`pulumi up`); confirm the user appears in the Zitadel admin console under the dev project and that the `users` table in dev DB does NOT yet have a row for the new user (DB row is created lazily on first sign-in via the existing Create RPC)
- [ ] 1.8 Verify dev-only gating end-to-end by running `pulumi preview --stack staging` (or any non-dev stack) and confirming the preview shows NO `zitadel.HumanUser`-with-name-`e2e-test-password` resource in the diff. (The actual gating mechanism today is the outer `if (env === "dev")` check that skips Zitadel-component instantiation entirely on non-dev stacks — the synthesis guards inside `Zitadel` and `E2eTestUserComponent` are defensive depth that would only fire if the outer check is removed in a future refactor.)

## 2. Frontend — credentials handoff & gitignore

- [ ] 2.1 Verify `frontend/.gitignore` excludes `.auth/password.md` (and any other future password files under `.auth/`); if not, add the pattern. **Order matters**: do this BEFORE §2.2 so the password file cannot be accidentally tracked between write and gitignore-correction
- [ ] 2.2 Read the test user's password back from the ESC environment (`esc env get liverty-music/dev pulumiConfig.zitadel.e2eTestUser.password --show-secrets`) and write `frontend/.auth/password.md` locally; confirm `git status` does NOT list the file. **MUST use `esc env get`** (the ESC environment is the source of truth per Design D3), NOT `pulumi stack output` (the value isn't surfaced as a stack output and `pulumi config` writes elsewhere — see `cloud-provisioning/CLAUDE.md`)
- [ ] 2.3 Update `frontend/.auth/README.md` to document: (a) the dual test-user setup (passkey vs password), (b) how to retrieve the password from ESC, (c) which capture script to use for which user, (d) the WSL2 caveat

## 3. Frontend — headless capture script

- [ ] 3.1 Decide on the capture tool: try Playwright MCP first (per Design D2). Validate that it can output a Playwright-compatible `storageState.json` against `https://auth.dev.liverty-music.app`. If MCP cannot produce the storage-state shape directly, fall back to Playwright Node API in headless mode (driving Chromium via CDP without a display)
- [ ] 3.2 Add a new script under `frontend/scripts/` (e.g., `capture-auth-state-password.ts`) that: launches headless Chromium → navigates to the app → submits the email + password → completes the OIDC redirect → writes `frontend/.auth/storageState.json`
- [ ] 3.3 Expose the script via an `npm run auth:capture:password` package.json entry; ensure it exits non-zero on any auth failure (no silent 401 producing a broken storageState)
- [ ] 3.4 Add a smoke step inside the script: after writing storageState, replay it in a fresh browser context and assert that a known protected route (e.g., `/dashboard`) loads without redirecting to the landing page. Abort the script if the smoke fails
- [ ] 3.5 Run the capture script on the developer's WSL2 + WSLg host; confirm it produces a working `storageState.json` without any display server

## 4. Frontend — verify E2E suite passes

- [ ] 4.1 Run `npx playwright test` locally against the regenerated storage state; verify every existing test passes
- [ ] 4.2 If any test fails specifically because of the user-identity change (e.g., a test expected the passkey user's display name), update the test to be user-type-agnostic OR fork the test to cover both identities — do NOT silently mask the failure
- [ ] 4.3 Confirm `.auth/storageState.json` is NOT staged for commit (the entire `.auth/` directory is gitignored per the existing `e2e-auth-testing` "StorageState Gitignore" requirement); the file is locally regenerated by each developer via the capture script

## 5. Documentation & retention

- [ ] 5.1 Confirm `frontend/.auth/capture-auth-state.ts` (the existing headed passkey script) is untouched and the README clearly identifies it as the passkey path
- [ ] 5.2 Cross-link this change from `frontend/.auth/README.md`: "the password user provisioned by `cloud-provisioning/src/zitadel/e2e-test-user.ts` is the default for headless capture"

## 6. Archive prep

- [ ] 6.1 `openspec validate playwright-password-test-user` → passes
- [ ] 6.2 `openspec status --change playwright-password-test-user` reports `isComplete=true`
- [ ] 6.3 Close GitHub issue [liverty-music/frontend#345](https://github.com/liverty-music/frontend/issues/345) with a reference to the archive PR
- [ ] 6.4 `/opsx:archive playwright-password-test-user`
