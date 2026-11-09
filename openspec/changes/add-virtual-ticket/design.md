## Context

The tickets screen (`frontend/src/routes/tickets/tickets-route.*`) lists tickets grouped by event. The entry QR code is shown in a bottom sheet (`openCode` / `closeCode`). While the code is shown, `refreshStates` re-reads the tickets every 5 s (`ADMISSION_POLL_MS`), and admitted tickets leave the code. The last loaded list is kept in IndexedDB (`IWalletStorage`) for use without a connection.

A spike on 2026-11-09 (`~/.cache/rich-ticket-spike/` on the owner's machine; Edge 157 on Windows over CDP, and Playwright WebKit 27.2 in the `mcr.microsoft.com/playwright:v1.64.1-noble` container) measured the approach below:

- Chrome 157 turns HTML-in-Canvas on by default (`<canvas content="drawable">`, `drawable` children, the `paint` event, `requestPaint`, `updateElementGeometry`, `texElementSubImage2D`). Safari and Firefox have no support; WebKit standards position #630 and Mozilla #1076 are open.
- `pixi.js` 8.22.0 (npm `latest` on 2026-11-10) fails on Chrome 157 (pixijs#12340). The fix (#12341) is only in the `dev` tag. With the dev build, the spike rendered the face with WebGL; hit testing and text selection followed the drawn position after `updateElementGeometry`; a ShockwaveFilter distorted the text; a multiply-blended stamp worked; and an export worked. The texture is blank until the first paint.
- An export taken right after masking the DOM returned the unmasked face, because the repaint had not happened yet.
- WebKit 27.2: the face as plain DOM with a CSS stamp works. An SVG `foreignObject` image of a cloned face exports without tainting the canvas, but images nested in it miss the first draw, and a second draw about 50 ms later includes them.
- Cover images are served from `https://cdn.liverty-music.app`, which is not the fan web's origin. The served bucket has no CORS rule (checked with gcloud on 2026-11-09).
  - Chromium's HTML-in-Canvas silently leaves out a cross-origin image without a CORS response.
  - `crossorigin="anonymous"` without a CORS response stops the image from loading at all.
  - The image is drawn only when the server sends a CORS response and the image has `crossorigin`.
- The unoptimised lazy bundle of `pixi.js` plus `pixi-filters` was about 340 KB gzip.

Every value the face shows is already on the screen. These are the RPCs it is read from:

| face item | screen value | RPC response field |
|---|---|---|
| cover image | `WalletEventGroup.event.coverUrl` | `ConcertService.Get` → `series.cover_image.large` |
| performers | `event.performers[].name` | `ConcertService.Get` → `artists[].name` |
| title | `event.title` | `ConcertService.Get` → `series.title` |
| date, open, start | `event.date`, `openTime`, `startTime` | `ConcertService.Get` → `event.local_date`, `open_time`, `start_time` |
| venue, prefecture | `event.venueName`, `adminArea` | `ConcertService.Get` → `event.listed_venue_name` or `venue.name`, `venue.admin_area` |
| seat type | `WalletTicket.seatTypeName` | `TicketSaleService.ListByEvent` → stock's seat type name |
| state, admit time | `WalletTicket.state`, `admitTime` | `TicketService.List` → `status`, `admit_time` |
| full name, phone | `WalletPersonalDetails` | the fan's User, as the list already reads it |
| resale notice | `WalletTicket.resaleWithoutConsentProhibited` | `TicketService.List` |

The colour of the face's lower part comes from `artistHue(name)` (`src/adapter/view/artist-color.ts`) of the first performer, as the event cards already do.

## Goals / Non-Goals

**Goals:**

- One face component, `virtual-ticket`, that renders the same DOM in every browser. A renderer either draws that DOM into WebGL (Chrome with HTML-in-Canvas) or leaves it as DOM (everything else).
- The admission stamp is real text inside the face (入場済 and the admit time), so it is selectable and read aloud.

**Non-Goals:**

- The dashboard event card (owner's decision: later).
- Changing the QR code, its signing, the 15 s rotation or the 5 s polling.
- WebGL effects on Safari. The owner chose the CSS stamp only. The snapshot-to-WebGL shockwave worked in the spike, but its speed on an iPhone is unmeasured.

## Decisions

### The face is DOM; the renderer is chosen by feature detection

`virtual-ticket` renders the face as an ordinary element inside a `<canvas>`. The renderer checks `'requestPaint' in canvas && 'texElementSubImage2D' in WebGL2RenderingContext.prototype`.

- **Supported:** it lazy-loads PixiJS, wraps the face in `HTMLSource`, and keeps `updateElementGeometry` in step with the sprite on every tick, so hit testing, selection and accessibility bounds follow the drawn face.
- **Not supported:** it moves the face out of the canvas, because canvas children are fallback content and stay hidden, and it hides the canvas.

Alternative: draw the face with Canvas 2D or PixiJS text. The text would no longer be selectable or read aloud, and every face item would be laid out twice, once for the canvas and once for the accessibility tree. Rejected.

### PixiJS waits for 8.23 (owner's decision)

The WebGL path starts when the first `pixi.js` release containing pixijs#12341 is published under npm `latest` (expected 8.23.0). Until then, every browser takes the DOM path, which is complete on its own: the stamp, the share image and offline use all work without PixiJS. The frontend tasks are ordered so that the DOM path ships first.

Alternative: pin `8.22.0-dev.2ab93d2`. It worked in the spike. But it needs an npm `overrides` entry for `pixi-filters`' peer range, and the frontend's rule for overrides requires a written exit condition. Rejected by the owner in favour of waiting.

### The stamp starts in `refreshStates`

`refreshStates` already notices when tickets leave the code.

- When the presented tickets become empty because every one of them was admitted, the route calls `closeCode()` and then `openTicket(group, firstAdmitted, { stamp: true })`. "First" is the first of those tickets in list order.
- When some presented tickets remain, the code stays open, as it does today.

The other admitted tickets play their stamp the first time they are opened.

The "played once" record is a new IndexedDB object store, `stamped-tickets`, in the wallet database. `DB_VERSION` goes from 1 to 2, and `onupgradeneeded` creates only the missing store. `IWalletStorage` gains `getStampedIds(): Promise<ReadonlySet<string>>` and `addStampedIds(ids)`. `clear()` on sign-out empties it with the other stores.

Alternative: `localStorage`. The frontend review rule keeps storage behind `src/adapter/storage/`. The wallet database is already the per-device store that is cleared on sign-out. Rejected.

The animation plays when the ticket is `entered`, its id is not in the set, and `prefers-reduced-motion` is not `reduce`. The id is added after the animation ends. A dialog closed mid-animation leaves the id unrecorded, so the stamp plays again on the next open.

### Stamp effects per path (Safari: owner's decision)

- **WebGL path:**
  1. The stamp element scales from 2.5× to 1× with a back-ease over 380 ms.
  2. It lands with a multiply blend.
  3. A ShockwaveFilter (from `pixi-filters/shockwave` only) and about 40 particles follow for about 1.2 s.
- **DOM path:** a CSS animation with the same scale and ease, `mix-blend-mode: multiply`, and a short shadow sink. No WebGL.

Both are about 1.5 s. With reduced motion, the stamp is shown at rest.

### Share image

The share image sets `data-share` on the face (or on a clone of it). That CSS masks the full name and phone number and hides the stamp. The image has no QR code and no ticket id, because the face never contains them.

- **WebGL path:**
  1. Set `data-share` on the live face.
  2. Wait for the next `paint` of the `HTMLSource`.
  3. Extract the face sprite's frame.
  4. Remove `data-share`.

  The wait is what keeps the export masked: the spike exported the unmasked face without it. A unit test fakes the paint event and asserts that the extract runs after it.
- **DOM path:**
  1. Clone the face and set `data-share` on the clone only, so the view never changes.
  2. Inline the cover as a data URL with `fetch`, which needs CORS.
  3. Serialise the clone and the face's CSS into an SVG `foreignObject` image.
  4. Draw it to a canvas, draw it again after 50 ms (WebKit misses nested images on the first draw), and call `toBlob`.

  iOS uses the system font. The owner accepted this, so web fonts are not inlined.
- **Hand-off:** wrap the blob in `File([blob], 'liverty-ticket.png', { type: 'image/png' })`. Use `navigator.share({ files })` when `navigator.canShare({ files })` is true; otherwise download through an object URL.

### CORS on the served bucket

Add to the served bucket in `cloud-provisioning/src/gcp/components/object-storage.ts`:

```ts
cors: [{ origins: [`https://${publicDomain}`], methods: ['GET', 'HEAD'], responseHeaders: ['Content-Type'], maxAgeSeconds: 3600 }]
```

Then update the class docstring, which says the served bucket has no CORS. GCS answers an `Origin` request with `Access-Control-Allow-Origin` and `Vary: Origin`.

Cloud CDN may still hold responses cached without the header. Objects are immutable with fresh keys per upload, so old cache entries are possible only for covers uploaded before the change. The check after the production `pulumi up` is `curl -sI -H 'Origin: https://liverty-music.app' <an existing cover URL>`, looking for `access-control-allow-origin`. If the header is missing, set a custom response header on the CDN backend bucket. That change also lives in the same Pulumi component.

The cover `<img>` in the face gets `crossorigin="anonymous"` only after that check passes. In the reverse order, every fan's cover images would fail to load (measured in the spike).

### Loading and precache (owner's decision: precache)

The renderer imports `pixi.js`, `pixi.js/html-source` and `pixi-filters/shockwave` dynamically, the way `dna-orb` loads Matter.js. The service worker's precache (vite-plugin-pwa `injectManifest`, which excludes only admin and organizer chunks) includes the chunk. The virtual ticket can then open with WebGL in a venue without signal.

## Risks / Trade-offs

- [The masked export races the repaint and leaks the full name] → Await the `paint` event before extracting, and test it with a unit test. The DOM path masks a clone, so it never depends on a repaint.
- [The 50 ms second draw is not enough on a slower iPhone] → Measure it on a real iPhone during the frontend work. If needed, make the delay longer or draw until the image's pixels change.
- [The CORS rollout order is reversed and cover images break for everyone] → The frontend task that adds `crossorigin` depends on the CORS check passing in production, and the task says so.
- [PixiJS 8.23 is late] → The DOM path is complete and ships first. The WebGL path is an addition.
- [A larger precache, about 340 KB gzip before optimisation, for every fan] → Owner accepted it. Importing only the shockwave filter is expected to shrink it; the bundle size is reported in the frontend PR.
- [HTML-in-Canvas changes shape again in Chrome] → Feature detection falls back to the DOM path, which is the Safari path and is tested on every PR.

## Migration Plan

1. cloud-provisioning: the CORS rule. Merge, then the owner runs the production `pulumi up`. Merging also auto-runs the dev `pulumi up`; dev is stopped, so that run is not verified.
2. Check the CORS header on a production cover URL with `curl`.
3. frontend, DOM path: the virtual ticket, the stamp and the share image, with `crossorigin` on the cover. Release.
4. frontend, WebGL path: after `pixi.js` 8.23 is on npm `latest`. Release.

Rollback: remove `crossorigin` (frontend) before removing the CORS rule. A build with `DB_VERSION` 1 cannot open a database already upgraded to version 2 (`VersionError`), and the fan would lose the offline ticket list. So the frontend is never rolled back to an older build. Instead, a fix-forward build turns the virtual ticket off and keeps `DB_VERSION` 2 and the new store.
