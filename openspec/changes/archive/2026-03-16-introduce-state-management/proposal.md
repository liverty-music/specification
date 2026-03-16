## Why

フロントエンドの状態管理が Singleton DI サービス + `@observable` + `IEventAggregator` の3パターンに分散しており、特にオンボーディングフロー（3ページ横断・7ステップ）とゲストデータ管理で状態の流れが暗黙的になっている。`@aurelia/state` を部分導入し、複雑な共有状態を Redux-like な単一ストアに集約することで、状態遷移の可視化・デバッグ性・保守性を改善する。

## What Changes

- `@aurelia/state` パッケージを導入し、`StateDefaultConfiguration` で Store を登録
- オンボーディング状態（ステップ遷移・スポットライト制御）を `OnboardingService` から Store の Reducer に移行
- ゲストアーティスト状態（follow/unfollow・ホームエリア設定）を `LocalArtistClient` から Store の Reducer に移行
- localStorage 永続化を Middleware として実装し、手動の `StorageKeys` 管理を置き換え
- 既存の Auth, Error, Notification, PWA 関連サービスは現状維持（Store に移行しない）

## Capabilities

### New Capabilities
- `state-management`: `@aurelia/state` Store の設定、AppState 型定義、Action 型定義、Reducer 実装、Middleware 実装

### Modified Capabilities
- `frontend-onboarding-flow`: オンボーディングのステップ遷移と spotlight 制御が Store dispatch ベースに変更
- `artist-following`: ゲストユーザーの follow/unfollow 操作が Store dispatch ベースに変更
- `user-home`: ゲストユーザーのホームエリア設定が Store dispatch ベースに変更
- `guest-data-merge`: マージ時のゲストデータ取得元が Store に変更

## Impact

- **Frontend のみ**: バックエンド・protobuf・インフラへの変更なし
- **依存追加**: `@aurelia/state` パッケージ
- **影響コンポーネント**: OnboardingService, LocalArtistClient, DiscoverPage, Dashboard, MyArtistsPage, GuestDataMergeService, main.ts (Store 登録)
- **テスト**: OnboardingService・LocalArtistClient の既存テストを Store ベースに書き換え
