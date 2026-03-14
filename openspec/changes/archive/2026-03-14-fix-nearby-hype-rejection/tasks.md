## 1. Proto (specification repo)

- [x] 1.1 `follow_service.proto`: `SetHypeRequest.hype` から `not_in: [3]` を削除
- [x] 1.2 `follow.proto`: `HYPE_TYPE_NEARBY` のコメントから "Reserved for Phase 2; not exposed in the UI selector." を削除し、他ティアと同等の説明に更新
- [x] 1.3 `buf lint` / `buf breaking` 通過を確認

## 2. Frontend (frontend repo)

- [x] 2.1 `my-artists-page.ts`: `HYPE_META` → `HYPE_TIERS` にリネーム
- [x] 2.2 `my-artists-page.ts`: `HYPE_LEVELS` を削除し `HYPE_TIERS` から導出
- [x] 2.3 `my-artists-page.ts`: `HYPE_TYPE_TO_STOP` → `HYPE_TO_STOP`、`HYPE_STOP_TO_TYPE` → `HYPE_FROM_STOP` にリネーム
- [x] 2.4 テンプレート・テストファイルの参照を更新
- [x] 2.5 `make check` 通過を確認（lint/typecheck エラーは既存の環境問題で、本変更起因ではない）
