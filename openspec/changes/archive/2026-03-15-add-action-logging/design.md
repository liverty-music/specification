## Context

The `addEmailClaim` Zitadel Action (`cloud-provisioning/src/zitadel/scripts/add-email-claim.js`) injects the `email` claim into JWT access tokens. Currently the script has no logging, making it impossible to determine whether the Action fires, succeeds, or fails silently on Zitadel Cloud.

## Goals / Non-Goals

**Goals:**
- Add diagnostic logging to `addEmailClaim` so execution is observable via Zitadel Cloud Console Events.

**Non-Goals:**
- Fixing the root cause of the missing email claim (that depends on what the logs reveal).
- Adding logging to other Actions or flows.

## Decisions

### Use `zitadel/log` module

**Choice**: `require("zitadel/log")` with `logger.log()` / `logger.warn()`.

**Alternatives considered**:
- `api.v1.claims.appendLogIntoClaims()` — embeds logs in the JWT. Useful but the current bug causes a 401 before the token reaches the frontend, so these logs would be invisible.

**Rationale**: `zitadel/log` writes to Zitadel's execution log, viewable in the Cloud Console Events UI regardless of whether the token is ultimately accepted by the backend.

### Log on both success and failure paths

- **Success path**: `logger.log()` with the email value — confirms the Action fired and the claim was set.
- **Failure path**: `logger.warn()` with `JSON.stringify(user)` — captures the actual `user` object structure to diagnose why `user.human.email` is falsy.

### Keep ECMAScript 5.1 compatibility

Zitadel Actions run in an ES5.1 runtime. No optional chaining (`?.`), no template literals, no `const`/`let`.

## Risks / Trade-offs

- **PII in logs**: The email address and user object will appear in Zitadel execution logs. Acceptable in dev; review before enabling in prod. → Mitigation: remove or reduce logging after the bug is resolved.
- **`JSON.stringify(user)` size**: The user object could be large. → Mitigation: only called in the failure branch, which is the diagnostic scenario.
