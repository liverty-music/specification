## Why

Venue reception (`ticket-wallet-and-checkin`) is an unauthenticated surface used from staff phones at the door, but it is hosted inside the organizer console on both sides:

- **Web.** The reception screen is a route of the organizer console app (`organizer.liverty-music.app/reception#<token>`, exempt from sign-in). It decodes untrusted input (QR text, the URL fragment) on the same origin whose `localStorage` holds the operators' OIDC tokens, so a script injection on the reception screen exposes console sessions on that browser.
- **API.** `ReceptionService` (Open, Admit) is mounted on the organizer Connect listener and exempted from its sign-in and org-scope checks by `OrganizerPublicProcedures()`. The organizer-console-api workload, its Cloud SQL role and its ingress host therefore serve both an unauthenticated device API and the operators' console. The role's grants carry the reception writes, and the 2026-10-08 privilege restriction (backend#558) narrowed the console role partly because of this co-location.

The decision was never recorded in `ticket-wallet-and-checkin`'s design. Doing it now, before that change's real-device checks and production E2E, keeps those checks on the final origin (camera permission and the device's non-extractable key are stored per origin) and costs nothing to migrate: no live event has used a reception link yet.

## What Changes

- **Reception web on its own origin.** The reception screen moves out of the organizer console app into a separate entry of the frontend build, served by its own web workload at `reception.liverty-music.app`; the reception guide (`ticket-wallet-and-checkin` task 7.2, not built yet) is built there too. The console no longer ships or routes the reception screen.
- **Reception API as its own workload.** `ReceptionService` moves from the organizer listener to a dedicated reception listener of the backend binary, exposed only by a new `reception-api` workload at `api.reception.liverty-music.app`, with its own service account, its own Cloud SQL IAM user and grants for exactly the reception reads and writes, its own CORS allowlist (the reception origin) and its own unknown-token throttle.
- **Organizer console without public procedures.** The organizer listener has no public procedures; every call passes the console sign-in and org-scope checks. The reception-only writes (binding a link to a device, a ticket's admitted time, admissions, rejected scans) are revoked from the organizer-console-api role.
- **Reception link URLs** point to the reception origin (`https://reception.liverty-music.app/#<token>`). Links issued before the switch stop working; none is in use.
- **`ticket-wallet-and-checkin` follow-ups**: its reception-links spec states the URL as `/reception#<token>` and is amended in that unarchived change; its real-device checks (4.6, 5.6), reception guide (7.2) and production E2E (7.3) run after this change is in production.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. No product behavior changes: the screens, the service contract (`rpc.organizer.reception.v1.ReceptionService`, unchanged) and the reception rules stay as `ticket-wallet-and-checkin` specifies them; only where they are hosted changes. The one requirement that names a URL shape (`components/infrastructure/organizer/web/route/reception-links`) is not in the main specs yet, so it is amended inside `ticket-wallet-and-checkin`. This change sets `skip_specs: true`.

## Impact

- **backend:** a reception Connect server (port, CORS, auth func with only the reception procedures public, unknown-token throttle) started alongside the others; `ReceptionService` and `OrganizerPublicProcedures()` removed from the organizer server; a grant migration for the `reception-api` IAM user and revoking the reception writes from `organizer-console-api`, with the grants integration test updated.
- **cloud-provisioning:** `reception-api` Deployment, Service, HTTPRoute, health check policy and service account (Workload Identity, Cloud SQL IAM user); `reception-web` Deployment, Service and HTTPRoute; DNS and certificates for `reception` and `api.reception`; the organizer API CORS allowlist unchanged, the reception API allowlist set to the reception origin.
- **frontend:** a `reception` entry (`reception.html`, `Dockerfile.reception`, `Caddyfile.reception`) built from the existing reception route, its transport pointed at the reception API; the route, guide and reception client removed from the organizer app; the reception-links screen builds URLs on the reception origin.
- **specification:** no proto change. Planning edits to `ticket-wallet-and-checkin` (one spec line, task ordering).
- **Out of scope:** an edge rate limit (Cloud Armor) for the reception API; offline reception; a Zitadel `reception` role.
