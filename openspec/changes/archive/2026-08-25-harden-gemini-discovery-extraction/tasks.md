# Tasks

## 1. SDK & A/B harness tooling

- [x] 1.1 Bump `google.golang.org/genai` v1.57.0 → v1.69.0; `go mod tidy`; build/vet clean
- [x] 1.2 Add `gemini-3.6-flash` / `gemini-3.7-flash` pricing rows to the A/B pricing table
- [x] 1.3 Fix the Step 1 / Step 2 cost-attribution bug (cost computed against the wrong model → $0)
- [x] 1.4 Add venue-normalization aliases to the matcher (renamed venue; `某所` / TBD collapse)
- [x] 1.5 Add `gemini-3.7-flash` to the harness model list and set the evaluation axes

## 2. Ground-truth fixture

- [x] 2.1 Refresh `ab_ground_truth.json` to 101 events across 4 artists, `evaluation_from = 2026-08-23` (official-site verified; UVERworld special-page open/start times; SUPER BEAVER 高知 venue fix; +Zepp Taipei; +TBA-venue dates)
- [x] 2.2 Update the `LoadGroundTruth` fixture-well-formed assertion and the harness README (run commands / matrix axes / search pricing)

## 3. Concert Step 1 prompt — gemini-grounded-extract-and-coerce

- [x] 3.1 Mandate original-language extraction (no translation / romanization) for venue and all verbatim fields, including on multilingual pages
- [x] 3.2 Prefer the tour-specific special/feature page for `source_url` over the site top page or a generic news-list page

## 4. Sales-phase Step 1 prompt — sales-phase-discovery

- [x] 4.1 Classify a named-play-guide sale as `プレイガイド` (record the guide in `provider_name`); reserve `一般` for non-guide direct sales
- [x] 4.2 Extract `apply_end` and `lottery_result` for `抽選` phases when published (never guess)

## 5. Model evaluation & decision

- [x] 5.1 Run the 3.6-vs-3.7 A/B matrix (thinking × temperature, then `low` / `temp 0.4` across 4 artists)
- [x] 5.2 Offline re-score neutralizing venue-string artifacts; record decision — retain `gemini-3.6-flash`; measured optimum `thinking=low, temperature=0.4`

## 6. Verification & rollout

- [x] 6.1 Re-run the A/B harness with the hardened concert prompt and confirm `field_accuracy.source_url` improves
- [x] 6.2 `make check` (lint + unit tests) green
- [x] 6.3 Open the PR for the backend branch and merge after CI passes
