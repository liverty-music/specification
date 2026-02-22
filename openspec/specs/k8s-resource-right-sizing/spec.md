# k8s-resource-right-sizing Specification

## Purpose

Defines the resource request and limit policies for all Kubernetes workloads in the dev environment, targeting GKE Autopilot with Bursting support (v1.29+).

## Requirements

### Requirement: Dev environment resource requests use Autopilot Bursting minimums

All dev environment workloads with observed CPU usage below 50m SHALL set CPU request to 50m (GKE Autopilot Bursting minimum). Memory requests SHALL be set to 1.5-2x of observed peak usage, with a floor of 52MiB.

#### Scenario: ArgoCD components resource requests

- **WHEN** rendering the ArgoCD dev overlay manifests
- **THEN** all ArgoCD container CPU requests SHALL be 50m
- **AND** application-controller memory request SHALL be 128MiB
- **AND** repo-server, server, applicationset-controller memory requests SHALL be 64MiB
- **AND** redis, redisSecretInit memory requests SHALL be 52MiB

#### Scenario: External Secrets components resource requests

- **WHEN** rendering the external-secrets dev overlay manifests
- **THEN** controller CPU request SHALL be 50m with memory request of 64MiB
- **AND** webhook and cert-controller CPU requests SHALL be 50m with memory requests of 52MiB

#### Scenario: Backend server resource requests

- **WHEN** rendering the backend dev overlay manifests
- **THEN** server-app CPU request SHALL be 50m with memory request of 64MiB

#### Scenario: Frontend web-app resource requests

- **WHEN** rendering the frontend dev overlay manifests
- **THEN** web-app CPU request SHALL be 50m with memory request of 52MiB

#### Scenario: Reloader resource requests

- **WHEN** rendering the reloader dev overlay manifests
- **THEN** reloader CPU request SHALL be 50m with memory request of 64MiB

### Requirement: Resource limits provide burst headroom

All dev environment workloads SHALL have CPU limits set to 2-10x of request and memory limits set to 2-4x of request, providing headroom for burst usage without excessive reservation.

#### Scenario: Limits do not exceed original allocation

- **WHEN** rendering any dev overlay manifest
- **THEN** no container CPU limit SHALL exceed 500m
- **AND** no container memory limit SHALL exceed 512MiB
