## Why

On 2026-04-03, a combination of `DeliverAll` NATS policy and `AckAsync` bug triggered an infinite message redelivery loop that called the Places API (New) continuously for 5 days, resulting in ¥323,198 in unexpected charges. There are currently no hard limits preventing a similar runaway cost event from any GCP API. We need infrastructure-level guardrails before re-enabling the Places API and as a permanent safeguard going forward.

## What Changes

- Add a Cloud Billing Budget for the `liverty-music-dev` project with email alerts at 50%/90%/100% of a monthly threshold
- Add a daily quota limit for Places API (New) Text Search: **20 requests/day** on the dev project
- Add a daily quota limit for Vertex AI API (Gemini GenerateContent): **50 requests/day** on the dev project

## Capabilities

### New Capabilities

- `gcp-cost-guardrails`: GCP billing budget alert and per-API quota limits for the dev project to cap runaway external API costs

### Modified Capabilities

<!-- No existing spec-level behavior changes -->

## Impact

- **cloud-provisioning**: New `BillingBudgetComponent` or inline resources added to `monitoring.ts` / `project.ts`; new `QuotaOverrideComponent` for Places and Vertex AI quotas
- **Backend behavior on quota exceeded**:
  - **Places API (New)**: Returns HTTP 429 → `pkg/api.FromHTTP` maps to `codes.ResourceExhausted` → `resolveVenue` returns error → `CreateFromDiscovered` fails for that message → Watermill retries up to poison queue
  - **Vertex AI Gemini**: Returns HTTP 429 → `gemini/errors.go` maps to `codes.ResourceExhausted` → `isRetryable` returns `true` → exponential backoff retries (max 3), then graceful degradation (returns nil, no concerts persisted for that artist)
- **No changes** to backend code, frontend, or proto schemas
