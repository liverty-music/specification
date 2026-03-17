## 1. Follow 状態のリアクティビティ修正

- [x] 1.1 `BubblePool.followedIds` を `private` → `public readonly` に変更
- [x] 1.2 `DiscoveryRoute` に `public get followedIds(): ReadonlySet<string>` getter を追加（`this.pool.followedIds` を返す）
- [x] 1.3 `DiscoveryRoute.poolFollowedIds` プロパティを削除
- [x] 1.4 `DiscoveryRoute.isArtistFollowed()` メソッドを削除
- [x] 1.5 `followArtist()` 内の `poolFollowedIds` 手動同期コード（`new Set(...).add()` と rollback の `Set.delete()`）を削除
- [x] 1.6 テンプレートのバインディングを `isArtistFollowed(artist.id)` → `followedIds.has(artist.id)` に変更（disabled, data-followed, if.bind すべて）

## 2. 検索結果の行全体タップ化

- [x] 2.1 `<li>` 要素に `click.trigger="onFollowFromSearch(artist)"` を追加
- [x] 2.2 `<li>` に `followedIds.has(artist.id)` による disabled 判定を追加（follow 済みならイベント無視）
- [x] 2.3 `<button class="follow-button">` と `<svg-icon name="plus">` を削除
- [x] 2.4 follow 済み行に ✓ アイコンを表示（`<svg-icon if.bind="followedIds.has(artist.id)" name="check">`）
- [x] 2.5 CSS: `.result-item` にインタラクティブスタイル追加（cursor: pointer, hover/active 背景色変化, 最小 48px 高さ）
- [x] 2.6 CSS: follow 済み行のスタイル（opacity 低下、cursor: default）
- [x] 2.7 CSS: `.follow-button` 関連スタイルを削除

## 3. Follow 後の吸収アニメーション

- [x] 3.1 `DnaOrbCanvas` に `spawnAndAbsorb(artist: ArtistBubble, x: number, y: number)` メソッドを追加
- [x] 3.2 `spawnAndAbsorb` 内: physics body 作成 → 即 remove → AbsorptionAnimator 開始 → injectColor → need-more-bubbles イベント dispatch
- [x] 3.3 `DiscoveryRoute.onFollowFromSearch()` のフローを変更: followArtist → exitSearchMode → clearSearch → canvas resume → spawnAndAbsorb（バブルエリア上部 15-20%）
- [x] 3.4 follow 失敗時は検索モードに留まるようエラーハンドリングを調整

## 4. テスト

- [x] 4.1 `BubblePool` ユニットテスト: `markFollowed` 後に `followedIds.has()` が `true` を返すことを検証
- [x] 4.2 `BubblePool` ユニットテスト: `unmarkFollowed` 後に `followedIds.has()` が `false` を返すことを検証
- [x] 4.3 `BubblePool` ユニットテスト: `dedup` が followed artist を除外することを検証
- [x] 4.4 `make check` が通ることを確認（lint + test）
