## Why

ダッシュボードの使用頻度が上がるにつれて、UX 上の細かな摩擦点が積み重なってきた。PWA 更新通知のアクションボタンが目立たず更新を見逃すリスク、レーザービームエフェクトが一部ユーザーに不快感を与える、コンサート日付一覧で月・年の境界が分かりにくい、絞り込みシートのアーティスト欄が多アーティスト時にチケット状況欄を押し出す、bottom sheet のスワイプ dismiss が遅くかつ誤操作でシートが戻ってくるという5点を、単一の UI ポリッシュ変更としてまとめて対処する。

## What Changes

- **PWA 更新スナックバー**: 「更新」アクションボタンを pill 形状 + pulse アニメーションで強調し、ユーザーが即座に更新を促せるようにする
- **レーザービームエフェクト toggle**: spotlight アイコンのトグルボタンをダッシュボードヘッダー（絞り込みボタン隣）に追加。デフォルト off、localStorage で永続化
- **コンサート日付 月境界セパレーター**: 月が変わる最初の日付グループの前に "──── 2026年7月 ────" 形式のセパレーターを挿入（常に年を含む）
- **絞り込みシート アーティスト欄高さ制限**: `.artists-list` に `max-height: 40dvh; overflow-y: auto` を追加し、チケット状況セクションと完了ボタンが常に表示されるようにする
- **絞り込みシート セクション区別**: `filter-facet` 間に hairline separator + heading を uppercase に変更してセクション境界を明確化
- **Bottom sheet swipe dismiss 改善**: close アニメーション duration を 240ms → 160ms に短縮、snap-to-dismiss-zone 後に `pointer-events: none` でバウンスバックを防止、`pointerup` 時点の早期クローズ検出を追加

## Capabilities

### New Capabilities

- `beam-effect-toggle`: ユーザーがレーザービームエフェクトの表示/非表示を切り替えられるダッシュボードのトグル機能。設定は localStorage に永続化し、デフォルトは off

### Modified Capabilities

- `pwa-update-lifecycle`: 更新通知スナックバーのアクションボタンに視覚的強調（pill + pulse）を追加する要件
- `bottom-sheet-ce`: スワイプ dismiss のレスポンス要件を強化（dismiss zone snap 後の逆戻り防止、早期クローズ検出）

## Impact

- **Frontend only** — proto/RPC 変更なし、BSR gen 不要
- 変更対象: `frontend/src/components/snack-bar/`, `frontend/src/components/bottom-sheet/`, `frontend/src/components/artist-filter-bar/`, `frontend/src/components/live-highway/`, `frontend/src/components/svg-icon/`, `frontend/src/routes/dashboard/`, `frontend/src/constants/storage-keys.ts`
- localStorage キー追加: `liverty:beams:enabled`（既存の naming convention に準拠）
- Breaking changes: なし
