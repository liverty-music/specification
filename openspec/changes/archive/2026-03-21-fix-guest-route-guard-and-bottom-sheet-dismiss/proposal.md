## Why

`isCompleted` ゲスト（オンボーディング完了・未サインアップ）への route guard が全ルートを無制限に許可しており、仕様を超えた動作をしている。また `bottom-sheet` の外タップ dismiss が機能しておらず、`hype-notification-dialog` をタップアウトで閉じることができない。さらに、`isCompleted` ゲストが dashboard に再アクセスした際に `user-home-selector` が再表示される（`guest/setUserHome` の dispatch がオンボーディング中のみに限定されていた）。signup-prompt-banner には dismiss 手段がなく、ユーザーが閉じることができない。

## What Changes

- **Route guard (auth-hook)**: `isCompleted` ゲストに許可するルートを `dashboard`・`discovery`・`my-artists` の 3 ルートに限定する。`tickets`・`settings` 等の認証必須ルートにアクセスした場合は LP へリダイレクトせず、現在のページにとどまりつつ "login required" toast を表示する。
- **bottom-sheet dismiss**: `onBackdropClick` の `event.target !== this.scrollWrapper` 比較を修正する。現状、`.dismiss-zone` クリック時に `event.target` が子要素になるため条件が失敗し dismiss が機能しない。dismiss-zone クリックを正しく検出するよう修正する。
- **user-home-selector 再表示バグ**: `dashboard-route.ts` の `onHomeSelected()` で `guest/setUserHome` dispatch を `isOnboarding` 条件の外に移動し、`isCompleted` ゲストが home を選択した際にも localStorage に永続化する。
- **signup-prompt-banner dismiss ボタン**: × ボタンを追加し、`banner-dismissed` CustomEvent を dispatch。親ルートで `showSignupBanner = false` にセットする。

## Capabilities

### New Capabilities

なし

### Modified Capabilities

- `onboarding-tutorial`: `isCompleted` ゲストが利用可能なルートの要件を追加（dashboard / discovery / my-artists のみ許可）。`guest/setUserHome` の永続化を `isCompleted` ゲストにも適用。
- `bottom-sheet-ce`: `onBackdropClick` の dismiss-zone クリック検出要件を修正
- `signup-prompt-banner`: × dismiss ボタンの追加と `banner-dismissed` イベントの要件を追加

## Impact

- `src/hooks/auth-hook.ts`: Priority 3 の `isCompleted` ゲスト判定ロジック変更
- `src/components/bottom-sheet/bottom-sheet.ts`: `onBackdropClick` の event.target チェック修正
- `src/routes/dashboard/dashboard-route.ts`: `onHomeSelected()` の dispatch 修正
- `src/components/signup-prompt-banner/signup-prompt-banner.ts`: dismiss ボタン追加
- `src/components/signup-prompt-banner/signup-prompt-banner.html`: × ボタン追加
- `src/components/signup-prompt-banner/signup-prompt-banner.css`: dismiss ボタンスタイル
- `src/routes/my-artists/my-artists-route.ts`: `onBannerDismissed()` ハンドラ追加
- `src/routes/my-artists/my-artists-route.html`: `banner-dismissed.trigger` 追加
- `src/locales/en/translation.json`, `src/locales/ja/translation.json`: `common.dismiss`, `auth.loginRequired` キー追加
- `test/hooks/auth-hook.spec.ts`: isCompleted ゲストのルート別アクセス制御テスト追加
