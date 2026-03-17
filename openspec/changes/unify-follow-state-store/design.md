## Context

`improve-search-bar` change で BubblePool.followedIds を public にし、テンプレートからの直接 Set 観測で dual-state バグを解消した。しかし follow 状態の管理は依然として BubblePool (Set)、DiscoveryRoute (followedArtists 配列)、Store (guest.follows、onboarding 時のみ) に分散している。

既存の `@aurelia/state` Store は onboarding/guest 状態を Redux スタイルで管理しており、reducer は pure function としてテスト可能。この仕組みを discovery の follow 状態にも拡張することで、状態管理を一元化する。

## Goals / Non-Goals

**Goals:**

- follow 状態の single source of truth を `@aurelia/state` Store に置く
- follow/unfollow/rollback を `dispatch()` のみで実行できるようにする
- reducer を pure function としてユニットテスト可能にする
- `@aurelia/state` のリアクティビティによりテンプレートバインディングを自動更新する
- BubblePool から follow 追跡の責務を除去し、pool 管理に集中させる

**Non-Goals:**

- Onboarding と Authenticated の follow フローの統合（現在 guest.follows と backend RPC で分岐するロジックはそのまま維持）
- follow 状態の localStorage 永続化（discovery slice は session-scoped; onboarding の guest.follows は既存の永続化で対応）
- DnaOrbCanvas の followedIds 参照方法の変更（canvas は引き続き外部から `followedIds` bindable を受け取る）

## Decisions

### 1. discovery slice の state shape: `followedArtists: FollowedArtist[]`

**選択**: `DiscoveryState.followedArtists` を `{ id: string; name: string; mbid: string }[]` として定義。

**理由**: `ArtistBubble` は UI 固有のプロパティ (x, y, radius, imageUrl) を含むため、Store に入れるべきではない。Store には follow 状態の判定とリスト表示に必要な最小限のフィールドのみ保持する。follow 判定用の `followedIds` (string[]) は getter で derived する。

**代替案**: `followedIds: string[]` のみ保持 → follow 済みアーティストの名前が必要な箇所 (seed similar, toast 等) で困るため却下。

### 2. `guest.follows` との関係: 共存、統合しない

**選択**: `discovery.followedArtists` と `guest.follows` を別 slice として共存させる。

**理由**:
- `guest.follows` は onboarding 専用で localStorage に永続化される（ページリロード後も復元）
- `discovery.followedArtists` は session-scoped（ページ遷移後は backend から再取得）
- Onboarding 時は `discovery/follow` dispatch と `guest/follow` dispatch を両方実行する（FollowServiceClient が後者を担当）
- 統合するとライフサイクルの違い（永続化 vs session）を混在させることになる

### 3. BubblePool.dedup: followedIds を引数で注入

**選択**: `dedup(bubbles: ArtistBubble[], followedIds: ReadonlySet<string>): ArtistBubble[]`

**理由**: BubblePool が Store に依存するのを避ける。BubblePool は plain class として DI 不要のままテスト可能。呼び出し側 (DiscoveryRoute) が Store から followedIds を取得して渡す。

### 4. テンプレートバインディング: Store state から derived getter

**選択**: DiscoveryRoute に以下の getter を追加:

```ts
public get followedIds(): ReadonlySet<string> {
  return new Set(this.store.getState().discovery.followedArtists.map(a => a.id))
}
```

テンプレートは `followedIds.has(artist.id)` でバインド。

**理由**: `@aurelia/state` の dispatch は Store 変更を Aurelia に通知し、Store を参照する getter のバインディングが再評価される。`improve-search-bar` change で導入した `followedIds.has()` のテンプレートパターンをそのまま維持できる。

**パフォーマンス**: followedArtists が < 100 件のため、毎回 Set を生成するコストは無視できる。将来的に問題になれば `@computed` でキャッシュ可能。

### 5. Optimistic update + rollback パターン

```ts
// follow
store.dispatch({ type: 'discovery/follow', artist: { id, name, mbid } })

// rollback (on error)
store.dispatch({ type: 'discovery/unfollow', artistId: id })
```

**理由**: reducer は pure function なので rollback も単純な dispatch。batch() も不要（1 dispatch = 1 state update）。

## Risks / Trade-offs

**[Risk] getter で毎回 `new Set()` を生成する** → < 100 件では問題にならない。プロファイリングで問題が見つかれば `@computed` でキャッシュする。

**[Risk] `@aurelia/state` の dispatch が getter バインディングの再評価をトリガーしない可能性** → 実装時にコンポーネントテストで検証。問題があれば `@watch` で明示的に observe する。

**[Trade-off] `guest.follows` と `discovery.followedArtists` の二重管理が残る** → ライフサイクルの違い（永続化 vs session）のため意図的に分離。統合は onboarding フローのリファクタリング時に検討。

## Open Questions

- `discovery.followedArtists` を persistenceMiddleware で localStorage に永続化する必要はあるか？（現状は session-scoped で十分と判断）
- canvas の `followedIds` bindable は Store 参照の getter 経由で更新されるか、または明示的な `@watch` が必要か？
