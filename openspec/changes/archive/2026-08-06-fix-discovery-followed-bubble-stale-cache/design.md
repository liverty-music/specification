## Context

`ArtistStore` はシングルトンとして `lastBubbles` に最後に生成されたバブルプールをキャッシュし、
`DiscoveryRoute` の re-entry 時に `peekBubbles()` で即時描画を実現する。

問題は `setBubbles()` が `loadInitialBubbles()` 完了時にのみ呼ばれる点にある。
セッション中にバブルをタップしてフォローしても、キャッシュは更新されない。
次の re-entry で `peekBubbles()` が返すプールにはフォロー済みアーティストが残っており、
`pool.replace()` → `artistsChanged()` → `physics.addBubbles()` の経路でバブルが物理エンジンに追加され、
`renderBubble()` の `isFollowed ? opacity * 0.4` でバブルが薄く表示される。

## Goals / Non-Goals

**Goals:**
- re-entry 時にフォロー済みアーティストのバブルが表示されなくなる
- `renderBubble()` の `isFollowed` 条件分岐（opacity 0.4）を削除してコードをシンプルにする

**Non-Goals:**
- セッション中のフォロー発生時にキャッシュをリアルタイム更新すること（タップ後即座にバブルは物理的に消えているため不要）
- 50バブル上限修正（別 change `discovery-perf-instrumentation-and-bubble-cap` で対応）

## Decisions

### D1: フィルタはキャッシュ「読み込み時」に行う

**選択**: `loading()` で `peekBubbles()` した直後に `followedIds` でフィルタする。

```typescript
// Before
this.bubbles.pool.replace(cachedBubbles)

// After
const filteredCache = cachedBubbles.filter(a => !this.followStore.followedIds.has(a.id))
this.bubbles.pool.replace(filteredCache)
```

**理由**: フォロー時にキャッシュを更新する方式（書き込み側フィルタ）だと、
`onArtistSelected` / `onFollowFromSearch` の 2 箇所にキャッシュ更新コードが必要になり、
将来のフォロー経路が増えたときに漏れる。読み込み側で一元的にフィルタする方が、
「キャッシュは生プールを保持し、消費時に除外する」という責務分離が明確で保守しやすい。

### D2: `renderBubble()` の `isFollowed` 分岐を削除する

`isFollowed ? opacity * 0.4` は、本来現れないはずのフォロー済みバブルへのフォールバック描画だった。

**適用前提**: 実装時に `onFollowFromSearch` がフォロー済みバブルを物理エンジンから除去していることを確認すること（`pool.remove()` 等）。タップによるフォロー（`onArtistSelected`）はバブル吸収アニメーションで除去されるが、検索フォローは別コードパスである。除去できていない場合、この分岐を削除すると該当バブルが dimmed → full opacity になり regression となるため、D2 は適用せず分岐を残すこと。

除去が確認できた場合、D1 の修正後は到達不能になるため削除してコードをシンプルにする。
`showFollowedIndicator` バインダブルと `followedIds` バインダブルも、他に利用箇所がなくなれば削除対象とする。

## Risks / Trade-offs

- **[リスク] フィルタ後プールが空になる** → `loadInitialBubbles()` がバックグラウンドで即座に走り新アーティストをロードするため、ゴーストバブル UX で空にならない（`loading()` 内の ghost artist パスが引き続き機能する）
- **[リスク] `followedIds` が `loading()` 時点で未ロード** → `FollowStore` は Dashboard 起動時に `loadFollowed()` を完了させており、Discovery の `loading()` が呼ばれる時点では `followedIds` が populated されている。この前提が実装上崩れる場合（初回起動直後に Discovery へ直接遷移するケースなど）は、`loading()` 内で follow データのロード完了を `await` してからフィルタを適用すること
