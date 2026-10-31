# Hosted Login

## Purpose

The static Zitadel platform scaffolding for one Organization per Organizer:
a shared, actor-named `organizer-console` project (roles + apps) owned by the
product org, a dedicated provisioner machine user, and the login policy that
every Organizer's Organization, provisioned at runtime, must receive. Per-Organizer orgs,
the domain entity, the console, and the API server are separate changes.

## Requirements

### Requirement: Organizers' Organizations use a passkey-primary login policy with a designed recovery path

Every Organizer's Organization SHALL be given an **explicit** login policy — it SHALL NOT inherit the instance default (admin Google-IdP-only) policy. The policy SHALL make **passkeys the primary credential** and SHALL have this shape:

- `passwordlessType = PASSWORDLESS_TYPE_ALLOWED` — passkeys enabled and primary; the Organizer's members enroll a passkey on first sign-in.
- `allowUsernamePassword = true` — **local authentication is enabled.** Despite its name, this field gates ALL local authentication (user name or email plus **passkey** OR password), not only passwords: with it disabled, the hosted login renders no entry form and, with no external IdP configured, the invited person is left with an empty login card. Passkey-primary / "no passwords" is therefore expressed by `passwordlessType=ALLOWED` **plus never setting a password on an identity**, NOT by disabling local authentication.
- `allowRegister = false` — no open self-registration; identities are created by Liverty Music for vetted Organizers only.
- `allowExternalIDP = true` — permit OIDC federation so an Organizer that already has a workspace IdP can federate.
- `ignoreUnknownUsernames = false` — an email that names no identity in this Organization is reported as unknown. With it on, the hosted login passes the typed email, not the identity's user name, to the passkey step, and the identity provider cannot match an email to a user name of the form `<email> (<short name>)`, so a passkey sign-in typed by email fails (verified in production on 2026-10-15). What becomes visible is only whether an email has an identity in this one Organization, to someone who already holds the Organization's address; the product organization keeps hiding unknown emails.
- `disableLoginWithEmail = false` — people sign in by typing their email; their user name is never typed.
- `defaultRedirectUri = <organizer console origin>/?org_id=<Organization id>` — after the invited person completes credential setup via the invitation flow (which runs outside any in-flight OIDC request), the identity provider SHALL redirect them to the organizer console, from which the console completes sign-in.
- `allowDomainDiscovery` — **NOT required (off).**
- `hidePasswordReset = true` — the hosted login offers no password reset, its only self-service path to set a password while local authentication must stay enabled for passkeys.
- Check lifetimes set explicitly to the identity provider's instance defaults (Zitadel v4.19.4 `cmd/defaults.yaml`): password check 240h, external login check 240h, MFA init skip 720h, second factor check 18h, multi-factor check 12h. Omitted lifetimes are stored as 0, and the identity provider's console then refuses to save the policy ("Form contains invalid value(s).").

A **recovery path MUST exist** — passkey-only with **no** recovery is prohibited. Recovery SHALL be an **admin-initiated re-invite** (the system re-issues the person's invitation after out-of-band verification), optionally with an email magic-link/OTP self-serve fallback; any non-passkey fallback lane SHALL be step-up protected so it is not a weaker bypass. The policy SHALL NOT rely on a hard `allowLocalAuthentication=false` lockdown.

Synced passkeys (iCloud Keychain / Google Password Manager) survive single-device loss, so a second **hardware** authenticator is NOT mandated.

**The Organization is bound to the person's identity; an address only names which Organization's sign-in to open.** The single OIDC app serves all Organizers. The console names the Organization from `?org=<short name>`, `?org_id=<Organization id>` or the Organization remembered on the device, which selects that Organization's login policy and grants nothing; the token's Organization is authoritative. A person SHALL NOT be routed to a different Organization by supplying a different email, and a session belonging to a different Organization SHALL NOT satisfy an entry for this one (the console enforces the token's Organization — see `organizer-shell`).

#### Scenario: A provisioned Organization has the passkey-primary policy

- **WHEN** an Organizer's Organization is provisioned
- **THEN** it SHALL have an explicitly set login policy, not the inherited admin default
- **AND** the policy SHALL be passkey-primary with **local authentication enabled** (`passwordlessType=PASSWORDLESS_TYPE_ALLOWED`, `allowUsernamePassword=true`, `allowRegister=false`) and every identity SHALL be created with no password
- **AND** `allowExternalIDP` SHALL be enabled, `ignoreUnknownUsernames` SHALL be disabled and login with email SHALL be enabled
- **AND** `hidePasswordReset` SHALL be enabled, and every check lifetime SHALL be the instance default (240h, 240h, 720h, 18h, 12h), never 0, on a new policy and when an existing policy is converged on re-provisioning

#### Scenario: The policy renders a usable login and returns the member to the console

- **WHEN** an invited person reaches the Organization's hosted login
- **THEN** local authentication SHALL be available (no empty login card)
- **AND** after the person completes passkey setup via the invitation flow, the identity provider SHALL redirect them to the organizer console (`defaultRedirectUri`)

#### Scenario: Owner completes first login by enrolling a passkey

- **WHEN** Liverty Music creates a no-password identity and the person opens the invitation and enrolls a passkey
- **THEN** the person SHALL complete first sign-in by enrolling a passkey via the invitation flow
- **AND** on later sign-ins they SHALL type their email and use that passkey

#### Scenario: A recovery path exists for a lost passkey

- **WHEN** a person loses access to their passkey(s)
- **THEN** an admin SHALL be able to re-invite them (re-issue the invitation) after out-of-band verification
- **AND** a policy with no recovery path (passkey-only, no re-invite / no fallback) SHALL be rejected
- **AND** any non-passkey fallback lane SHALL be step-up protected

#### Scenario: Organization is resolved by org-pinned entry for every member

- **WHEN** any person (consumer / free-mail such as `gmail.com`, or a custom domain) signs in, whose email may also be a fan account's
- **THEN** the Organization SHALL be the one the console named and the person's own identity confirms, never one derived from the email domain
- **AND** a person SHALL NOT be routed into a different Organization by supplying a different address, and a session belonging to a different Organization SHALL NOT satisfy an entry for this one
- **AND** no per-Organizer domain verification SHALL be required for this path

#### Scenario: Email-domain discovery is a future optional enhancement

- **WHEN** a later change enables type-email-only routing for an Organizer that has a **verified** custom domain (typically alongside enterprise SSO)
- **THEN** that enhancement MAY route from the find-organizer screen by the verified domain
- **AND** it SHALL remain additive — the Organization named by the console stays the baseline
- **AND** this change neither requires nor implements domain discovery

### Requirement: Every console sign-in names one Organization

The organizer console SHALL start every sign-in tied to exactly one Organizer's Organization and SHALL never start a sign-in that names none, because such a sign-in matches the fan account of a person whose fan and Organizer emails are the same. After a sign-in, the console SHALL remember that Organization on the device and name it in the next sign-in there until an address names another. The sign-in screen SHALL ask for the email alone: it SHALL show no domain or other text after the email field, since people type their whole email.

#### Scenario: Owner whose email is also a fan account

- **WHEN** the owner of `xx-records`, whose fan account has the same email, opens `https://organizer.liverty-music.app/?org=xx-records` and types that email
- **THEN** they sign in with the passkey of their identity in xx-records' Organization, shown as `<email> (xx-records)`, not with the fan account

#### Scenario: Device that remembers no Organization

- **WHEN** the console is opened on a device with no remembered Organization and no Organization in its address
- **THEN** no sign-in starts and the find-organizer screen is shown

#### Scenario: Sign-in screen asks for the email alone

- **WHEN** the console opens the sign-in for `xx-records`
- **THEN** the email field shows nothing after it, such as `@xx-records.auth.liverty-music.app`, and the whole typed email signs the owner in

### Requirement: The invitation flow sets up no password

An invited person SHALL be able to set up a passkey as the only credential stored with their identity in the Organizer's Organization; signing in through an identity provider the Organization federates with stays available where the Organization has one. The hosted login SHALL offer no Password choice in the invitation flow or at first sign-in, and SHALL show its not-found page for any page that would set a password, also when that page's address is typed. The same hosted login serves fans, so the rules of the fan hosted login's "The hosted login offers no way to set a password" apply here unchanged.

#### Scenario: Invited person chooses a credential

- **WHEN** an invited person opens the invitation and the hosted login asks which credential to set up
- **THEN** Passkey is offered and Password is not, and after enrolling the passkey they arrive at the organizer console
- **AND** an identity provider the Organization federates with, if any, is still offered

#### Scenario: Set-password page opened by address

- **WHEN** an invited person opens the set-password page by typing its address
- **THEN** the hosted login shows its not-found page and no password is set
