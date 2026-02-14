# Deployment Strategy Documentation

This directory contains research and analysis documents related to deployment automation strategies for the Liverty Music platform.

## Documents

### [image-update-strategies.md](image-update-strategies.md)
Initial analysis of deployment automation options for dev and prod environments. Covers:
- Manual update workflow (current approach)
- GitHub Actions automation
- ArgoCD Image Updater
- Promotion-based workflow
- Comparison table and recommendations

**Context:** Solo developer, dev environment with multiple daily merges, prod with manual releases.

### [image-update-strategies-2026.md](image-update-strategies-2026.md)
Updated analysis based on latest 2026 CNCF and Kubernetes best practices. Includes:
- Flux CD built-in image automation (newly discovered)
- Kyverno policy-based image mutation
- Argo Rollouts for progressive delivery
- Latest Kubernetes imagePullPolicy best practices
- Comparison with official documentation sources

**Key Findings:**
- Flux CD has built-in image automation (vs. ArgoCD's external plugin)
- kubectl rollout restart recommended for simplicity (solo dev workflow)
- Semantic versioning essential for production
- imagePullPolicy: Always required for latest tags

## Related OpenSpec Changes

- [automate-dev-deployment](../../openspec/changes/automate-dev-deployment/) - Implementation of ArgoCD Image Updater based on this research

## References

- [ArgoCD Image Updater Documentation](https://argocd-image-updater.readthedocs.io/)
- [Flux CD Image Automation](https://fluxcd.io/flux/guides/image-update/)
- [Kubernetes Image Pull Policy](https://kubernetes.io/docs/concepts/containers/images/)
- [CNCF GitOps Tools Comparison](https://www.cncf.io/blog/2023/12/01/gitops-goes-mainstream-flux-cd-boasts-largest-ecosystem/)
