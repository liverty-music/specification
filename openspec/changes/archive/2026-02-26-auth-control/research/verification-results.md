# Auth Control - Verification Results

## Environment

- Date: 2026-02-16
- Tool: Playwright MCP (unauthenticated browser session)
- Dev server: `http://localhost:5173`

## Frontend Route Guard

### Protected Routes (default-deny, no `data: { auth: false }`)

| Route | Expected | Result |
|---|---|---|
| `/dashboard` | Redirect to `/` | Redirected to `/` with toast notification |
| `/onboarding/discover` | Redirect to `/` | Redirected to `/` with toast notification |
| `/onboarding/loading` | Redirect to `/` | Not explicitly tested (same hook logic) |

### Public Routes (`data: { auth: false }`)

| Route | Expected | Result |
|---|---|---|
| `/` (welcome) | Display normally | Displayed normally |
| `/about` | Display normally | Displayed normally |
| `/auth/callback` | Display normally | Not explicitly tested (OIDC callback) |

### Auth Hook Behavior

- `AuthHook.canLoad()` correctly awaits `authService.ready` before checking auth state
- Unauthenticated users see a toast notification ("ログインが必要です") before redirect
- Routes with `data: { auth: false }` bypass the auth check entirely

## E2E Auth Testing Setup

| Requirement | Status | Notes |
|---|---|---|
| StorageState Capture Script | Done | `scripts/capture-auth-state.ts` created with 5-min timeout for manual OIDC login |
| StorageState Gitignore | Done | `.auth/` added to `.gitignore` |
| MCP Config with storageState | Done | `.claude/settings.json` committed with `--isolated --storage-state` flags |
| Playwright MCP navigates protected routes | Pending | Requires `npx tsx scripts/capture-auth-state.ts` (manual Zitadel login) to generate `.auth/storageState.json` |

## Bug Fix Verified

- **Issue #20**: `concert-service.ts` had a broken import (`{ transport }` instead of `{ createTransport }`). Fixed during this change. The dev server starts without import errors, confirming the fix.
