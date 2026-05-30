## Why

The current onboarding and dashboard copy uses colloquial/subcultural Japanese ("推し") that narrows the perceived audience to fan-culture insiders, contains semantically inaccurate phrases ("近日開催予定" when concerts are not actually imminent, "あなたの地元" when the area is user-selected rather than user-resident), and surfaces hardcoded English strings inside the concert detail sheet to Japanese users. The coach mark on the Discovery page also auto-dismisses after 2 seconds — too fast for users to read the guidance and act — and the prefecture-selection step of the home-area selector exposes a circular back affordance with no visible label, leading users to perceive it as a decorative dot rather than a navigation control.

These rough edges accumulated as the product evolved from a fan-culture demo toward a general-audience music-event PWA. Polishing them now — before broader user testing — keeps the perceived audience wide, reduces support questions, and prevents users from feeling lost during the only structured tutorial moment in the product.

## What Changes

- Replace "推し" across all onboarding-adjacent copy with the entity-grounded pair "アーティスト" (noun) + "フォローする" (verb). Affects Welcome CTAs, signup prompts, preview labels, popover guide, and dashboard onboarding subtitle.
- Replace the Discovery snack notification copy "{{name}}のライブが近日開催予定です！" with "{{name}}の開催予定のライブが見つかりました！" so the wording accurately reflects "concerts were discovered" rather than implying imminent dates.
- Change the Discovery-page "View timetable" coach mark dismissal model from auto-dismiss-after-2-seconds to tap-to-dismiss (no timer). The user must explicitly tap the highlighted Home/Dashboard icon to advance.
- Replace the home-area selector description "HOME STAGEにはあなたの地元のライブが並びます。居住エリアはどこですか？" with the clearer "HOME STAGEには選択したエリアのライブが並びます。あなたの居住エリアはどこですか？" — separating the explanation of what HOME STAGE shows from the question being asked.
- Add a visible text label ("地方一覧" / "Regions") to the prefecture-step back button in the home selector so it is recognizable as a "go back" affordance rather than an unlabeled circular icon.
- Translate the concert detail sheet (currently English-only hardcoded strings: "Open / Start", "Open in Google Maps", "Ticket Status", "Stop tracking", "View Official Info", "Add to Calendar", plus journey-status enum values) into a JA/EN i18n namespace `eventDetail.*` so Japanese users see Japanese copy throughout.

## Capabilities

### New Capabilities
<!-- No new capabilities. -->

### Modified Capabilities
- `brand-vocabulary`: Add a Layer B vocabulary policy retiring "推し" in favor of "アーティスト" + "フォローする" for user-facing copy; register the canonical surface forms.
- `onboarding-tutorial`: Change the Step 1 coach mark (Dashboard icon on Discovery completion) dismissal behavior from a 2-second timer to tap-only.
- `user-home`: Update the home-selector explanatory copy and require the prefecture-step back control to display a visible text label in addition to its icon and `aria-label`.
- `concert-detail`: Require all user-facing strings in the concert detail sheet (date/time labels, action buttons, ticket-status section, journey-status enum surface forms) to be localized via i18n keys with JA and EN translations rather than embedded English literals.

## Impact

- **Frontend code**:
  - `frontend/src/locales/ja/translation.json` and `.../en/translation.json` — add/modify keys under `welcome.cta`, `welcome.preview`, `signup`, `discovery`, `userHome`, and add a new `eventDetail.*` namespace.
  - `frontend/src/routes/discovery/discovery-route.ts` — remove `COACH_MARK_FADE_MS` constant, `coachMarkFadeTimer` field, the `setTimeout` that schedules auto-deactivation, and the cleanup branch in `detaching()`.
  - `frontend/src/components/user-home-selector/user-home-selector.html` + `.css` — restructure the prefecture-step header so the back control shows label text alongside the chevron icon.
  - `frontend/src/components/live-highway/event-detail-sheet.html` — replace inline literal English text with `t.bind` / `${... | t}` bindings keyed under `eventDetail.*`; localize `journeyStatuses` surface forms.
- **No backend / proto / infra changes.**
- **No breaking changes**: All updates are user-visible copy and one timer-removal behavior change that only affects the brief Discovery → Dashboard onboarding transition. Existing localStorage state, persisted user data, RPC contracts, and routing are untouched.
- **Tests**: Vitest unit tests asserting specific copy strings (if any) and Playwright E2E flows that interact with the coach mark or home selector by selector may need updates.
