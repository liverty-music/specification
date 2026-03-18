## Why

Onboarding 完了後に `/dashboard` へ遷移すると、`querySelector('')` が呼ばれて `InvalidSelectorError` が発生する。`@aurelia/state` の Store dispatch で `spotlightTarget` と `spotlightActive` が同時に変更された際、Aurelia のバインディング更新順序が非決定的であるため、`targetSelector` が空文字に変わった時点でまだ `active` が `true` のままコールバックが発火するレースコンディションが原因。

## What Changes

- `coach-mark.ts` の `findAndHighlight()` メソッドに空セレクタの早期リターンガードを追加
- `querySelector` に無効な引数が渡されることを防止

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `onboarding-spotlight`: coach-mark コンポーネントが空セレクタに対して防御的に振る舞うようになる

## Impact

- `frontend/src/components/coach-mark/coach-mark.ts` — 1行の早期リターン追加
- 他のコンポーネント・サービス・API への影響なし
