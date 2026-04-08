## 1. Billing Budget

- [x] 1.1 Add `gcp.billing.Budget` resource to `src/gcp/index.ts`, scoped to `liverty-music-dev` project, with ¥3,000/month budget and 50%/90%/100% email alert thresholds (dev-only, guarded by `environment === 'dev'`)
- [x] 1.2 Run `make lint` to verify TypeScript compiles without errors

## 2. Places API Quota Override

- [x] 2.1 Add `gcp.serviceusage.ConsumerQuotaOverride` for `places.googleapis.com` with daily limit of 20 requests in `src/gcp/index.ts` (dev-only)
- [x] 2.2 Verify the quota metric name and limit name are correct (`places.googleapis.com/v1/places_requests`, `PLACES_REQUESTS-DAILY-per-project`) — adjust if needed based on Pulumi plan output

## 3. Vertex AI Quota Override

- [x] 3.1 Add `gcp.serviceusage.ConsumerQuotaOverride` for `aiplatform.googleapis.com` with per-minute limit of 5 requests in `src/gcp/index.ts` (dev-only)
- [x] 3.2 Verify the quota metric name and limit name are correct for Gemini GenerateContent — adjust if needed based on Pulumi plan output

## 4. Deploy and Verify

- [ ] 4.1 Commit and push, open PR to cloud-provisioning
- [ ] 4.2 Merge PR and confirm Pulumi Cloud Deployments completes successfully for dev
- [ ] 4.3 Verify in GCP Console: billing budget visible under Billing → Budgets & Alerts
- [ ] 4.4 Verify in GCP Console: Places API quota override visible under IAM & Admin → Quotas (20 req/day)
- [ ] 4.5 Verify in GCP Console: Vertex AI quota override visible under IAM & Admin → Quotas (5 req/min)
