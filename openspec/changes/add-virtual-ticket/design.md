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

- **WebGL path:** the face drawn on screen is the live DOM face, so masking it would also mask what the fan sees. The on-screen canvas is frozen while the masked texture exists:
  1. Stop the ticker, so the visible canvas keeps its last frame, and set `aria-busy="true"` on the face, so assistive technology does not announce the masked text in the two paints it lasts.
  2. Set `data-share` on the live face, and wait for the next `paint` of the `HTMLSource`.
  3. Extract the face sprite's frame. The design assumes that `extract` renders into an offscreen render texture and not into the visible canvas; task 4.4 verifies this by capturing the visible canvas during an export.
  4. In a `finally` block, so a failure never leaves the face masked or frozen: remove `data-share` and `aria-busy`, wait for the next `paint`, then restart the ticker.

  The first wait is what keeps the export masked: the spike exported the unmasked face without it. The frozen ticker is what keeps the view unchanged. A unit test fakes the paint events and asserts the order (ticker stopped, mask, paint, extract, unmask, paint, ticker restarted), including when the extract throws.
- **DOM path:**
  1. Clone the face and set `data-share` on the clone only, so the view never changes. In the clone, the cover `<img>` is hidden, so the cover's area is transparent.
  2. Fetch the cover (this needs the CORS header) and decode it with `createImageBitmap`.
  3. Serialise the clone and the face's CSS into an SVG `foreignObject` image.
  4. On the export canvas, draw the cover bitmap into the cover's rectangle (measured on the live face, cropped as `object-fit: cover` crops it), then draw the SVG image over it, and call `toBlob`.

  The cover is drawn directly and never as an image nested in the SVG. WebKit misses nested images on the first draw (the spike needed a second draw about 50 ms later), and with no iPhone available, no delay could be measured. Drawing the cover directly removes the wait altogether. When the cover cannot be fetched (no connection, or an event without a cover), the image is made without it, as the face is shown without it.

  iOS uses the system font. The owner accepted this, so web fonts are not inlined.
- **Hand-off:** wrap the blob in `File([blob], 'liverty-ticket.png', { type: 'image/png' })`. Use `navigator.share({ files })` when `navigator.canShare({ files })` is true; otherwise download through an object URL.

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

### Loading and precache (owner's decision: precache)

The renderer imports `pixi.js`, `pixi.js/html-source` and `pixi-filters/shockwave` dynamically, the way `dna-orb` loads Matter.js. The service worker's precache (vite-plugin-pwa `injectManifest`, which excludes only admin and organizer chunks) includes the chunk. The virtual ticket can then open with WebGL in a venue without signal.

## Risks / Trade-offs

- [The masked export races the repaint and leaks the full name] → Await the `paint` event before extracting, and test it with a unit test. The DOM path masks a clone, so it never depends on a repaint.
- [WebKit drops images nested in an SVG `foreignObject` on the first draw] → The DOM-path export draws the cover bitmap directly onto the canvas, so it does not depend on WebKit's timing. This is verified in Playwright WebKit only, because the owner has no iPhone.
- [The CORS rollout order is reversed and cover images break for everyone] → The frontend task that adds `crossorigin` depends on the header check passing in production, and the task says so.
- [PixiJS 8.23 is late] → The DOM path is complete and ships first. The WebGL path is an addition.
- [A larger precache, about 340 KB gzip before optimisation, for every fan] → Owner accepted it. Importing only the shockwave filter is expected to shrink it; the bundle size is reported in the frontend PR.
- [HTML-in-Canvas changes shape again in Chrome] → Feature detection falls back to the DOM path, which is the Safari path and is tested on every PR.

## Migration Plan

1. cloud-provisioning: the CORS response header on the CDN backend bucket. Merge, then the owner runs the production `pulumi up`. Merging also auto-runs the dev `pulumi up`; dev is stopped, so that run is not verified.
2. Check the header on an existing production cover URL with `curl`.
3. frontend, DOM path: the virtual ticket, the stamp and the share image, with `crossorigin` on the cover. Release.
4. frontend, WebGL path: after `pixi.js` 8.23 is on npm `latest`. Release.

Rollback: remove `crossorigin` (frontend) before removing the header. A build with `DB_VERSION` 1 cannot open a database already upgraded to version 2 (`VersionError`), and the fan would lose the offline ticket list. So the frontend is never rolled back to an older build. Instead, a fix-forward build turns the virtual ticket off and keeps `DB_VERSION` 2 and the new store.
