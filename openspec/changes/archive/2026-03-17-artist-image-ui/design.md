## Context

The backend Artist proto message now includes an optional `Fanart` field with five image types: `artist_thumb` (1000x1000 portrait), `artist_background` (1920x1080 backdrop), `hd_music_logo` (800x310 transparent), `music_logo` (400x155 transparent), and `music_banner` (1000x185 wide). The RPC mapper (`ArtistToProto`) correctly maps `entity.Fanart` to proto when present, and the `artist-image-sync` CronJob populates the `artist_fanart` table from fanart.tv.

However, the `ListFollowed` RPC's SQL query (`followListByUserQuery`) only selects `a.id, a.name, a.mbid, fa.hype` from the `artists` table — it does not JOIN `artist_fanart`, so `entity.Artist.Fanart` is always `nil` in the response. The backend needs to be updated to load fanart data when listing followed artists.

The frontend currently:
- Uses hash-based HSL colors (`artistColor(name)`) as the sole visual identifier
- Has no `<img>` elements anywhere in the app
- Dashboard events are rendered via `event-card` component with `artist-color` custom attribute
- My-artists grid tiles use CSS gradients derived from the generated color
- Both Dashboard and My Artists call `ListFollowed` but the response never contains fanart data due to the missing JOIN

## Goals / Non-Goals

**Goals:**
- Display artist logos on dashboard event cards (replacing text when available)
- Show artist background images in the event detail sheet hero area
- Use artist thumbnails as grid tile backgrounds on the my-artists page
- Graceful fallback to existing HSL color visuals when images are unavailable

**Non-Goals:**
- Image caching or service worker preloading (browser cache is sufficient for now)
- My-artists list view changes (list view keeps existing dot + text layout)
- DNA Orb / discovery bubble images (Canvas-based, high implementation cost)
- Downloading/self-hosting images (continue using fanart.tv CDN URLs directly)

## Decisions

### 1. Data Flow: Extend existing ListFollowed mapping

Add fanart URL fields to the existing `FollowedArtistInfo` and `LiveEvent` interfaces. Extract URLs in the service client layer with the logo fallback chain: `hd_music_logo?.value ?? music_logo?.value`.

**Why**: No new RPC calls needed. The data is already in the ListFollowed response but currently discarded during mapping. Minimal change surface.

### 2. Image Loading: Native `<img>` with `loading="lazy"` + `decoding="async"`

Use standard `<img>` elements with native lazy loading rather than IntersectionObserver or a custom component.

**Why**: All target browsers support `loading="lazy"`. No JavaScript overhead. The `decoding="async"` attribute prevents main-thread blocking during decode. Combined with fanart.tv CDN, this is sufficient for the image count (tens, not hundreds).

### 3. Event Card Logo: Conditional `<img>` / `<span>` swap

```html
<img if.bind="event.logoUrl" src.bind="event.logoUrl" ... />
<span else class="artist-name">${event.artistName}</span>
```

Transparent PNG logos on the existing `artist-color` gradient background. Constrain with `max-block-size` and `object-fit: contain` to fit card proportions.

**Why**: Logos are transparent, so they naturally layer over the existing color scheme. Keeping the color background ensures visual consistency between logo and non-logo cards.

### 4. Detail Sheet Hero: Conditional image block above header

Insert a `<div class="sheet-hero">` with `background-image` above the existing `sheet-artist-header`. Only rendered when `artist_background` URL exists. Use `aspect-ratio: 16/9` with `object-fit: cover` and a bottom gradient fade into the sheet background.

**Why**: The 1920x1080 background images are cinematic and benefit from a dedicated display area. Placing above (not behind) text avoids readability issues. Conditional rendering means no layout shift for artists without backgrounds.

### 5. Grid Tile Thumbnail: CSS `background-image` with gradient overlay

Set `artist_thumb` as `background-image` on the grid tile, layered under the existing gradient overlay (`linear-gradient(to top, black/60%, transparent)`). Fall back to the existing color gradient when no thumbnail is available.

**Why**: The existing gradient overlay already provides text readability. Adding a photo underneath maintains the same text contrast. CSS `background-image` with `onerror` fallback (clear the URL) handles broken images gracefully.

### 6. Fanart Data Propagation: Dashboard uses a fanart lookup map

Dashboard currently maps concerts to `LiveEvent` objects. Concert data includes `artistId` but not Artist details. Build a `Map<artistId, FanartUrls>` from the `ListFollowed` response, then look up fanart URLs when constructing `LiveEvent` objects.

**Why**: Dashboard already calls `ListFollowed` (for hype levels). Enriching `LiveEvent` with image URLs from the same response avoids additional RPC calls. Artists not in the followed list simply have no images (acceptable — dashboard only shows followed artists' concerts).

## Risks / Trade-offs

**[fanart.tv CDN availability]** — Images load from fanart.tv's CDN. If slow or down, cards show fallback text/color immediately; images pop in when loaded. No loading spinners to avoid visual noise.

**[Large background images on mobile]** — `artist_background` is 1920x1080. On slow connections, the detail sheet hero may load slowly. Acceptable because the sheet content below is usable immediately; the hero is enhancement-only.

**[No image for most artists]** — fanart.tv coverage skews toward popular artists. Many followed artists will have no images, so the HSL color fallback must remain polished — it's not a degraded state, it's the default state with images as progressive enhancement.
