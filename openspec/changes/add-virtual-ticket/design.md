## Context

The tickets screen (`frontend/src/routes/tickets/tickets-route.*`) lists tickets grouped by event. The entry QR code is shown in a bottom sheet (`openCode` / `closeCode`). While the code is shown, `refreshStates` re-reads the tickets every 5 s (`ADMISSION_POLL_MS`), and admitted tickets leave the code. The last loaded list is kept in IndexedDB (`IWalletStorage`) for use without a connection.

A spike on 2026-11-09 (`~/.cache/rich-ticket-spike/` on the owner's machine; Edge 157 on Windows over CDP, and Playwright WebKit 27.2 in the `mcr.microsoft.com/playwright:v1.64.1-noble` container) measured the approach below:

- HTML-in-Canvas (WICG explainer: https://github.com/WICG/html-in-canvas) was on by default in Edge 157 in the spike, with no flag: `<canvas content="drawable">`, `drawable` children, the `paint` event, `requestPaint`, `updateElementGeometry`, `texElementSubImage2D`. WebKit 27.2 in the spike had none of them. The browser vendors' positions are open: https://github.com/WebKit/standards-positions/issues/630 and https://github.com/mozilla/standards-positions/issues/1076.
- `pixi.js` 8.22.0 (npm `latest` on 2026-11-10) fails on Chrome 157: https://github.com/pixijs/pixijs/issues/12340. The fix, https://github.com/pixijs/pixijs/pull/12341, is only in the `dev` tag. With the dev build, the spike rendered the face with WebGL; hit testing and text selection followed the drawn position after `updateElementGeometry`; a ShockwaveFilter distorted the text; a multiply-blended stamp worked; and an export worked. The texture is blank until the first paint.
- An export taken right after masking the DOM returned the unmasked face, because the repaint had not happened yet.
- WebKit 27.2: the face as plain DOM with a CSS stamp works. An SVG `foreignObject` image of a cloned face exports without tainting the canvas, but images nested in it miss the first draw, and a second draw about 50 ms later includes them.
- Cover images are served from `https://cdn.liverty-music.app`, which is not the fan web's origin. The served bucket has no CORS rule (checked with gcloud on 2026-11-09), and its CDN responses carry no CORS header.
  - Chromium's HTML-in-Canvas silently leaves out a cross-origin image without a CORS response.
  - `crossorigin="anonymous"` without a CORS response stops the image from loading at all.
  - The image is drawn only when the server sends a CORS response and the image has `crossorigin`.
- The unoptimised lazy bundle of `pixi.js` plus `pixi-filters` was about 340 KB gzip.

Every value the face shows is already loaded by the screen; only the prefecture is not displayed in the list today. These are the RPCs each value is read from:

| face item | screen value | RPC response field |
|---|---|---|
| cover image | `WalletEventGroup.event.coverUrl` | `ConcertService.Get` → `series.cover_image.large` |
| performers | `event.performers[].name` | `ConcertService.Get` → `artists[].name` |
| title | `event.title` | `ConcertService.Get` → `series.title` |
| date, open, start | `event.date`, `openTime`, `startTime` | `ConcertService.Get` → `event.local_date`, `open_time`, `start_time` |
| venue, prefecture | `event.venueName`, `adminArea` (shown as a localized name with the Event page's prefecture helper, never the raw ISO 3166-2 code) | `ConcertService.Get` → `event.listed_venue_name` or `venue.name`, `venue.admin_area` |
| seat type | `WalletTicket.seatTypeName` | `TicketSaleService.ListByEvent` → stock's seat type name |
| state | `WalletTicket.state` (the stamp shows the event's date, not the admit time) | `TicketService.List` → `status` |
| full name, phone | `WalletPersonalDetails` | the fan's User, as the list already reads it |
| transfer prohibition | shown on every ticket's back: the Ticket entity's flag is always true, so it is not read | — |

The colour of the face's lower part comes from `artistHue(name)` (`src/adapter/view/artist-color.ts`) of the first performer, as the event cards already do.

## Goals / Non-Goals

**Goals:**

- The ticket is a keepsake, not a list of facts: a printed object with art, foil and its own typography, in a design the fan picks. The owner set this goal on 2026-11-10 after seeing the first release, which listed the items as text.
- One component, `virtual-ticket`, renders the same DOM in every browser, so every item stays selectable text that a screen reader reads. WebGL draws under or through that DOM; it never replaces it.
- The admission stamp is real text on the front (入場済, ringed by the event's date).

**Non-Goals:**

- The dashboard event card (owner's decision: later).
- Changing the QR code, its signing, the 15 s rotation or the 5 s polling.
- Changing the tickets list, which keeps the 特定興行入場券 face of every ticket.
- Asking for the device's orientation where that opens a permission dialog (Safari on iOS: https://www.w3.org/TR/orientation-event/#dom-deviceorientationevent-requestpermission). The ticket sways by itself there.

## Decisions

### Two sides (owner's decision, 2026-11-10)

The ticket has a front and a back and turns over at a tap or with the button below it.

- **Front:** the cover as art, the headline, the facts as ruled cells and a stub below a tear line. No personal details, no QR code, no ticket id. Because nothing on it is personal, the share image is the front as it is.
- **Back:** the 特定興行入場券 face. It carries what チケット不正転売禁止法 第2条第3項 asks a covered ticket to display: that paid transfer without the organizer's consent is prohibited (第1号, shown as 無断有償譲渡禁止) and that the eligible person's name and contact details were confirmed at the sale (第3号, shown as 入場資格者の氏名・連絡先確認済み). The name itself need not be displayed by the law; the back shows it with the phone number so the fan can check what was registered. Source: 文化庁's pages on チケット不正転売禁止法 and their Q&A for organizers (https://www.bunka.go.jp/seisaku/bunka_gyosei/ticket_resale_ban/index.html).

The side that is turned away is `inert`, so neither a pointer nor a screen reader reaches it.

Alternative: one face with the personal details masked for sharing (the first release). The masked bars looked like damage in the shared image, and the statements crowded the art. Rejected by the owner.

### Two ways to draw one DOM

`virtual-ticket` lays the ticket out at one design size (20rem by 34rem) and scales it to its stage, so type and spacing keep their proportions on every screen. The stage takes the sheet's width up to 26rem, bounded by 52% of the viewport's height (owner's request, 2026-11-11: a larger ticket with less room around it), and WebGL draws at the scaled resolution, at most 3 device pixels per CSS pixel. It is drawn in one of two ways, chosen by feature detection (`'requestPaint' in HTMLCanvasElement.prototype && 'texElementSubImage2D' in WebGL2RenderingContext.prototype`):

- **Sheet (Chrome and Edge 157 and later):** the card is moved into a `<canvas>`, and both sides become `HTMLSource` textures on one mesh (`ticket-sheet-renderer.ts`). The mesh's vertices are moved every frame: it turns about its vertical axis, its top runs ahead of its foot and it bows across its width, so the ticket bends like paper. The foil and the stamp's shockwave run through the text. `updateElementGeometry` tells the browser where the facing side was drawn, so taps and text selection hit it.
- **DOM (Safari, Firefox, and a fan who asked to reduce motion):** both sides stay in the page; a canvas under the front's text draws the art, the foil and the paper (`ticket-renderer.ts`), and the card turns with a CSS 3D transform. With reduced motion this renderer draws one still frame per change.

When the sheet cannot start, or WebGL is unavailable, the component falls back one step: sheet to DOM, DOM to the plain cover image under the text.

Alternative: draw the text with PixiJS. It would no longer be selectable or read aloud, and every item would be laid out twice. Rejected.

### The ticket follows the device's tilt

The component listens for `deviceorientation` wherever the event exists, unless the fan asked to reduce motion; level across and held at about 45 degrees is the ticket at rest. Listening asks for nothing. Chrome has `DeviceOrientationEvent.requestPermission()` since 121 (Intent to Ship: https://groups.google.com/a/chromium.org/g/blink-dev/c/ckd2rFmT3PA) and grants the sensors by default; whether it holds the events back until the method is called could not be settled from the sources. So on the first touch of the ticket, the component calls it only when `navigator.permissions.query({ name: 'accelerometer' })` already answers `granted`, which cannot open a dialog and which Safari does not answer at all.

### PixiJS is pinned to a dev build (owner's decision, 2026-11-10; replaces "wait for 8.23")

`pixi.js` is pinned to `8.22.0-dev.f7d8c62`, the `dev` build that contains pixijs#12341; 8.22.0 on `latest` fails in Chrome 157 only in `HTMLSource`. The owner chose to ship the sheet now rather than wait. The pin needs an npm `overrides` entry: `pixi-filters` peers `pixi.js >=8.0.0-0`, a semver range does not match a prerelease of another version, and `npm ci` fails with `ERESOLVE` without it (seen in the frontend PR's first CI run, 2026-11-11). The override hands `pixi-filters` the root's `pixi.js`; the frontend's AGENTS.md records it with its exit condition. Exit condition: when a `pixi.js` release containing pixijs#12341 is on npm `latest` (expected 8.23.0), move to it and delete the pin and the override.

### Design presets, kept on the device (owner's decision, 2026-11-10)

Six presets (`default`, `rock`, `pop`, `jazz`, `classic`, `electronic`) share one layout. A preset sets the paper, two inks, one accent and the faces of the headline and the values in CSS (`ticket-presets.css`), and the art's duotone grading and foil in the renderers (`ticket-presets.ts`). The layout follows a professional ticket reference the owner supplied: the photo leads, two inks and one accent, small labels over large values in ruled cells, a stub with bars in a white box.

The fan's choice is kept per ticket in `localStorage` (`tickets.presets`, a JSON map of ticket id to preset name) behind `src/adapter/storage/ticket-preset-storage.ts`, and removed on sign-out. It is not sent to the server, so another device shows the default (owner's decision).

Alternative: a store in the wallet's IndexedDB database, as for the stamps. It needs `DB_VERSION` 3, and a build can never be rolled back past a database version; a small preference is not worth that. Rejected.

The presets' display faces (Anton, Fredoka, Abril Fatface, Playfair Display, Orbitron, Space Mono; `@fontsource`, self-hosted) are imported when a virtual ticket is first shown and are not precached: without them the ticket is set in the app's own faces. They are Latin faces; Japanese text falls back to the app's faces.

The ticket is a printed object, so its stylesheets set literal colours, sizes and type. `stylelint.config.js` allows that for `src/routes/tickets/virtual-ticket/*.css` only; margins, focus outlines, `z-index` and the block length stay bound.

### The stamp starts in `refreshStates`

`refreshStates` already notices when tickets leave the code.

- When the presented tickets become empty because every one of them was admitted, the route calls `closeCode()` and then `openTicket(group, firstAdmitted, { stamp: true })`. "First" is the first of those tickets in list order.
- When some presented tickets remain, the code stays open, as it does today.

The other admitted tickets play their stamp the first time they are opened.

The "played once" record is a new IndexedDB object store, `stamped-tickets`, in the wallet database. `DB_VERSION` goes from 1 to 2, and `onupgradeneeded` creates only the missing store. `IWalletStorage` gains `getStampedIds(): Promise<ReadonlySet<string>>` and `addStampedIds(ids)`. `clear()` on sign-out empties it with the other stores.

Alternative: `localStorage`. The frontend review rule keeps storage behind `src/adapter/storage/`. The wallet database is already the per-device store that is cleared on sign-out. Rejected.

The animation plays when the ticket is `entered`, its id is not in the set, and `prefers-reduced-motion` is not `reduce`. The id is added after the animation ends. A dialog closed mid-animation leaves the id unrecorded, so the stamp plays again on the next open.

### Stamp effects

The stamp is a DOM element on the front's stub, over the decorative bars, so it covers no fact; on an entered ticket the bars fade under it. It carries no admit time (owner's decision: the time is not needed on a keepsake).

1. It comes down from 1.6× with an ease-in and lands at 20% of 1.5 s; only `transform` and `opacity` move.
2. Where it lands, a ShockwaveFilter, a short colour split and about 44 sparks run for about 1.4 s, all dying away along one curve. In the sheet they run through the text; in the DOM way, through the art.

With reduced motion, the stamp is shown at rest and nothing is drawn.

### Share image

The share image is the front, which holds no personal details, so nothing is masked. It is made the same way in both ways of drawing:

1. Draw the front's art and paper with a second, off-screen `ticket-renderer` in the ticket's preset, without tilt animation, and copy its canvas. Without WebGL, the image gets the paper and the plain cover instead.
2. Clone the front, without its cover, its canvas and its stamp. Mount the clone off screen inside a copy of the card, so the scoped stylesheets and the preset apply, and inline every computed style. Every style is read before any is written.
3. Embed the faces the clone is set in: every `@font-face` the page has loaded for those families, with its file as a data URL. An SVG used as an image loads no external resources, the page's fonts among them (SVG Integration, secure static mode: https://www.w3.org/TR/svg-integration/#secure-static-mode), and the presets depend on their faces.
4. Serialise the clone into an SVG `foreignObject` image, scaled with a CSS `transform` inside it. Observed on 2026-11-10 in Playwright WebKit (iPhone 14): it drew the `foreignObject` content at 1x in the corner of a `viewBox`-scaled SVG, while Chromium scaled it.
5. On the export canvas: the art, the SVG image over it, then cut the outline (round corners, the two notches of the tear), and `toBlob`.

The image is made at the layout size, not the size on screen: the ticket is tilted and scaled on screen.

- **Hand-off:** wrap the blob in `File([blob], 'liverty-ticket.png', { type: 'image/png' })`. Use `navigator.share({ files })` when `navigator.canShare({ files })` is true; otherwise download through an object URL.

Alternative for the sheet: extract the WebGL frame of the live sheet. The stamp would have to be hidden and a repaint awaited while the visible canvas is frozen, and Safari would still need the SVG way. One way for every browser is simpler. Rejected.

Verification (2026-11-11): CI ran `e2e/functional/virtual-ticket.spec.ts` in Chromium (`functional`) and WebKit (`webkit-virtual-ticket`), and both passed on frontend#992. Locally it passed in Chromium on the dev server: the shared file is a PNG of the front's shape with the test cover's hue in its art and no stamp ink. Share images of the default and rock presets, made from Storybook in headless Chromium, showed the art, the preset's embedded face and the notches. WebKit (`webkit-virtual-ticket`) runs in CI; it could not run on the owner's machine (missing system libraries).

### CORS header from the CDN backend bucket

The served bucket sits behind Cloud CDN as a private origin. The backend bucket uses `cacheMode: FORCE_CACHE_ALL` with a one-year TTL, and its cache key does not include `Origin` (`cloud-provisioning/src/gcp/components/object-storage.ts`, `object-storage-backend-bucket`). A CORS rule on the GCS bucket would therefore not be enough. GCS adds `Access-Control-Allow-Origin` only to a request that carries `Origin`. The edge caches whichever response it fetched first and serves it for a year. Any plain `<img>` request (the list, the organizer console, the dashboard) could fill the cache with a response without the header, and then every `crossorigin` request for that object would fail.

The header is therefore set on the backend bucket's responses, which the load balancer adds whether the object came from the cache or not:

```ts
customResponseHeaders: ['Access-Control-Allow-Origin: *']
```

`*` rather than the fan web origin:

- The objects are public images served without cookies, so a wildcard exposes nothing that `<img>` does not already expose.
- A single fixed value would have to choose between prod, dev (`dev.liverty-music.app`) and a local dev server. `*` works for all three.
- `crossorigin="anonymous"` sends no credentials, so a wildcard is accepted.

The class docstring's CORS section, which says the served bucket has no CORS, is updated in the same change. Source: Cloud CDN custom response headers (https://cloud.google.com/cdn/docs/using-custom-headers) and the Fetch standard's CORS check (https://fetch.spec.whatwg.org/#cors-check).

After the production `pulumi up`, the check is `curl -sI <an existing cover URL>`, looking for `access-control-allow-origin: *`. An existing cover is used because it is the case that a cached response could break. The cover `<img>` in the face gets `crossorigin="anonymous"` only after that check passes. In the reverse order, every fan's cover images would fail to load (measured in the spike).

Result (2026-11-10): the production `pulumi up` (prod stack version 293, cloud-provisioning PR #748) succeeded at 01:44 UTC, and `gcloud compute backend-buckets describe liverty-music-prod` lists `customResponseHeaders: ['Access-Control-Allow-Origin: *']`. The header reached the edge about 4 minutes after the update. From 01:48 UTC, `curl -sI` on an existing cover (`https://cdn.liverty-music.app/cdn/<organizer>/<id>/large.webp`, cached before the change) returns `HTTP/2 200` with `access-control-allow-origin: *`, both without `Origin` and with `Origin: http://localhost:9000`. Task 3.6 may proceed.

### Loading and precache (owner's decision: precache)

The component imports its renderers dynamically, the way `dna-orb` loads Matter.js; they import `pixi.js`, `pixi.js/html-source`, `pixi-filters/shockwave` and `pixi-filters/rgb-split`. The service worker's precache (vite-plugin-pwa `injectManifest`) includes both chunks, so the virtual ticket opens with its effects in a venue without signal.

Measured on a production build (2026-11-11): `ticket-renderer` 304.8 KB (92.4 KB gzip), which holds PixiJS, and `ticket-sheet-renderer` 18.0 KB (6.3 KB gzip).

## Found in production (2026-11-11)

The owner opened the released ticket (v1.159.0) on a Pixel: no effects, and no tilt with the device. Both were dead in the app and only there.

- **Content-Security-Policy.** The fan app's `index.html` sets `script-src` without `'unsafe-eval'`. PixiJS 8 builds its uniform and shader sync code with `new Function`, so every renderer threw at start, and the component fell back to the plain cover without logging. PixiJS ships `pixi.js/unsafe-eval` for this (https://pixijs.com/8.x/guides/migrations/v8): both renderers import it first, and a renderer that cannot start is now logged. The effects had been seen in Storybook, which has no policy; the e2e passed because the fallback satisfied its checks.
- **Tilt.** The presence of `DeviceOrientationEvent.requestPermission` was read as "iOS, do not ask", but Chrome has had it since 121, so the listener was never added on the Pixel. See "The ticket follows the device's tilt".
- **`font-src`.** It gains `data:`: Vite inlines small font files of the presets' faces as data URLs, and the share image embeds faces the same way.
- **The sheet, in the app.** Driving the production build in Edge 157 over CDP (the first time the sheet ran outside Storybook) showed three more:
  - The canvas's bend margin lay over the button below the ticket and took its taps. The controls are now positioned above the stage.
  - A side without a paint record, a frame or two after the card moves into the canvas, makes the upload throw `No cached paint record for element` inside PixiJS's own `paint` listener, as an unhandled error. The sources are created with `autoUpdate: false`, and the renderer follows `paint` itself and draws its own frames, with that failure handled.
  - A descendant of a canvas reports no size (`offsetWidth` 0, a computed width of `auto`). The share image and its art take the ticket's size from the box the card is laid out in, outside the canvas.

Verification after the fixes, on a production build (`vite preview`):

- `e2e/functional/virtual-ticket-webgl.spec.ts` (Chromium with software WebGL): the front is drawn under the policy (`data-drawn="true"`), the card tilts when `deviceorientation` events arrive, and the shared image carries the cover's hue in its art. The long flow in `virtual-ticket.spec.ts` now runs with WebGL turned off, so it tests the fallback on purpose.
- Edge 157 over CDP with the same mocked backend: the ticket is drawn as a sheet; closed and reopened it has one canvas and is drawn; the button below it receives its tap; the back, a preset change and the share image work; no page error is logged.
- Not verified: a real phone. The Pixel check is task 4.9.

## Risks / Trade-offs

- [The speed of the WebGL art on an iPhone is unmeasured; the owner has no iPhone] → The resolution is capped at 2 device pixels per CSS pixel, and WebKit runs the flow in CI. A slow phone still shows every item, because the text is DOM.
- [A `dev` build of PixiJS in production] → The version is pinned exactly, the sheet is behind feature detection with the DOM way as fallback, and the exit condition is written above.
- [HTML-in-Canvas changes shape again in Chrome] → Feature detection falls back to the DOM way, which is the Safari way and is tested on every PR.
- [WebKit draws the SVG `foreignObject` image before its embedded fonts are ready] → Unverified locally. The image then shows the fallback face; CI's WebKit run checks the image's content, not its typeface.
- [The CORS rollout order is reversed and cover images break for everyone] → Done in the right order (see the result above).
- [A larger precache for every fan: about 99 KB gzip] → Owner accepted precaching; the measured size is a third of the spike's estimate.
- [The preset faces are Latin only] → Japanese names are set in the app's faces. Open: whether to add Japanese display faces.

## Migration Plan

1. cloud-provisioning: the CORS response header on the CDN backend bucket. Merge, then the owner runs the production `pulumi up`. Merging also auto-runs the dev `pulumi up`; dev is stopped, so that run is not verified.
2. Check the header on an existing production cover URL with `curl`.
3. frontend, first release (v1.155.0): the virtual ticket as one DOM face, the stamp and the masked share image, with `crossorigin` on the cover.
4. frontend, the collectible: two sides, presets, the WebGL art and the sheet, and the share image of the front. Release.

Rollback: remove `crossorigin` (frontend) before removing the header. A build with `DB_VERSION` 1 cannot open a database already upgraded to version 2 (`VersionError`), and the fan would lose the offline ticket list. So the frontend is never rolled back to an older build. Instead, a fix-forward build turns the virtual ticket off and keeps `DB_VERSION` 2 and the new store.
