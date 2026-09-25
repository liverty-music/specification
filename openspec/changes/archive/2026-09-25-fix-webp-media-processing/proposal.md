## Why

`CreateMediaUploadURL` accepts `image/webp` and authorizes the upload, but `ProcessMedia` currently rejects every WebP original outright (no variants, original deleted, cover unchanged). An organizer who uploads a WebP cover is told the upload is authorized, uploads successfully, and then silently loses the image with no explanation. The fix is to make `ProcessMedia` process WebP the same way it processes JPEG and PNG, so accepted content types and processed content types agree.

## What Changes

- `ProcessMedia` accepts a WebP original in addition to JPEG and PNG, subject to the same pre-decode safety limits (8000 px per edge, 50,000,000 px total).
- A WebP original produces thumb (≤800 px wide) and large (≤1920 px wide) WebP variants with EXIF/metadata stripped, identical to the JPEG/PNG path.
- SVG and corrupt/unrecognized files remain rejected (no variants, original deleted, not retried).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/usecase/media/process-media`: "Only safe images become variants" now accepts WebP originals (in addition to JPEG and PNG) and produces variants for them; the "WebP original" scenario is replaced with one showing WebP producing variants like any other accepted type.

## Impact

- Affected code: `backend/internal/adapter/event/media_processor_vips.go` (register the WebP decoder so the magic-byte safety check and libvips decode both recognize `image/webp`).
- No API/proto changes — `CreateMediaUploadURL`'s accepted-types contract (`components/usecase/media/create-media-upload-url`) is unchanged; this change only brings `ProcessMedia` into agreement with it.
- No entity changes; `Media` and its operations are unaffected.
