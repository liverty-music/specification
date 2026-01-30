# Design: Cloud SQL Provisioning

## Architecture

We will provision a **Cloud SQL for PostgreSQL** instance with the following specification, adhering to 2026 best practices:

- **Edition**: Enterprise (Standard edition, sufficient for early stage).
- **Version**: PostgreSQL 18 (Latest stable).
- **High Availability**: Enabled (Regional).
- **Tier**: `db-f1-micro` (Shared CPU, 0.6 GB RAM).
- **Storage**: 10 GB SSD (Minimum).
- **Protection**: Deletion protection enabled.

### Why Enterprise instead of Enterprise Plus?

Enterprise Plus is designed for high-performance workloads but requires larger minimum machine types. **Enterprise** edition allows for shared-core instances like `db-f1-micro`, which significantly reduces the starting cost while still providing production-grade reliability and the PostgreSQL 18 feature set.

## Networking

We will use **Private Service Connect (PSC)** for secure, private connectivity from the application (Cloud Run / GKE) to the database.

- **Why**: PSC avoids the complexity and CIDR overlap issues of VPC Native Peering.
- **Config**: A Service Attachment is created on the Cloud SQL side, and the application VPC connects via a PSC Endpoint.

## Security

- **Authentication**: IAM Database Authentication is MANDATORY.
- **Encryption**: Customer verification of Google-managed keys is sufficient (CMEK not required for this phase).
- **Public IP**: Disabled.

## Operations

- **Backups**: Automated daily backups (start 03:00 JST), retention 30 days.
- **Maintenance**: Scheduled window (Sunday 04:00 JST).
- **Observability**: Query Insights enabled with standard query string limits.

## Infrastructure as Code via Pulumi

New component: `src/components/gcp/database.ts`

- Resource: `gcp.sql.DatabaseInstance`
- Resource: `gcp.sql.Database` (default `liverty-music`)
- Resource: `gcp.sql.User` (IAM service account mapping)
