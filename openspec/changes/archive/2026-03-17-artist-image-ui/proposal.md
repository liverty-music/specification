## Why

Artist cards on the dashboard and my-artists page display only text names with generated HSL colors. The backend now serves fanart.tv image data (logos, thumbnails, backgrounds) via the Artist.fanart proto field, but the frontend does not consume it yet. Displaying real artist images significantly improves visual recognition and the overall fan experience.

## What Changes

- Replace artist name text with transparent logo image (`hd_music_logo` / `music_logo`) on dashboard event cards, falling back to existing text when no logo is available
- Add a hero background image (`artist_background`) to the event detail sheet when available, expanding the sheet vertically to accommodate the image above the existing content
- Use artist thumbnail (`artist_thumb`) as background image on my-artists grid tiles, falling back to the existing gradient when unavailable

## Capabilities

### New Capabilities

- `artist-image-ui`: Display fanart.tv artist images (logos, thumbnails, backgrounds) across dashboard and my-artists UI components

### Modified Capabilities

None. The backend already serves Fanart data in the Artist proto message. This change is frontend-only consumption.

## Impact

- **Frontend**: Changes to `follow-service-client.ts` (fanart field mapping), `live-event.ts` (new image URL fields), `event-card` component (logo display), `event-detail-sheet` component (hero image), `my-artists-route` (grid tile backgrounds)
- **Proto**: No changes required. `Artist.fanart` already provides all needed image URLs
- **Backend**: No changes required. RPC mapper already populates Fanart in Artist responses
