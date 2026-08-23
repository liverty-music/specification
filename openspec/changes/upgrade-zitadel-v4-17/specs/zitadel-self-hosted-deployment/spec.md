## ADDED Requirements

### Requirement: Zitadel Version Upgrades Applied by Pinned-Tag Edit with Boot-Time Migration and Post-Upgrade Verification

The self-hosted Zitadel runtime version SHALL be upgraded by an explicit edit to
the pinned image tag in `k8s/namespaces/zitadel/base/values.yaml` — the API
server image `tag`, the Login V2 UI `login.image.tag`, and the OTEL
`service.version` resource-attribute label SHALL all move together to the same
target version in a single pull request. On rollout the new image SHALL run its
boot-time Cloud SQL schema migration (the chart `init`/`setup` job) to
completion before the `zitadel-api` Deployment reports ready, and the upgrade
SHALL be verified against the live OIDC + Login V2 surface before it is
considered done. While the `#10103` notification-deadlock upstream bug remains
unfixed, the watchdog cronjob SHALL be retained across the upgrade.

The current pinned version is **v4.17.1** (was v4.14.0). Because the dev
environment is intentionally stopped, this upgrade is applied **prod-direct**,
with the prod rollout gated on explicit operator approval; the same pinned-tag
edit procedure applies to dev when it is next started.

#### Scenario: Image tag and version label move together to the pinned version

- **WHEN** the rendered `k8s/namespaces/zitadel/base/values.yaml` is inspected
  after an upgrade
- **THEN** the API server image `tag` SHALL equal the target version (e.g.
  `v4.17.1`)
- **AND** the Login V2 UI `login.image.tag` SHALL equal the same target version
- **AND** the OTEL `service.version` resource attribute SHALL equal the same
  target version
- **AND** the change SHALL be an explicit edit in a pull request (not `latest`)

#### Scenario: Boot-time schema migration completes before the API is ready

- **WHEN** the upgraded Zitadel image first boots against the environment's
  `POSTGRES_18` Cloud SQL instance
- **THEN** the chart-rendered init/setup migration SHALL run and complete
  successfully
- **AND** the `zitadel-api` Deployment SHALL become ready only after the
  migration has completed
- **AND** if the migration fails, the documented rollback SHALL be to re-pin the
  previous version

#### Scenario: Post-upgrade OIDC and Login V2 verified in prod

- **WHEN** the upgrade has rolled out to the prod cluster
- **THEN** `https://auth.liverty-music.app/.well-known/openid-configuration`
  SHALL return the discovery document with `issuer` equal to
  `https://auth.liverty-music.app`
- **AND** the hosted Login V2 UI SHALL serve a real end-to-end sign-in (consumer
  and organizer console) on the new image
- **AND** the API SHALL NOT log `Errors.Instance.NotFound` for cluster-internal
  Login V2 calls (the `InstanceHostHeaders` / `x-zitadel-public-host` resolution
  is intact)

#### Scenario: Notification-deadlock watchdog retained while upstream bug unfixed

- **WHEN** the upgraded version still carries the unfixed `#10103`
  notification/projection deadlock
- **THEN** the prod `cronjob-watchdog-zitadel` SHALL remain deployed and active
  after the upgrade
