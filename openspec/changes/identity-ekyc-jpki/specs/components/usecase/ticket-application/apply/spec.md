## ADDED Requirements

### Requirement: Relationship to the ④ covered-ticket identity

**MVP:** the covered ticket is bound by ④ lottery-application's apply-time **本人確認
(self-declared name + contact)** (`ApplicantIdentity`); the verified identity supplies
the **per-person dedupe key (`User.id`)** but **not a verified name** in the MVP. This
satisfies the 特定興行入場券 requirement (チケット不正転売禁止法 does not mandate JPKI-level
name verification).

**POST-MVP:** where an event requires verification, the **verified 基本4情報 name**
(retrieved via the JPKI 署名用証明書 + Pocket Sign ConsentService) becomes authoritative
and ④'s self-declared name MUST be **consistent** with it (no conflicting name bound).
Its exact legal sufficiency is a legal-review item.

#### Scenario: Covered ticket is bound by ④'s self-declared identity (MVP)

- **WHEN** a verified person applies to a verification-required event
- **THEN** the covered ticket is bound by ④'s captured self-declared 本人確認 (name + contact), and the verified identity contributes the per-person dedupe key (`User.id`); verified-`基本4情報`-name consistency is a post-MVP enhancement
