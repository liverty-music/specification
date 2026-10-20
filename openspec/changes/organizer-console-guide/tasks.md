## 1. Developer document (specification)

- [ ] 1.1 Write `docs/organizer-console-story-map.md` in English, quoting console words in Japanese (design D7). It holds the backbone `journey`, one `journey` per member story, the IA `flowchart` (subgraph per destination, dashed cross-links), the screen inventory table (information, actions, guide chapter id per screen), and the gaps list with evidence and proposed fixes. Mark scores as an estimate. Verify that every Mermaid block renders with `npx -y @mermaid-js/mermaid-cli` and that `python3 scripts/check-forbidden-words.py` passes.

## 2. Guide page (components/infrastructure/organizer/web/route/guide)

- [ ] 2.1 Write `frontend/organizer/guide/guide.html`: static, no script, `lang="ja"`, `noindex`. It has the chapter list, the screen map drawn in HTML/CSS, and the eight chapters with the ids of design D3. The content follows the story map, including the "What the screens do not say" items. Add a header comment that points to the developer document. Verify by opening it at 390 px and 1280 px.
- [ ] 2.2 Add `frontend/test/organizer/guide.spec.ts` (design D8) with `@spec` annotations. It covers "Opened signed out" (static page, no script, no sign-in code), "Contents", "Link to a chapter" (chapter list order and ids), "Where a Home item leads", "Publishing step", "Selling step" (quoted words present in both `locales/ja/translation.json` and the guide), "Referral link" and "Sale blocked by business details". Verify that `npm test` passes.
- [ ] 2.3 Add a functional E2E for "Opened on a phone": at 390 px, `scrollWidth <= clientWidth` for the guide page. Verify that it passes locally.
- [ ] 2.4 Copy the guide into the organizer serving root in `Dockerfile.organizer` as `guide.html`. Verify that a local `docker build -f Dockerfile.organizer` image answers `GET /guide.html` with 200 and the guide, and still answers `GET /organizers/x` with `organizer.html`.
- [ ] 2.5 Add a rule to `frontend/AGENTS.md`: a change to the organizer console's words or flow updates the matching chapter of the guide and the developer document. Verify that the rule is in the file.

## 3. Help action (components/infrastructure/organizer/web/global/organizer-shell)

- [ ] 3.1 Add the outlined `help` icon to `console-icon` with a Storybook story. Verify that the story renders.
- [ ] 3.2 Add the guide link module: the `/guide.html#<id>` builder and the route-to-chapter mapping of the spec table. Verify with a unit test that every screen of the table maps to its chapter and that every mapped id exists in the guide HTML.
- [ ] 3.3 Add the help link to the top bar, before the account icon: `target="_blank"`, `rel="noopener"`, the visually hidden label and `title` from `shell.help` (使い方 / Help) in both locales. Verify with component tests annotated with `@spec` for "Help on the Sales tab" and "Console in English", and that the existing shell tests still pass.
- [ ] 3.4 Add functional E2E tests annotated with `@spec`. "Help while editing": a new page opens at `#publish`, no unsaved-changes dialog appears, and the typed title is kept. "Help on a phone": at 390 px on an event page, the bounding boxes of the back arrow, title, help and account do not overlap. Verify that they pass, and re-run the existing organizer-shell E2E tests for "Persistent navigation around every screen".

## 4. Guide links in prerequisite notices (components/infrastructure/organizer/web/route/event, components/infrastructure/organizer/web/route/ticket-sale-editor)

- [ ] 4.1 Add the optional `guide-chapter` bindable to `prerequisite-callout`, rendering 詳しく見る / Learn more as a secondary link that opens in a new tab (design D5), with a Storybook story for a callout that has a fix and a guide link and one that has only a guide link. Verify that the stories render.
- [ ] 4.2 Wire the Sales tab notices (`publish` for draft and no start time, `business-and-payout` for business details) and the Reception tab notices (`publish`). Verify with tests annotated with `@spec`: route/event "Draft event", "No start time", "Business details incomplete", "Unpublished event" and "Event without a start time".
- [ ] 4.3 Wire the lottery and first-come sale editor notices the same way. Verify with tests annotated with `@spec`: route/ticket-sale-editor "No start time" and "Business details incomplete".

## 5. Integration in prod

- [ ] 5.1 After the organizer image is deployed, check read-only in prod. `curl -s -o /dev/null -w '%{http_code}' https://organizer.liverty-music.app/guide.html` returns 200 without a sign-in redirect. In the signed-in console, 使い方 on a Sales tab opens the guide at チケットを販売する. Record both results in this task, and mark "Opened signed out" with `@spec-manual` citing this check if no automated test covers the served page.
