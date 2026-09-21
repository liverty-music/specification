## ADDED Requirements

### ~~Requirement: Private DNS zone for restricted.googleapis.com~~
**Superseded — see tasks.md 1.3.** The original plan created a separate `restricted.googleapis.com.` private zone, but Cloud DNS private zones do not follow cross-zone CNAMEs. The A record for `restricted.googleapis.com` was placed in the same `googleapis.com.` zone instead (PR #188). The living spec at `openspec/specs/private-google-access/spec.md` reflects the correct single-zone implementation.
