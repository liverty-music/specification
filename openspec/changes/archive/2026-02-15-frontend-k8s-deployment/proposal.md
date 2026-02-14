## Why

The Aurelia 2 frontend web application is currently not hosted anywhere and cannot be accessed by users or developers. To enable dev environment testing and future production deployment, we need to self-host the frontend on our existing GKE cluster using the same GitOps workflow as the backend.

## What Changes

- Add Kubernetes manifests for frontend namespace (Deployment, Service, HTTPRoute)
- Create multi-stage Dockerfile using Caddy web server to serve static assets
- Configure ArgoCD Application for automated frontend deployments
- Add GitHub Actions workflow for building and pushing frontend container images to Google Artifact Registry
- Configure Gateway API HTTPRoute for `dev.liverty-music.app` domain
- Set up SPA routing fallback (all routes → index.html)

## Capabilities

### New Capabilities
- `frontend-hosting`: Kubernetes-based hosting infrastructure for serving the Aurelia 2 SPA with automated GitOps deployment, container image builds, and HTTPS ingress

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- **cloud-provisioning repo**: New ArgoCD Application manifest, new frontend namespace manifests (deployment, service, httproute)
- **frontend repo**: New Dockerfile, Caddyfile, GitHub Actions workflow for image builds
- **GKE cluster**: New frontend namespace, new HTTPRoute binding to existing Gateway API
- **DNS/Certs**: Requires `dev.liverty-music.app` DNS record and TLS certificate configuration in existing cert-map
