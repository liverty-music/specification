# Zitadel User Account Sync — Approaches Research

Research conducted: 2026-02-15

## Problem Statement

When a user signs up via Zitadel, the identity is created in Zitadel's database but no corresponding record exists in the liverty-music application database. A synchronization mechanism is needed.

## Approaches Evaluated

### A. Zitadel Actions v2 (Webhook) — Push-based

```
┌──────────┐  user.human.added  ┌──────────────┐
│ Zitadel  │ ─────────────────► │ Backend      │
│          │   HTTP POST        │ /webhooks/   │
│          │   + Signature      │ user-created │
└──────────┘                    └──────┬───────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ Postgres │
                                 │ INSERT   │
                                 └──────────┘
```

Zitadel v2 Actions define external HTTP endpoints (Targets) that receive event POSTs.

- **Execution conditions**: `user.human.added`, `user.human.profile.changed`, etc.
- **Payload**: userID, email, displayName, createdAt, etc.
- **Signature verification**: `ZITADEL-Signature` header for integrity
- `interruptOnError: true` blocks Zitadel operations if webhook fails

**Configuration example**:
```json
// 1. Create Target
POST /v2/actions/targets
{
  "name": "sync-user-to-db",
  "restWebhook": { "interruptOnError": false },
  "endpoint": "https://your-backend/webhooks/zitadel/user-created",
  "timeout": "10s"
}

// 2. Create Execution
PUT /v2/actions/executions
{
  "condition": { "event": { "event": "user.human.added" } },
  "targets": ["<TargetID>"]
}
```

| Pros | Cons |
|------|------|
| Real-time sync | Requires hosting webhook endpoint |
| Language-agnostic | Event loss risk when endpoint is down |
| Signature verification for security | No documented retry/DLQ mechanism |

### B. First-Login Provisioning — Simplest

```
┌──────────┐  login   ┌──────────┐  token  ┌──────────┐
│  User    │ ───────► │ Zitadel  │ ──────► │ Frontend │
└──────────┘          └──────────┘         └────┬─────┘
                                                │
                                          JWT (sub, email, name)
                                                │
                                                ▼
                                          ┌──────────┐
                                          │ Backend  │
                                          │ if user  │
                                          │ not found│──► INSERT
                                          │ by sub   │
                                          └────┬─────┘
                                               ▼
                                          ┌──────────┐
                                          │ Postgres │
                                          └──────────┘
```

Auth interceptor checks if user exists by `sub` on every authenticated request. Auto-creates if missing.

| Pros | Cons |
|------|------|
| No additional infrastructure | DB query on every request |
| Self-healing (retries on next login) | User doesn't exist until first API call |
| Easy to test | Mixes auth and provisioning concerns |

### C. Event API (Pull-based Polling)

```
┌──────────┐                    ┌──────────────┐
│ Zitadel  │  POST /admin/v1/  │ Cron Job /   │
│ Event    │ ◄─────────────────│ Worker       │
│ Store    │  events/_search   │              │
└──────────┘                    └──────┬───────┘
                                       │
                                  filter: user.human.added
                                  since: last_checkpoint
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ Postgres │
                                 │ UPSERT   │
                                 └──────────┘
```

Zitadel is event-sourced. All events can be queried via the Admin API.

```json
POST /admin/v1/events/_search
{
  "asc": false,
  "limit": 1000,
  "creation_date": "2026-02-15T00:00:00Z",
  "aggregate_types": ["user"],
  "event_types": ["user.human.added"]
}
```

| Pros | Cons |
|------|------|
| No event loss — can backfill | Not real-time (polling interval) |
| Good for reconciliation | Requires checkpoint management |
| Works as fallback for webhooks | Requires Admin API access |

### D. Management API (User List Polling)

`POST /management/v1/users/_search` to periodically fetch the user list.

| Pros | Cons |
|------|------|
| Simple REST/gRPC API | Pull-based with latency |
| Good for batch sync/migration | No change detection (state only) |

### E. Actions v1 (JS) — Deprecated

JavaScript snippets running inside Zitadel with `TRIGGER_TYPE_POST_CREATION` trigger.

**⚠️ Scheduled for removal in Zitadel V5. Do not use for new implementations.**

### F. Hybrid Approaches

| Combination | Primary | Fallback | Characteristics |
|-------------|---------|----------|----------------|
| B + C | First-Login | Event API Polling | Simple + robust |
| A + C | Webhook | Event API Polling | Real-time + robust |
| B + A | First-Login | Webhook | Incremental adoption |

## Comparison Matrix

| # | Approach | Real-time | Impl Cost | Reliability | Zitadel Feature |
|---|---------|:---------:|:---------:|:-----------:|:---------------:|
| **A** | Actions v2 (Webhook) | Immediate | Medium | Low (endpoint failure risk) | Yes |
| **B** | First-Login Provisioning | On first API call | **Low** | High | No |
| **C** | Event API (Polling) | Polling interval | Medium | High | Yes |
| **D** | Management API (Polling) | Polling interval | Medium | Medium | Yes |
| **E** | Actions v1 (JS) | Immediate | Low | Medium | Yes (deprecated) |
| **F** | Hybrid (A+C or B+C) | Immediate | Medium-High | Very High | Yes |

## Decision

**MVP**: Client-side provisioning via OIDC `state` — Frontend detects signup via `state.isRegistration`, calls `GetOrCreate` RPC immediately in the callback. Simplest approach with zero additional infrastructure.

**Future**: Migrate to Zitadel Actions v2 Webhook for real-time, server-side provisioning. Add Event API polling as a reconciliation fallback.

## Zitadel First-Signup Detection Research

Additional research was conducted on whether Zitadel or OIDC standards can distinguish signup from login:

| Method | Feasibility | Notes |
|--------|-------------|-------|
| OIDC standard claims | Not possible | No standard `is_new_user` claim |
| Zitadel built-in claims | Not possible | No `urn:zitadel:iam:user:is_new` claim |
| UserInfo `created_at` | Not possible | Not exposed in UserInfo response |
| `prompt=create` callback | Not possible | Callback is identical to login |
| `oidc-client-ts` state | **Client-side only** | Pass custom state through OIDC flow |
| Actions v2 Complement Token | **Possible** | `user.creation_date` available in webhook payload |

The `oidc-client-ts` state approach was selected for MVP due to its simplicity.

## References

- [Zitadel Actions v2 Concepts](https://zitadel.com/docs/concepts/features/actions_v2)
- [Using Actions](https://zitadel.com/docs/guides/integrate/actions/usage)
- [Event API](https://zitadel.com/docs/guides/integrate/zitadel-apis/event-api)
- [OIDC Claims](https://zitadel.com/docs/apis/openidoauth/claims)
- [User Metadata](https://zitadel.com/docs/guides/manage/customize/user-metadata)
- [Management API](https://zitadel.com/docs/apis/resources/mgmt)
- [Migrate Actions v1 to v2](https://zitadel.com/docs/guides/integrate/actions/migrate-from-v1)
- [Complement Token Flow](https://zitadel.com/docs/apis/actions/complement-token)
