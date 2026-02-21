## Context

The frontend uses `oidc-client-ts` with Zitadel as the OIDC provider. Zitadel has a two-tier login policy hierarchy: Instance-level defaults and Org-level custom overrides. The Org-level policy (managed by Pulumi) correctly disables password login, but the OIDC authorization request does not include the org scope, causing Zitadel to fall back to Instance defaults where password login is enabled.

## Goals / Non-Goals

**Goals:**
- Ensure the OIDC login flow uses the Org-level custom login policy (passkey only)
- Make the org scope configurable via environment variable alongside existing Zitadel config

**Non-Goals:**
- Modifying the Instance-level default login policy
- Changing the Zitadel login UI or branding
- Implementing passkey registration flow changes

## Decisions

### 1. Add org scope to OIDC settings via environment variable

Add `urn:zitadel:iam:org:id:{orgId}` to the OIDC `scope` parameter. The org ID will come from a new `VITE_ZITADEL_ORG_ID` environment variable, keeping it consistent with how `VITE_ZITADEL_ISSUER` and `VITE_ZITADEL_CLIENT_ID` are already configured.

**Alternative considered**: Hardcoding the org ID — rejected because it differs per environment (dev/staging/prod).

### 2. Update cloud-provisioning comment only

The `allowExternalIdp: false` setting is already correct for passkey-only auth. Only the comment needs updating from "Temporarily disabled" to reflect the permanent intent.

## Risks / Trade-offs

- [Risk] If `VITE_ZITADEL_ORG_ID` is not set, the scope won't include the org and will silently fall back to Instance defaults → Mitigation: Document the required env var; the login flow will still work but with Instance policy.
