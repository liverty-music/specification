## Context

See proposal.md - Why. This extends the MVP `organizer-event-authoring`
capability (②) with richer authoring. All additions are additive on top of
the shipped ② data model and RPCs; no ② behavior changes. This is a backlog
change — captured now so the deferred scope is not lost, implemented when
demand appears.

## Goals / Non-Goals

**Goals:** competitor-parity authoring (media, streaming, JP structured
fields, password pages, per-event notes, lineup roles, scheduled publish)
as additive extensions.

**Non-Goals:** ticketing (④); co-organizer / sub-owner RBAC
(`organizer-rbac-subowners`); nice-to-haves not planned (祝い花, face-auth,
blocklist).

## Decisions

- **All additive.** New fields are nullable columns / new enum values /
  new join columns; no migration of existing ② data. `PASSWORD` is a new
  `Visibility` enum value; streaming mode is a new `Event`/`Series`
  attribute; performer role/order are new `event_performers` columns;
  per-event description is a new `Event` column; `publish_at` extends the
  publish flow.
- **Password gate reuses the unlisted read-path guard** (② already gates
  DRAFT/UNLISTED out of public queries); `PASSWORD` adds a verify step on
  the same read path.
- **Scheduled publish** runs the same publish transaction (supersede +
  `CONCERT.created`) from a timer instead of the manual action.
- **Streaming mode** relaxes the venue requirement for `online`; discovery
  treatment of online concerts is decided when this ships (Liverty is
  attendable-concert-first).

## Risks / Trade-offs

- **Scope can balloon** → keep each sub-feature independently shippable;
  this change may be split further when actually scheduled.
- **Online concerts vs the "attendable concert" product framing** →
  revisit discovery/notify rules for `online` at implementation time.

## Migration Plan

Additive proto + nullable columns; ship per the cross-repo release order.
Sequenced after ② is in production. May be split into smaller changes when
picked up.

## Open Questions

- Whether `online` concerts belong in the fan discovery feed at all
  (product framing) — decide when this change is scheduled.
