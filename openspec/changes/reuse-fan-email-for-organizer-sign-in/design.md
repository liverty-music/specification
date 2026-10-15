## Context

See proposal.md - Why. Facts the approach rests on, checked against Zitadel v4.19.4 (the version prod runs, `cloud-provisioning/k8s/namespaces/zitadel/base/values.yaml:265`; source tag `v4.19.4`, commit `101343ad`) and in production on 2026-10-15:

- **User names are unique across the instance; emails are not.** A user name's unique key is the user name alone unless the organization's domain policy has `userLoginMustBeDomain`, which turns every login name into `<user name>@<organization primary domain>` (`internal/repository/user/user.go:29-38`). No constraint covers email (`internal/repository/user/human_email.go`). A user name may be any 1-200 characters, trimmed non-empty (`proto/zitadel/user/v2/user_service.proto:2005-2009`, `internal/command/user_human.go:98`), unless the part after its last `@` is another organization's verified domain (`internal/command/user_human.go:380-399`). `organizationScopedUsernames` exists only on unreleased `main`.
- **The identity provider documents two ways to sign in with an email**: the email as the user name (instance-unique), or "the email field of the user as additional login to the username ... no matter how the username of your user does look like", allowed by default (zitadel.com/docs/guides/solution-scenarios/configurations, "Use email to login").
- **Login v2** searches the typed value as a login name, within the organization when the request names one, then falls back to the email attribute within the same organization (`apps/login/src/lib/zitadel.ts:762-870`). When the organization's `ignoreUnknownUsernames` is on, it forwards the typed value, not the found user's login name, to the passkey step (`apps/login/src/lib/server/loginname.ts:313-315`), which recreates the session from that value (`apps/login/src/lib/server/session.ts:165-181`); the instance resolves a login name by user name only (`internal/query/user_by_login_name.sql`). A typed email that is not the user name therefore fails the passkey step ("Could not request passkey challenge").
- **Production verification on the existing Organizer's Organization (`org-01a124ae-…`, 2026-10-15)**: an identity with the owner's fan email `pepperoni9@gmail.com` was created there (no AlreadyExists), renamed to the user name `pepperoni9@gmail.com (XX Records)` (accepted), invited, given the `owner` grant and a passkey; with `ignoreUnknownUsernames` off, typing `pepperoni9@gmail.com` in the console opened with `?org_id=` signed in to that identity, shown as `pepperoni9@gmail.com (XX Records)`; the fan app still signed in to the fan account; the existing identity `pannpers+org-e2e@pannpers.dev` still signed in. With `ignoreUnknownUsernames` on, the passkey step failed. A sign-in with no organization named resolved to the fan account. The console then crashed after the callback (`AUR3500` on `/`), unrelated to this change.
- **Today's code**: `OrganizerUseCase.Create` calls `CheckOperatorEmailAvailable` (`backend/internal/usecase/organizer_uc.go:200-221`), an instance-wide search (`infrastructure/zitadel/organizer_provisioner.go:160-180, 639-670`); the Organization is named `org-<Organizer id>` (`organizer_provisioner.go:184-215`); `ensureHumanUser` lets the user name default to the email (`:578-632`); `ensureLoginPolicy` sets `IgnoreUnknownUsernames: true` (`:425-476`). The console takes `?org_id`/`?org` (both an Organization id) or localStorage, and with none signs in naming no organization (`frontend/organizer/main.ts:68-109`, `organizer/services/org-handle.ts`). The organizer server has no public procedures (`backend/internal/di/provider.go:514`); a token-bucket limiter exists (`internal/infrastructure/server/ratelimit`, `provider.go:697`).
- **Drift found**: the existing Organization's login policy has `hidePasswordReset` off, though the provisioner and the spec set it on.

## Goals / Non-Goals

**Goals:**

- A fan's email can be an Organizer's owner email; the person signs in to either account by typing that email and never types a user name.
- No organizer-console sign-in starts without naming an Organization; a new device reaches it by short name or by email.
- Organizations are identifiable at the identity provider (named by the short name).
- The structure stays the one later changes build on: owner-invited team members (identities and roles inside the Organizer's Organization) and per-Organizer SSO.

**Non-Goals:**

- Team members and roles beyond `owner`, per-Organizer SSO and domain routing (follow-ups).
- Renaming the tenant- and operator-named operations, proto and Go names (a method rename is a change of its own per the spec schema; done with the forbidden-word CI check).
- The console's post-sign-in crash (`AUR3500`; separate issue).

## Decisions

### D1 - Keep one Organization per Organizer, with separate accounts

Organizer identities stay in the Organizer's Organization; fan accounts in the product organization. This is the identity provider's B2B structure (one organization per business customer, with its own users, policies and IdPs), which per-Organizer SSO, per-Organizer policy and owner-managed teams need; and it keeps Organizer identities - which reach payouts - out of reach of the fan side (the fan API's identity-provider key is limited to the product organization, `cloud-provisioning/src/zitadel/components/machine-user.ts:94`; Organizer Organizations allow no self-registration).

**Rejected** (explored on 2026-10-15, reviewed by gpt-6-astra): one identity for fan and organizer with ownership in the database - the product organization's registration offers password sign-up whenever passkeys are allowed (`apps/login/src/components/register-form.tsx:160, 194-197`), the fan API's key could take over owners, and account deletion and recovery couple the two roles; one shared Organization for all organizers - no per-Organizer SSO or policy without moving identities later.

### D2 - User name `<email> (<short name>)`, sign-in by email

**Choice**: every identity Liverty Music creates in an Organizer's Organization gets the user name `<owner email> (<short name>)` and the email `<owner email>`; people type the email. The instance and the product and admin organizations are unchanged.

**Why**: it is the identity provider's documented "email as additional login" with the email shared across organizations; the user name is unique by construction (an email names at most one identity per Organization, and the short name is unique), readable where the hosted login and the passkey list show it, and never typed. The owner email is limited to 165 characters so the user name stays within 200.

**Rejected**: `userLoginMustBeDomain` on Organizer Organizations - verified in production, but the login name becomes `pepperoni9@gmail.com@org-…auth.liverty-music.app` and the instance default must be flipped with every other organization pinned first; `organizationScopedUsernames` - unreleased, and the instance resolves login names without an organization, so two identical user names would be ambiguous.

### D3 - Organizer Organizations report unknown emails

**Choice**: `ensureLoginPolicy` sets `IgnoreUnknownUsernames: false` (and keeps `DisableLoginWithEmail: false`).

**Why**: required for D2 (Context, verified). **Trade-off**: whether an email has an identity in one Organization becomes visible to someone who already holds the Organization's address (`?org=<short name>` or `?org_id`). The product organization keeps it on, so fan accounts stay hidden.

### D4 - The console always names the Organization; `?org=<short name>`

- `org-handle.ts` keeps `org_id` (an Organization id, as the invitation's return address uses) and changes `org` to mean a short name. With a short name, the console signs in with the scope `urn:zitadel:iam:org:domain:primary:<short name>.<identity provider domain>` - the Organization's generated primary domain (for example `admin.auth.liverty-music.app`, `liverty-music.auth.liverty-music.app`) - instead of `urn:zitadel:iam:org:id:<id>`, and remembers the short name. Task 0.3 verifies the scope pins the Organization, keeps email sign-in working and survives an Organization rename; if it does not, the fallback is a public `OrganizerService` lookup of the Organization id by short name (rate-limited like D5).
- With neither in the address nor on the device, `main.ts` routes to `find-organizer` and never calls `signIn()` (a sign-in naming no organization resolves to the fan account, verified).

### D5 - SendSignInLinks

- **Lookup**: `Organizer.ListByOwnerEmail` (`lower(owner_email) = lower($1) AND status = 2 ORDER BY name`), organizer server DB role (SELECT on `organizers`).
- **Mail**: `Organizer.SendSignInLinks` on the existing Postmark sender, Japanese template, one `https://organizer.liverty-music.app/?org=<short name>` per Organizer.
- **Public procedure**: `rpc.organizer.v1.OrganizerService/SendSignInLinks` in a new `auth.OrganizerPublicProcedures()` passed to `organizerAuthFunc`.
- **Limits**: per client, the existing `ratelimit` interceptor keyed by client IP for unauthenticated calls, 10 per 60 minutes, ResourceExhausted; per address, an in-process limiter in the usecase, 3 sends per 60 minutes, silently skipped. Per pod; `organizer-console-api` runs one replica.
- **Timing and errors**: the usecase answers after the per-address check and runs the lookup and the send in a background task with a detached context, so the outcome and the response time do not depend on the address; failures are logged.

### D6 - Short name, owner email, proto and schema

- Atlas migration: `organizers.short_name TEXT` with `CHECK (short_name ~ '^[a-z][a-z0-9-]{2,31}$' AND short_name NOT IN ('admin','liverty-music'))` and a unique index; `operator_email` renamed `owner_email` with `CHECK (char_length(owner_email) <= 165)`. The column is added nullable, the existing row is backfilled with the short name the owner chooses (task 6.1), then made `NOT NULL` in the same migration file or a follow-up one once the value is known (task 3.1 decides from 0.4).
- Proto: `entity/v1/organizer.proto` adds `message OrganizerShortName { string value = 1 [(buf.validate.field).string = { pattern: "^[a-z][a-z0-9-]{2,31}$", not_in: ["admin", "liverty-music"] }]; }` (owner decision 2026-10-15: the format is checked by protovalidate) and `OrganizerShortName short_name = 10` (OUTPUT_ONLY; set on admin and organizer reads, never on fan reads). `rpc/admin/organizer/v1` `CreateRequest`: `operator_email` → `owner_email` (field 2; BREAKING name change, merged with the `buf skip breaking` label as liverty-music/specification#1127 did) and `OrganizerShortName short_name = 3` (required). `rpc/organizer/v1`: `rpc SendSignInLinks(SendSignInLinksRequest{entity.v1.UserEmail email}) returns (SendSignInLinksResponse{})`. The entity and the DB repeat the format and the reserved words, so a caller that skips protovalidate is still refused.
- Go: `entity.Organizer.ShortName`, `OperatorEmail` → `OwnerEmail`; admin console: short name and owner email fields.

### D7 - Provisioning

- `EnsureTenantOrg` creates the Organization with the name `<short name>` and `FindTenantOrg` searches by it.
- `ensureHumanUser` sets `Username: "<owner email> (<short name>)"`; on AlreadyExists it searches the Organization by email and reuses the match; the instance-wide "email in use" branch and `listUsersByEmail`'s instance-wide mode are removed; `CheckOperatorEmailAvailable` is removed from the port, its three implementations, the mocks and `Create`.
- `ensureLoginPolicy` sets `IgnoreUnknownUsernames: false` and converges `HidePasswordReset: true` on existing policies (fixes the drift).

### D8 - The Organization entity

`components/entity/organization` is introduced with its Purpose and the sign-in rule. It has no table and no operations yet; the Organizer refers to it by `provider organizer ID`. The tenant-named operations move under it in the rename follow-up.

## Risks / Trade-offs

- [Organizer membership by email becomes visible to holders of an Organization's address] → D3; limited to one Organization per address; fan accounts stay hidden.
- [`?org=<short name>` scope does not behave as expected] → task 0.3 before group 5; fallback lookup in D4.
- [The user name does not follow an Organizer's later display-name change] → it uses the short name, which never changes.
- [A person typed their email on an identity-provider page that names no organization] → it resolves to the fan account; the console never opens such a page (D4).
- [SendSignInLinks abuse: mail bombing, enumeration by timing] → D5 limits and background send.
- [A background send is lost when the pod stops] → the person asks again.
- [In-flight `organizer-antisocial-vetting`] → touches `usecase/payout-account/get` with an ADDED block; whichever archives second re-validates.

## Migration Plan

1. **specification**: proto PR, Release, BSR gen.
2. **backend**: D6 migration (short name nullable), D7, D5; deploy. New Organizers get the new form at once.
3. **frontend**: D4, the find-organizer screen, admin short name field; deploy.
4. **Existing Organizer** (one in prod, task 6.1): the owner chooses its short name; set it in the row (break-glass SQL as `postgres`, per the cloud-sql runbook); rename its Organization to the short name and converge its login policy (`ignoreUnknownUsernames` off, `hidePasswordReset` on) through the Zitadel API; rename its identities' user names to `<email> (<short name>)`; delete the verification identity created on 2026-10-15 unless the owner keeps it; then the `NOT NULL` migration.
5. **Check in prod** (group 6).

Rollback: backend and frontend roll back by release; the identity-provider edits of step 4 are reversible through the same API calls.

## Open Questions

- None that change the plan. Task 0.3 decides between the primary-domain scope and the lookup fallback for `?org=`.
