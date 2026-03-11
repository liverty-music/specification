## Context

The hype tier system uses four values: `watch`, `home`, `nearby`, `anywhere`. The "Anywhere" tier was introduced in the `rename-passion-to-hype` change as a replacement for `must_go`. The term "Away" better communicates the user's willingness to travel away from home and creates a cleaner tier progression: Watch → Home → Nearby → Away.

This rename touches all layers: proto enum, Go constants, database stored values, frontend enum references, and i18n labels. The wire format (proto enum number 4) is unchanged.

## Goals / Non-Goals

**Goals:**
- Rename `HYPE_TYPE_ANYWHERE` → `HYPE_TYPE_AWAY` in proto
- Rename `HypeAnywhere` → `HypeAway` and `"anywhere"` → `"away"` in Go
- Migrate database stored values from `'anywhere'` to `'away'`
- Update frontend enum references and i18n keys
- Update spec documents to use "Away" terminology

**Non-Goals:**
- Changing tier semantics or notification behavior
- Modifying the proto enum numeric value (stays at 4)
- Updating archive files (historical records remain as-is)

## Decisions

### 1. Database migration strategy: single UPDATE + constraint swap

A new migration renames stored values in-place:

```sql
UPDATE followed_artists SET hype = 'away' WHERE hype = 'anywhere';
ALTER TABLE followed_artists ALTER COLUMN hype SET DEFAULT 'away';
-- Drop old CHECK, add new with 'away'
```

**Alternative**: Add `'away'` as an accepted value alongside `'anywhere'`, deprecate later.
**Rationale**: Clean cut is simpler. The rename is atomic within a transaction. No dual-value ambiguity.

### 2. Proto enum: rename value name, keep number

```proto
HYPE_TYPE_AWAY = 4;  // was HYPE_TYPE_ANYWHERE
```

Wire compatibility is preserved (number 4 unchanged). This is a breaking change in generated code names only.

**Alternative**: Add `HYPE_TYPE_AWAY = 5` as a new value and deprecate `HYPE_TYPE_ANYWHERE`.
**Rationale**: Adding a new numeric value creates mapping complexity and a permanent deprecated enum value. Since this ships as a coordinated release (specification → backend → frontend), a clean rename is preferable.

### 3. Cross-repo deployment order

Same pattern as the parent `refactor-follow-entity` change:

```
1. specification PR → merge → Release → BSR gen
2. backend PR (includes DB migration + code rename)
3. frontend PR (enum reference + i18n updates)
```

The backend migration must run before the new code deploys. Atlas Kubernetes Operator handles this via sync wave ordering.

### 4. i18n key rename: `hype.anywhere` → `hype.away`

Both the key and any labels/descriptions referencing "Anywhere" are updated. The Japanese label `遠征OK` remains unchanged since it already conveys the "Away" meaning.

## Risks / Trade-offs

- **Breaking proto change** → Coordinated release across 3 repos. Mitigated by the established release process (specification first, then downstream).
- **Data migration on live table** → Single UPDATE statement on `followed_artists`. Low risk: the table is small and the update is indexed. Rollback: reverse migration (`'away'` → `'anywhere'`).
