# Tasks

## 1. Usecase (components/usecase/media/process-media)

- [x] 1.1 Register the WebP decoder in the media processor's safety-check and decode paths so a WebP original is recognized and processed like JPEG/PNG, and verify the "Valid photo" and "WebP original" scenarios pass via a unit test with a WebP fixture (liverty-music/backend#492, liverty-music/backend#501, liverty-music/backend#502)
- [x] 1.2 Verify the "Decompression bomb" scenario still rejects an oversized image before full decode (no regression) (liverty-music/backend#501 — existing pre-decode edge/pixel checks are unchanged, covered by a dedicated test)
