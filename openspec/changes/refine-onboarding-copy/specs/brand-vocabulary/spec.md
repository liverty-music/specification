## ADDED Requirements

### Requirement: Deprecated Colloquial Terms

The system SHALL maintain a registry of colloquial Japanese terms whose use in user-facing copy is forbidden in favor of entity-grounded vocabulary, and SHALL provide the canonical replacement guidance for each.

> **Enforcement model**: This requirement is normative (the `SHALL NOT` clauses below are binding on any change to JA user-facing copy). Until the `check-brand-vocabulary` lint script is extended to flag arbitrary banned tokens (currently it enforces `entity.*` JA/EN parity only — see Open Questions in this change's `design.md`), enforcement relies on (a) the registry below acting as the single source of truth and (b) reviewer attention during PR review. The follow-up to add automated token scanning is tracked separately and does not block any change that respects the rules.

#### Scenario: 推し is deprecated in favor of entity-grounded vocabulary

- **WHEN** authoring or reviewing JA user-facing copy in `frontend/src/locales/ja/translation.json`
- **THEN** the token `推し` SHALL NOT appear as a noun standing in for "artist a user follows"
- **AND** the noun SHALL be expressed as `アーティスト` (mapping to the protobuf `Artist` entity)
- **AND** the act of marking an artist as followed SHALL be expressed with the verb `フォローする` (mapping to the `FollowService.Follow` RPC semantics)
- **AND** typical surface forms SHALL follow these patterns:
  - CTA verb phrase: `アーティストをフォローする`
  - Outcome phrase: `フォローしたアーティストの<…>`
  - Possessive phrase: `好きなアーティストの<…>` (when the relationship has not yet been formalized as a follow)

#### Scenario: Registry of deprecated terms maintained in this spec

- **WHEN** this requirement is in effect
- **THEN** this spec SHALL list every deprecated colloquial JA term alongside its canonical replacement guidance
- **AND** the initial registry SHALL contain at least:
  - `推し` → noun `アーティスト` (Layer A, entity-grounded) + verb `フォローする`

#### Scenario: Adding a new deprecated term

- **WHEN** the team agrees that a previously-used JA colloquial term is no longer acceptable in user-facing copy
- **THEN** a row SHALL be added to this spec's deprecated-terms registry before or alongside the change that removes its remaining usages
- **AND** the row SHALL state the deprecated token and its canonical replacement guidance

## MODIFIED Requirements

### Requirement: Brand Expression Registry
The system SHALL maintain a single registry table in this spec listing every Layer B brand expression with its canonical JA and EN forms.

#### Scenario: Initial registry contents
- **WHEN** this spec is first introduced
- **THEN** the registry SHALL include the following Layer B expressions:
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME STAGE lane` — JA: `HOME STAGE` / EN: `HOME STAGE`
  - `NEAR STAGE lane` — JA: `NEAR STAGE` / EN: `NEAR STAGE`
  - `AWAY STAGE lane` — JA: `AWAY STAGE` / EN: `AWAY STAGE`

#### Scenario: Adding a new brand expression
- **WHEN** a new coined phrase is introduced into user-facing copy
- **AND** the phrase has no corresponding protobuf entity
- **THEN** a row SHALL be added to this spec's registry table before or alongside the change that introduces the phrase

#### Scenario: Removing a graduated expression
- **WHEN** a Layer B expression becomes entity-modeled and is migrated to Layer A
- **THEN** its row SHALL be removed from this spec's registry table in the same change that performs the migration

#### Scenario: Registry SHALL NOT include deprecated colloquial terms

- **WHEN** a colloquial JA term (such as `推し`) is identified as deprecated per the Deprecated Colloquial Terms requirement
- **THEN** the term SHALL NOT be listed in the Layer B brand expression registry
- **AND** the term SHALL instead be tracked in the deprecated-terms registry with its canonical entity-grounded replacement
