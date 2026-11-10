# Design tokens, typography, spacing, responsive

> Extracted verbatim from `SPEC.md` (sections 3.1.2-3.1.6). Do not edit here; edit SPEC.md and re-extract.

## 3.1.2 Design tokens table

Token values are the Carbon **g100** values confirmed from the built CSS bundle. Where the application hard-codes a hex, that is stated.

| Token / use | Value | Where used |
|---|---|---|
| `background` (page) | `#161616` | `body` (hard-coded), login gradient base, favicon |
| `text-primary` | `#f4f4f4` | `body` (hard-coded), `.twin-title` |
| `text-secondary` | `#c6c6c6` | `.header-status`, `.page-subtitle`, `.card-help`, `.stat .label`, `.step-source`, `.twin-sub` |
| `layer-01` | `#262626` | `.card`, `.stat`, `.login-card`, `.twin-rect` |
| `border-subtle-01` | `#393939` (Carbon g100) | `.card`, `.stat`, list separators |
| `border-strong-01` | `#6f6f6f` | `.stat` left border, `.twin-rect` stroke, `.twin-flow` |
| `support-success` | `#42be65` | Connected dot, completed icons, `.stat.ok` |
| `support-error` | `#fa4d56` | Failed dot, `.stat.bad` |
| `support-warning` | `#f1c21b` | `.stat.warn`, skipped/cancelled icons, `.log-line.warn .msg` |
| `support-info` | `#4589ff` | `.stat.info`, running icon, active twin node |
| Hard-coded status blue (connecting / running dot) | `#78a9ff` | `AppShell` header dots, `.src-backend`, favicon glyph |
| Not-configured / idle grey | `#8d8d8d` | `AppShell` header dots |
| Log background | `#0b0b0b` | `.log-view`, markdown `pre`, `.progress-lines` |
| Inline-code background | `#262626` | `.markdown code` |
| Log timestamp | `#6f6f6f` | `.log-line .ts` |
| Log source colours | backend `#78a9ff`; headless-bob `#be95ff`; system `#a8a8a8` | `.src-*` |
| Log error message | `#ff8389` | `.log-line.error .msg` |
| Login background | `radial-gradient(circle at 20% 10%, #1c2a44 0%, #161616 55%)` | `.login-shell` |

## 3.1.3 Typography

| Role | Font | Detail |
|---|---|---|
| Body / UI | IBM Plex Sans (Plex stack) | via `@ibm/plex-sans` default CSS |
| Code, logs, `pre`, `.mono` | IBM Plex Mono | `.log-view` 0.75 rem, line-height 1.5 |
| `.page-title` | Carbon `heading-05` | margin-bottom `$spacing-02` |
| `.page-subtitle` | Carbon `body-compact-01`, secondary colour | max-width 60 rem, margin-bottom `$spacing-07` |
| `.card-title` | Carbon `heading-03` | flex, gap `$spacing-03`, margin-bottom `$spacing-03` |
| `.card-help` | Carbon `helper-text-01`, secondary | margin-bottom `$spacing-05` |
| `.stat .label` | Carbon `label-01`, uppercase, letter-spacing 0.32 px | secondary colour |
| `.stat .value` | Carbon `heading-03` | margin-top `$spacing-02` |
| Markdown body | Carbon `body-02`, max-width 62 rem | h1 `heading-05`, h2 `heading-04`, h3 `heading-03` |
| Twin text | system SVG text | title 12 px / 600, sub and src 10 px, state 11 px |

## 3.1.4 Known token caveat

`GlobalTheme` only supplies React context. It does **not** add the `.cds--g100` class to the DOM, so `--cds-*` custom properties are **undefined** in the running page. Consequences:

- HTML surfaces survive because `body` hard-codes `#161616` / `#f4f4f4`, and Carbon component CSS carries its own resolved fallbacks.
- Custom rules that read `var(--cds-*)` (for example `.card { background: var(--cds-layer-01) }`, the success icon fill `var(--cds-support-success)` in `OverviewPage` and `WorkspacePage`) may resolve to the property's initial value.
- SVG is more sensitive than HTML (undefined fill falls back to black, undefined stroke to none). This blanked the first version of the digital twin.
- The twin therefore defines its own `--twin-*` variables with literal g100 values (see [3.4](#34-pipeline-digital-twin)).

A re-implementation must either apply the `cds--g100` class to `<html>` or `<body>`, or keep the literal values above. Status: **Partial** (observation recorded; application source intentionally not changed by this document).

## 3.1.5 Spacing and layout

| Item | Value |
|---|---|
| Carbon spacing scale | `$spacing-02` … `$spacing-07` (0.25 rem … 3 rem) |
| `.app-main` | padding `$spacing-07`; `min-height: calc(100vh - 3rem)`; `max-width: 1584px`; `margin: 0 auto` |
| `.section` | margin-bottom `$spacing-07` |
| `.card` | background layer-01, 1 px `border-subtle-01`, padding `$spacing-06`; `.card + .card` margin-top `$spacing-05` |
| `.grid-2` | `grid-template-columns: repeat(auto-fit, minmax(min(100%, 28rem), 1fr))`, gap `$spacing-05` |
| `.grid-4` | `repeat(auto-fit, minmax(min(100%, 14rem), 1fr))`, gap `$spacing-05` |
| `.kv` | grid `minmax(8rem, 12rem) 1fr`, gap `$spacing-03 $spacing-05`; `dt` secondary, `dd` wraps anywhere |
| `.stat` | layer-01, border-subtle, left border 3 px `border-strong-01` (variants: ok/bad/warn/info set the colour), padding `$spacing-05` |
| `.actions` | flex wrap, gap `$spacing-03`, margin-top `$spacing-06` |
| `.form-stack > * + *` | margin-top `$spacing-05` |
| `.row` | flex, gap `$spacing-04`, align centre, wrap |
| `.step-list li` | grid `1.5rem 1fr auto`, gap `$spacing-04`, padding `$spacing-04 0`, bottom border-subtle |
| `.log-view` | height 26 rem, scroll, padding `$spacing-04`, border-subtle |
| `.log-line` | grid `5.5rem 6.5rem 1fr`, gap `$spacing-03`, `pre-wrap` |
| `.prompt-area textarea` | min-height 14 rem, IBM Plex Sans |
| `.progress-lines` | max-height 10 rem, mono 0.75 rem, background `#0b0b0b` |
| `.login-card` | width `min(100%, 26rem)`, padding `$spacing-07`, layer-01 |

## 3.1.6 Responsive behaviour

| Breakpoint | Behaviour |
|---|---|
| `max-width: 1056px` | `.hide-md` hidden (the header repository and QSE chips) |
| `max-width: 672px` | `.header-status` hidden entirely; `.app-main` padding `$spacing-05`; `.kv` collapses to one column |
| Always | `grid-2`/`grid-4` auto-fit; twin SVG has `min-width: 1000px` and scrolls horizontally inside `.twin { overflow-x: auto }` |
| Side nav | fixed, expanded, 16 rem wide at all widths (`Content` has `margin-left: 16rem`). There is no collapse or hamburger behaviour. |
