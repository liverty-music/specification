## Context

See proposal.md for the motivation. The current state that shapes the approach:

- The venue staff guide is a precedent to follow: `frontend/reception/public/guide.html` is a static page with no script, served from the reception build's `publicDir`, opened from the console's Reception tab and the scanner screen in a new tab, and `frontend/test/reception/guide.spec.ts` fails when a scanner-screen word it quotes changes.
- The organizer console has no `publicDir` of its own. It is one entry (`organizer.html`) of the main `vite.config.ts` build, whose `public/` is shared with the fan app. `Dockerfile.organizer` assembles the organizer serving root by copying an explicit list of files out of `dist/`.
- `Caddyfile.organizer` serves `/srv` with `try_files {path} /organizer.html`: a file that exists is served as is, before the SPA fallback. It sets no Content-Security-Policy.
- The top bar is `organizer/shell/top-app-bar`. Under 600 px on a deep page it shows the back arrow, the page title, the Organizer and Artist block (up to 45 % of the width) and the account icon.
- Prerequisite notices are the `prerequisite-callout` component, with one optional action (`action-href` or `action-label`).
- Icons are inline SVG paths registered in `organizer/ui/console-icon/console-icon.ts`.

## Goals / Non-Goals

**Goals:**

- One guide page that stays in step with the console: a unit test fails when a console word the guide quotes changes, or when the screen-to-chapter mapping names an anchor the guide does not have.
- The member story map and the information architecture kept as a developer document that outlives the change, and used as the source of the guide's chapters and screen map.

**Non-Goals:**

- An English guide. The guide is Japanese only for the trial (see Decisions).
- Fixing the UX gaps the story map shows (see proposal.md - What Changes).
- Screenshots. The guide draws the parts of screens it needs with HTML and CSS, as the reception guide does, so a restyle of the console does not leave stale images behind.

## Decisions

### D1. A static HTML page in the frontend repository

The guide is a hand-written static HTML page with no script, like the reception guide.

Alternatives:

- **A Claude Docs page or an Artifact.** It is quick to write and has no deploy. But it lives outside the console's origin, cannot be checked against the console's words by a test, and goes stale without anyone noticing. Rejected.
- **An Aurelia route of the console.** It would get the console's i18n and design tokens for free, but it would need sign-in (the console guard), load the app bundle, and could not be read by someone who cannot sign in, which is exactly when sign-in help is needed. Rejected.

### D2. Source path and serving

The source is `frontend/organizer/guide/guide.html`, and it is served at `/guide.html` on the organizer origin. `Dockerfile.organizer` copies it into `/organizer-srv/guide.html` next to `organizer.html`. Caddy serves it before the SPA fallback, so Caddy needs no change. No console route uses `/guide.html`.

Alternatives:

- **Put it in the shared `public/`.** It would also be emitted into the fan image, which serves `dist/`. A members' page on the fan origin is confusing. Rejected.
- **A separate organizer `publicDir`.** It is a build change for one file. Rejected.

In `npm run dev` the page is reachable at `/organizer/guide/guide.html`. The help link uses `/guide.html` and is only exercised against the production-like build in E2E.

The page links Google Fonts and the favicon the same way the reception guide does, and copies the palette from the organizer's `styles/tokens.css`. The copy is mirrored by hand, as in the reception guide, because a static page cannot import the console's CSS.

### D3. Chapter anchors and the screen-to-chapter mapping

Each chapter has a fixed id. The console links to `/guide.html#<id>`.

| chapter | id |
|---|---|
| ホームの見かた | `home` |
| サインインする | `sign-in` |
| 事業者情報と受取口座 | `business-and-payout` |
| 公演をつくって公開する | `publish` |
| 公開した公演を変える | `change-published` |
| チケットを販売する | `sell` |
| 売れ行きと紹介コード | `sales-and-referral` |
| 受付リンクを発行する | `reception` |

One frontend module holds the guide URL builder and the mapping from route component to chapter id. The table is in the organizer-shell spec. The top bar reads the active route from the router to choose the anchor. The prerequisite callouts use the same builder with a fixed id. The unit test reads the guide HTML and checks that every id in the mapping exists as an `id` attribute in the guide.

### D4. The help action is a link, not a button

The help action is `<a href="/guide.html#…" target="_blank" rel="noopener">` with a `help` icon (Material Symbols "help", outlined), a visually hidden label from `shell.help` (使い方 / Help), and a `title` with the same text for the pointer tooltip. It is a link because it navigates. It opens a new tab because the concert and sale editors guard unsaved changes on navigation, and the reception guide link already sets this pattern.

It sits immediately before the account icon. On a narrow deep page, the Organizer and Artist block shrinks, then the title; the back arrow, help and account keep their 48 px targets. This is verified at 390 px by E2E.

Alternative: **a 使い方 item in the account menu.** The menu hides it until opened, and it cannot hint that it is about the current screen. Rejected after discussion with the product owner.

### D5. Prerequisite callouts gain a second link

`prerequisite-callout` gets an optional `guide-chapter` bindable. When it is set, the callout renders a secondary link, 詳しく見る (Learn more), that opens the guide at that chapter in a new tab. The link sits below the existing action and is styled as a plain text link, so the fix stays the primary action. The business-details notice, which has no fix link, gets only this link.

### D6. Japanese only

The guide is Japanese, the console's default and the language of every trial partner, matching the reception guide. The organizer i18n spec requires every label the console shows in both languages. The guide is a separate page, not a console screen. Its language is stated in its own spec, and the help action's label itself is translated. An English guide is a follow-up if a non-Japanese partner joins.

### D7. Guide content follows the story map

The developer document `specification/docs/organizer-console-story-map.md` (English prose, console words quoted in Japanese) holds the following:

- **Story map.** A Mermaid `journey` backbone (one section per activity, one task per story) and one `journey` per story. Actors are Member, Liverty Music, Stripe, Venue staff and Fan. Scores are an estimate, from the specs, of how easily a member gets through a step without a manual. They are marked as an estimate, not a measurement.
- **Information architecture.** A Mermaid `flowchart` with one subgraph per destination. Solid edges are parent and child, dashed edges are cross-links (Home items, prerequisite links, external pages). A screen inventory table lists each screen's information and actions, and its guide chapter.
- **Gaps.** The steps with low scores, with evidence and a proposed fix. They feed the follow-up change.

`flowchart` is chosen over `mindmap` and `treeView-beta` because the console's structure has cross-links (Home to the Reception tab, Settings and the editor) that a strict tree cannot draw. `treeView-beta` also needs Mermaid 11.14 or later, and GitHub rendering of it is unconfirmed. A `classDiagram` per screen was rejected: a table carries the same inventory with fewer concepts.

The guide's chapters are the story map's stories, grouped as listed in the guide spec. Its screen map is the flowchart drawn with HTML and CSS: no Mermaid, because the page has no script. The guide's header comment points to the developer document as its source, as the reception guide's comment does.

### D8. Keeping the guide in step

`frontend/test/organizer/guide.spec.ts` asserts the following:

- The guide has a doctype and `lang="ja"`, and has no `<script>`.
- Every chapter id from the mapping is in the guide.
- A list of quoted console words is present both in `organizer/locales/ja/translation.json` and in the guide. The list covers buttons, tabs, sale states, Home kinds, prerequisite headings and scanner states.

A word change in the console then fails the test until the guide is updated.

## Risks / Trade-offs

- [The guide drifts on things the word list does not cover, such as an order of steps or a default value] → The developer document and the guide are listed in the frontend AGENTS.md checklist for organizer UI changes. Reviewers check the chapter of the screen they change.
- [A fourth icon crowds the 390 px top bar] → The E2E check at 390 px asserts that the back arrow, title, help and account do not overlap. The Organizer and Artist block truncates first.
- [Members using the console in English get a Japanese guide] → Accepted for the trial (D6). The help label is still English, so the action is discoverable.
- [The guide states facts owned by other specs: the referral window of 7 days, `?org=`, the automatic draw] → These are quoted in the developer document with their source spec. A change to those specs lists the guide in its impact.

## Migration Plan

This is frontend only: one PR in frontend and one PR in specification for the developer document. Deploying the organizer image ships the page and the help action together. Rollback is reverting the frontend PR. There is no data and no API change.
