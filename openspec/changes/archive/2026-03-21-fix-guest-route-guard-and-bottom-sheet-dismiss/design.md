## Context

### Route Guard (auth-hook)

現在の `AuthHook.canLoad` Priority 3 は以下のように実装されている：

```typescript
if (this.onboarding.isCompleted) return true  // 全ルートを許可
```

これにより `isCompleted` ゲストが `tickets`・`settings` など認証を要するルートにもアクセスできる。
仕様では `isCompleted` ゲストは dashboard / discovery / my-artists の 3 ルートのみ利用できることが想定されている。

また、現在は未許可ルートへのアクセス時に LP (`''`) へリダイレクトしているが、これはユーザーが意図せずページを離れる体験になる。ナビゲーションをキャンセルしてその場に留めつつ toast でフィードバックを返す方が適切。

### bottom-sheet dismiss

`onBackdropClick` の早期 return 条件：

```typescript
if (event.target !== this.scrollWrapper) return
```

HTML 構造上、`scrollWrapper` は `.dismiss-zone` と `.sheet-page` の親要素であり、これらの子要素をクリックした際は `event.target` がそれら子要素になる（イベントバブリングの仕様）。
`.dismiss-zone` クリック時に `event.target` は `<div class="dismiss-zone">` になるため、条件が `false` になり即 return される。

`popover="auto"` の light-dismiss（Escape / click-outside）も、click イベントが `scroll-wrapper` の `click.trigger` で消費されるため正常に機能しない。

### user-home-selector 再表示バグ

`dashboard-route.ts` の `onHomeSelected()` で `store.dispatch({ type: 'guest/setUserHome', code })` が `if (this.isOnboarding)` ブロック内にのみ存在していた。auth-hook の Priority 3 修正により `isCompleted` ゲストが dashboard に直接到達できるようになったが、`isOnboarding` は `false` のため dispatch が走らず、localStorage に home が保存されない。次回アクセス時に store の `guest.home` が空のため `user-home-selector` が再表示される。

### signup-prompt-banner に dismiss 手段がない

`signup-prompt-banner` は `visible` と `message` の bindable のみで、ユーザーが「あとで」と判断した際にバナーを閉じる手段がなかった。

## Goals / Non-Goals

**Goals:**
- `isCompleted` ゲストへの許可ルートを dashboard / discovery / my-artists に限定する
- 未許可ルートへのアクセス時は現在のルートにとどまり、"login required" toast を表示する
- `bottom-sheet` の `.dismiss-zone` クリックで dismiss が機能するよう修正する
- `isCompleted` ゲストが dashboard で home を選択した際にも localStorage に永続化する
- signup-prompt-banner に × dismiss ボタンを追加する

**Non-Goals:**
- `isCompleted` ゲストに許可するルートセットの拡張（本 change のスコープ外）
- bottom-sheet のアニメーション・スタイル変更
- `popover="auto"` の light-dismiss 動作の変更

## Decisions

### 1. isCompleted ゲストの許可ルート判定

ルートの `data.onboardingStep` が `dashboard`・`discovery`・`my-artists` のいずれかである場合のみ許可する。
`app-shell.ts` の route config で各ルートに設定済みの `onboardingStep` を再利用するため、新たなフラグを追加しない。

```typescript
// Priority 3: Completed onboarding (guest) — allow dashboard / discovery / my-artists only
if (this.onboarding.isCompleted) {
  const allowedSteps: OnboardingStepValue[] = [
    OnboardingStep.DASHBOARD,
    OnboardingStep.DISCOVERY,
    OnboardingStep.MY_ARTISTS,
  ]
  if (routeStep !== undefined && allowedSteps.includes(routeStep)) {
    return true
  }
  // Auth-required routes: stay in place, show toast
  this.ea.publish(new Snack(this.i18n.tr('auth.loginRequired'), 'warning'))
  return false  // ← false でナビゲーションをキャンセル（現在のルートに留まる）
}
```

**代替案:** `data.guestAllowed` フラグを各ルートに追加する
→ ルート設定を変更する必要があり、変更箇所が増える。既存の `onboardingStep` で充分表現できるため不採用。

**代替案:** リダイレクト先を LP でなく `discovery` にする
→ 「どこかに飛ばす」体験自体を避けるべきであるため不採用。

### 2. bottom-sheet の dismiss-zone クリック検出

`event.target !== this.scrollWrapper` を `event.target` が `.sheet-page` 内にあるかの判定に変える。
「sheet-page の外（= backdrop / dismiss-zone）をクリックした場合のみ dismiss する」というセマンティクスが明確になる。

```typescript
if ((event.target as Element).closest('.sheet-page')) return  // sheet-page 内なら無視
// それ以外（dismiss-zone またはスクロールラッパー直接）→ smooth-scroll to dismiss
this.scrollWrapper.scrollTo({ top: 0, behavior: 'smooth' })
```

**代替案:** `event.target.classList.contains('dismiss-zone')` で直接判定
→ dismiss-zone が存在しない場合（`dismissable=false`）の考慮が必要になるため、`closest('.sheet-page')` の否定形の方がシンプル。

### 3. guest/setUserHome dispatch の修正

`onHomeSelected()` 内で `!this.authService.isAuthenticated` を条件に `GuestService.setHome()` を呼び出す。`isOnboarding` の有無に関わらず、未認証ユーザーの home 選択は必ず localStorage に永続化する。

```typescript
public onHomeSelected(code: string): void {
  this.needsRegion = false
  if (!this.authService.isAuthenticated) {
    this.guest.setHome(code)
  }
  this.loadData()
  if (this.isOnboarding) {
    this.startLaneIntro()
  }
}
```

### 4. signup-prompt-banner dismiss ボタン

× ボタンを追加し、クリック時に `banner-dismissed` CustomEvent を dispatch する。親ルートがイベントをキャッチして `showSignupBanner = false` にセットする。

dismiss 状態は session-scoped（ページ離脱で復帰）とし、localStorage への永続化はスコープ外とする。

## Risks / Trade-offs

- **isCompleted ゲストが `tickets` へアクセスした場合の toast**: 現在は `auth.loginRequired` key を使用しているが、"tickets requires login" のような文脈に合わせたメッセージへ変更するかは今後の課題。→ 本 change では `auth.loginRequired` を流用。
- **bottom-sheet の `closest` パフォーマンス**: click イベント毎に `closest()` が走るが、底シートはユーザーインタラクション時のみ open しているため問題なし。
- **banner dismiss の非永続化**: ページ遷移で banner が復帰するが、signup-prompt-banner はコンバージョン目的のため意図的に再表示する設計。ユーザーがうっとうしく感じた場合は将来的に localStorage 永続化を検討。
