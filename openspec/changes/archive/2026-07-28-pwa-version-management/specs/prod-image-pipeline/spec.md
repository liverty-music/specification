## ADDED Requirements

### Requirement: The pin-bump workflow SHALL write `releaseVersion` to the frontend config.json ConfigMap

When the `bump-prod-pin.yml` workflow in `cloud-provisioning` processes a `frontend` component pin-bump event (dispatched by the frontend `push-image.yaml` release path), it SHALL also update the `releaseVersion` field inside the `config.json` JSON blob embedded in the `web-app-runtime-config` ConfigMap YAML file (`k8s/namespaces/frontend/overlays/prod/configmap.yaml`). The value written SHALL be the full release tag including the `v` prefix (e.g., `"v1.26.0"`). The `releaseVersion` field format (optional string, `v`-prefixed semver) is defined in the `frontend-runtime-config` capability spec — that spec is the single source of truth for the field's schema and absence-tolerance contract; this spec governs only the write-side workflow invariant. The update SHALL occur in the same commit as the `kustomization.yaml` image-pin rewrite, so the ConfigMap and the image tag are always in sync.

#### Scenario: Pin-bump commit includes releaseVersion update

- **WHEN** the `bump-prod-pin.yml` workflow runs for `component=frontend` with `tag=v1.26.0`
- **THEN** the workflow SHALL update `releaseVersion` in `k8s/namespaces/frontend/overlays/prod/configmap.yaml` to `"v1.26.0"`
- **AND** the `kustomization.yaml` image tag rewrite SHALL be in the same commit
- **AND** the resulting PR SHALL include both file changes together

#### Scenario: releaseVersion in configmap matches kustomization image tag after pin-bump

- **WHEN** inspecting the merged cloud-provisioning prod overlay after a frontend release
- **THEN** the `releaseVersion` value in `k8s/namespaces/frontend/overlays/prod/configmap.yaml` SHALL equal `"v<X.Y.Z>"`
- **AND** the `newTag` in `k8s/namespaces/frontend/overlays/prod/kustomization.yaml` for `web-app` SHALL equal `v<X.Y.Z>`
- **AND** both values SHALL reference the same release

#### Scenario: No-downgrade guard also protects releaseVersion write

- **WHEN** the `bump-prod-pin.yml` no-downgrade guard blocks the pin-bump (incoming tag is lower than current)
- **THEN** the `configmap.yaml` `releaseVersion` field SHALL NOT be modified
- **AND** the workflow SHALL fail before writing any file change
