# Tasks

## 1. Usecase (components/usecase/media/process-media)

- [x] 1.1 Register the WebP decoder in the media processor's safety-check and decode paths so a WebP original is recognized and processed like JPEG/PNG, and verify the "Valid photo" and "WebP original" scenarios pass via a unit test with a WebP fixture (liverty-music/backend#492)
- [x] 1.2 Verify the "Decompression bomb" scenario still rejects an oversized image before full decode (no regression) (liverty-music/backend#492 — existing pre-decode edge/pixel checks are unchanged and covered by the same test build)
