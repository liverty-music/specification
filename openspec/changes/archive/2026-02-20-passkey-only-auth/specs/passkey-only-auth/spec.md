## ADDED Requirements

### Requirement: OIDC authorization requests SHALL include org scope
The OIDC authorization request scope SHALL include `urn:zitadel:iam:org:id:{orgId}` so that Zitadel applies the Org-level custom login policy instead of the Instance-level default.

#### Scenario: Sign-in with org scope present
- **WHEN** the user clicks "Sign In" and `VITE_ZITADEL_ORG_ID` is configured
- **THEN** the OIDC authorization redirect includes `urn:zitadel:iam:org:id:{orgId}` in the scope parameter

#### Scenario: Sign-up with org scope present
- **WHEN** the user clicks "Sign Up" and `VITE_ZITADEL_ORG_ID` is configured
- **THEN** the OIDC authorization redirect includes `urn:zitadel:iam:org:id:{orgId}` in the scope parameter

### Requirement: Passkey-only login policy SHALL be enforced
When the org scope is included, Zitadel SHALL apply the Org-level login policy which disables password login and external IDPs, presenting only the passkey authentication option.

#### Scenario: No password form displayed
- **WHEN** the user is redirected to the Zitadel login page with the org scope
- **THEN** no password input form is displayed

#### Scenario: No external IDP option displayed
- **WHEN** the user is redirected to the Zitadel login page with the org scope
- **THEN** no external identity provider login option (e.g., Google) is displayed
