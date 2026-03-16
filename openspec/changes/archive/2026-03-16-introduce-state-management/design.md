## Context

フロントエンドは現在、Aurelia 2 の DI コンテナで Singleton サービスを登録し、各サービスの `@observable` プロパティと `IEventAggregator` で状態を共有している。オンボーディング（7ステップ・3ページ横断）とゲストデータ管理（follow/home の localStorage 永続化）で、状態遷移ロジックが複数コンポーネントに散在し、暗黙的な協調が発生している。

`@aurelia/state` は Redux-like な単一ストア（Action dispatch → Reducer → 新 State）を提供する Aurelia 公式プラグイン。既存の DI サービスと共存可能で、段階的な移行ができる。

## Goals / Non-Goals

**Goals:**
- オンボーディングとゲストデータの状態を `@aurelia/state` Store に集約し、状態遷移を明示的にする
- localStorage 永続化を Middleware に統一し、各サービスでの手動管理を排除する
- DevTools (time-travel debugging) によるオンボーディングフローのデバッグ性向上

**Non-Goals:**
- Auth, Error, Notification, PWA Install 状態の Store 移行（現状の DI サービスで十分）
- バックエンド・protobuf・インフラの変更
- 全コンポーネントのローカル状態の Store 化（ページローカル状態はコンポーネントに残す）
- RxJS や他の状態管理ライブラリの導入

## Decisions

### 1. Store スコープ: オンボーディング + ゲストデータのみ

**選択**: AppState にはオンボーディングとゲストデータだけを含め、他の共有状態は既存 DI サービスのまま維持する。

**代替案**: 全共有状態を Store に移行する → 既存サービス（AuthService 等）は外部ライブラリ（oidc-client-ts）と密結合しており、Store 化のメリットが薄く移行コストが高い。

**理由**: 「痛みがある箇所」だけを移行することで、導入リスクを最小化しつつ最大の効果を得る。

### 2. AppState 型設計

```typescript
interface AppState {
  onboarding: {
    step: OnboardingStep           // enum: 0-7
    spotlightTarget: string | null
    spotlightMessage: string | null
    spotlightRadius: number
    spotlightActive: boolean
  }
  guestArtists: {
    follows: GuestFollow[]         // { artistId, name }
    home: string | null            // ISO 3166-2 code
  }
}
```

**理由**: 既存の `OnboardingService` と `LocalArtistClient` が持つプロパティをそのまま型に落とし込む。`onSpotlightTap` コールバックは状態ではなくイベントなので Store に含めない（dispatch で代替）。

### 3. Action 定義: Discriminated Union

```typescript
type AppAction =
  | { type: 'onboarding/advance'; step: OnboardingStep }
  | { type: 'onboarding/setSpotlight'; target: string; message: string; radius?: number }
  | { type: 'onboarding/clearSpotlight' }
  | { type: 'onboarding/complete' }
  | { type: 'onboarding/reset' }
  | { type: 'guest/follow'; artistId: string; name: string }
  | { type: 'guest/unfollow'; artistId: string }
  | { type: 'guest/setUserHome'; code: string }
  | { type: 'guest/clearAll' }
```

**理由**: TypeScript の discriminated union により、dispatch 時の型安全性を確保。Action 名は `domain/verb` 形式で意図を明示する。

### 4. localStorage Middleware

```
dispatch(action)
  → [before] loggingMiddleware (dev only)
  → reducer(state, action) → newState
  → [after] persistenceMiddleware
      → localStorage に onboarding.step, guestArtists を書き込み
```

**選択**: Middleware の `After` placement で永続化を行う。

**代替案**: Reducer 内で localStorage を直接操作する → Reducer の純粋性が壊れ、テスタビリティが下がる。

**理由**: 関心の分離。Reducer は純粋関数、Middleware が副作用を担当。

### 5. 既存サービスとの共存パターン

`OnboardingService` と `LocalArtistClient` は Store の薄いファサードとしてリファクタリングする:

```
[コンポーネント] → store.dispatch(action)     // 状態変更
[コンポーネント] → store.getState().onboarding // 状態参照
```

既存サービスのインターフェース（`IOnboardingService`, `ILocalArtistClient`）は削除し、コンポーネントが `IStore<AppState, AppAction>` を直接 inject する。

**理由**: ファサードを残すとストアとサービスの二重管理になり、どちらが正なのか曖昧になる。Store 導入の目的は状態の一元管理なので、中間層は不要。

### 6. GuestDataMergeService の変更

`GuestDataMergeService` は `store.getState().guestArtists` からゲストデータを読み取り、マージ完了後に `store.dispatch({ type: 'guest/clearAll' })` で状態をクリアする。サービス自体は DI に残す（RPC 呼び出しのオーケストレーションは Store の責務外）。

## Risks / Trade-offs

**[Store と DI サービスの二重パラダイム]** → 一部が Store、一部が DI サービスという混在は新規メンバーの学習コストになる。対策: Store に載せる基準（「複数ページ横断 + localStorage 永続化が必要な状態」）をドキュメント化する。

**[OnboardingService 削除の影響範囲]** → 5+ コンポーネントが inject しているため、全てを `IStore` inject に書き換える必要がある。対策: タスクを段階的に分割し、コンポーネントごとに移行。

**[Middleware での localStorage 操作の暗黙性]** → Reducer の結果が自動的に永続化されるため、「いつ localStorage に書かれるか」が見えにくくなる。対策: Middleware のログ出力と DevTools で可視化。

**[テスト書き換えコスト]** → OnboardingService・LocalArtistClient の既存テストを Store ベースに全面書き換え。対策: Reducer は純粋関数なのでテスト自体はシンプルになる。
