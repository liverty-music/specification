## 1. Specification (proto, all additive)

- [ ] 1.1 `series.proto` / `event.proto`: gallery images, `video_url`, external links, streaming mode (`venue`/`online`/`hybrid`) + stream URL, category, keywords, notices, contact, `age_restriction`, per-event `description`, `publish_at`
- [ ] 1.2 `series.proto` `Visibility`: add `PASSWORD`; carry a password hash (backend-only)
- [ ] 1.3 `event_performers`: performer `role` + `order`
- [ ] 1.4 authoring RPC fields for the above; `buf` checks; Release → BSR gen

## 2. Backend

- [ ] 2.1 Migrations: nullable columns for all new fields; `PASSWORD` handling; performer role/order
- [ ] 2.2 Streaming mode: relax venue requirement for `online`; decide discovery treatment
- [ ] 2.3 Password read-path verify (reuse the ② unlisted/draft guard)
- [ ] 2.4 Scheduled publish job (runs the ② publish transaction at `publish_at`)
- [ ] 2.5 Validation + tests for each field/behavior; `make check`

## 3. Frontend (organizer console)

- [ ] 3.1 Rich authoring form: media/gallery uploader, video/link fields, streaming toggle, category/keywords, structured 注意事項/問い合わせ先/年齢制限, password option, per-event notes, lineup role/order editor, schedule picker
- [ ] 3.2 Password-gate viewer route; `make check`

## 4. Release & ship to prod

- [ ] 4.1 Ship per cross-repo order after ② is live; verify each extension in prod
- [ ] 4.2 (If split) track sub-features as their own changes when scheduled

Note: this is a backlog change captured to preserve deferred scope; it may
be split into smaller changes when work actually starts.
