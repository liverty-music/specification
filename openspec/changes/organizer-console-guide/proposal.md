## Why

The trial of ticket sales puts the organizer console in the hands of partner Artists' members, and there is no guide for it: a member who gets stuck (a sale that cannot start, a draw that has not happened yet, a referral link) has nobody to ask but the owner of Liverty Music. The console should be usable without a manual, but until every gap is fixed in the screens, a member needs a guide that the console itself opens at the step they are on. The venue staff already have such a page (the reception guide); members do not.

## What Changes

- Add a static guide for members, served by the organizer console without sign-in, in Japanese. It is organised by what a member wants to do (one chapter per member story: sign in, set up the payout account, create and publish a concert, change a published concert, sell by lottery, sell first come, check sales and referral codes, issue reception links, handle reception trouble), opens with a map of the console's screens, and names every button and notice as the console shows it.
- Add a help action (an icon next to the account menu) to the console frame. It opens the guide in a new tab at the chapter for the screen the member is on, so unsaved input in an editor is never lost.
- The notices that say why a sale or a reception link cannot start yet (event not published, no start time, business details incomplete) link to the guide's chapter that explains it, in addition to their existing link to the fix.
- Add the member story map and the console's information architecture (Mermaid user journeys and a flowchart, plus the screen inventory) as a developer document in `specification/docs/`, so that the guide's structure and future console UX work share one source that survives the change's archive.

Out of scope: fixing the gaps the story map surfaces (business details missing from Home, no UI for referral links, the short name for a new device, a first-run prompt on Home). They are recorded in the developer document and proposed as a separate change; until then the guide explains the current behaviour.

## Capabilities

### New Capabilities

- `components/infrastructure/organizer/web/route/guide`: the members' guide page — static, no sign-in, Japanese, chapters per member story, a screen map, screen words quoted as shown, one anchor per chapter.

### Modified Capabilities

- `components/infrastructure/organizer/web/global/organizer-shell`: the frame gains a help action next to the account menu that opens the guide at the current screen's chapter in a new tab.
- `components/infrastructure/organizer/web/route/event`: the Sales tab's and the Reception tab's missing-prerequisite notices link to the guide's chapter.
- `components/infrastructure/organizer/web/route/ticket-sale-editor`: the editor's missing-prerequisite notice links to the guide's chapter.

No entity, usecase or adapter changes: the guide reads no data and calls no RPC.

## Impact

- **frontend**: a new static page for the organizer image (outside the Aurelia app, no script), copied into the organizer serving root by `Dockerfile.organizer`; a help icon in `organizer/shell/top-app-bar`, a `help` icon in `console-icon`, a screen-to-chapter mapping, guide links in the prerequisite callouts; Japanese and English labels for the help action; a unit test that the guide quotes the console's Japanese labels; an E2E check of the top bar at 390 px.
- **specification**: `docs/organizer-console-story-map.md` (developer document).
- **backend, cloud-provisioning**: none. The organizer Caddy server already serves files before falling back to the SPA.
