# Design

<!-- impeccable:design-schema 1 -->

## Direction

**Parish typography, not a template** — full-bleed photography, deep-blue devotional bands ruled top and bottom with a lighter blue hairline, cream and white alternating underneath, air instead of frames. Ornament is typographic only: serif numerals on cards and a 54×2 accent divider under each section heading.

Built to a **design handoff supplied by the parish** (`design_handoff_annunciation`): four HTML reference screens (home, schedule, trebas, commemoration notes) plus the Saint Nina Orthodox design system they are built on, with the system's palette overridden to blue. The handoff states its own fidelity as high — "цвета, типографика, отступы и состояния окончательные" — and asks for the mockups to be reproduced inside the existing Django templates rather than copied as HTML. That is what this pass does.

Replaces the previous **fse-church** direction (floating rounded nav pill, rounded photo cards with gradient captions, gold pill buttons, shadows everywhere). That world is now an anti-reference: the shape language inverted from rounded-and-shadowed to hairline-and-flat, and the gold accent is gone entirely. What survives is product truth only — the schedule is still the site's centre of gravity and still glanceable on a phone, and the members-only portal stays in its own denser working register.

Two departures from the handoff, both forced, both marked at the point of use in `base.css`:

1. **Type families.** The handoff specifies Libre Baskerville + Work Sans. Both ship Latin and Latin-Ext only — no Cyrillic — so on a Russian-first parish site every heading and paragraph would fall back mid-page. Lora and Inter stand in (see Type).
2. **Body size.** The handoff sets `--fs-body: 0.96rem` (15.4px). This build previously ran 19px with a written note that the audience skews elderly; 15.4px would silently reverse that decision. It lands at 17px — the handoff's density, most of the legibility. Everything stays in rem, so browser zoom scales all of it (verified: no horizontal overflow at 200%).

## Color

Strategy: **Committed** — one blue family on cream and white. No second colour.

The handoff's blue override, taken verbatim, with one correction. The design system carries historical `--gold*` token names holding blue values; here they are named for what they are.

**The correction.** The handoff uses its accent `#5b8fc0` for eyebrows and small uppercase labels. Measured, that is 3.42:1 on white, 3.09:1 on cream and 3.52:1 on the dark band — under the 4.5:1 floor for text on all three grounds. The accent is kept for what it *does* clear (3:1 non-text graphics) and split from two text-safe siblings.

| Token | Value | Use |
|---|---|---|
| `--deep` | `#15375f` | devotional bands, page heads, footer rules |
| `--deep-2` | `#1d4470` | headings, primary button, footer emblem |
| `--mid` | `#3573a6` | button gradient end — darkened off the handoff's `#3a7fb5`, which put white button text at 4.30:1 |
| `--accent` | `#5b8fc0` | **non-text only**: 3px band rules, 2px header rule, dividers, card top-rules, borders |
| `--accent-deep` | `#2a6f9e` | text-safe accent on light: links, eyebrows (5.43:1 white / 4.90:1 cream) |
| `--accent-bright` | `#3b88bb` | link and button hover |
| `--accent-on-deep` | `#8fb6dd` | text-safe accent on dark: eyebrows on bands (5.68:1 on `--deep`, 4.69:1 on `--deep-2`) |
| `--accent-tint` | `#e6f0f9` | tinted fill, selected radio pill |
| `--surface` / `--paper` / `--paper-deep` | `#ffffff` / `#eef4fa` / `#e3edf7` | white and cream alternating grounds; wells and progress tracks |
| `--ink` / `--ink-2` | `#444444` / `#666666` | body, secondary (9.74:1 / 5.74:1 on white) |
| `--ink-on-deep` / `--ink-on-deep-2` | `#ffffff` / `#b9c9dc` | text on dark |
| `--line` / `--line-deep` | `#cfe0ef` / `rgba(91,143,192,.26)` | hairlines, light and dark ground |
| `--footer-bg` | `#16283a` | footer |
| `--focus` | `#3d8bff` | focus ring only |

Contrast was verified two ways, not one: a scripted WCAG pass over every token pairing, then an **automated audit that walks every rendered text node on ten pages**, resolves its effective background through the ancestor chain, and flags anything under 4.5:1 (3:1 for large text). Zero failures.

Text over photography can't be checked that way — the scrim is a sibling pseudo-element, not an ancestor — so it was measured from the rendered pixels instead, with the text hidden. Worst case (brightest 5% of the background behind the text):

| Surface | brightest 5% of background |
|---|---|
| homepage hero | 5.02:1 |
| "Строим храм" band | 8.09:1 |
| trebas page head | 8.37:1 |
| "Впервые здесь" hero | 5.13:1 |

Two places where the handoff's own choice was overridden on contrast grounds, both noted in `base.css`:

- **Primary buttons on dark grounds.** The mockups put a blue-gradient button on the blue band, where the fill barely separates from its background. On `.band--deep` and `.photo-band` the primary button is white with navy text instead.
- **Forms on dark grounds.** Labels, legends and help text take colours tuned for a white sheet; on the "Впервые здесь" enquiry form they were invisible. They flip to white/accent-on-deep inside `.band--deep`.

## Shape

Restrained, per the design system — the previous direction's roundedness is gone.

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | `4px` | buttons, inputs |
| `--radius-md` | `6px` | cards, side cards, announcement |
| `--radius-lg` | `8px` | — |
| `--radius-pill` | `100px` | radio pills, status chips, progress track |
| `--shadow-sm/md/lg` | navy-tinted `rgba(28,38,71,…)` | resting card / hover / feature photo |
| `--section` | `5.625rem` (90px) | the vertical rhythm between sections |
| `--shell` / `--shell-wide` | `1140px` / `1440px` | content measure / header bar |

## Type

| Token | Face | Use |
|---|---|---|
| `--font-display` | **Lora** (400/500/600/700 + italic), self-hosted | headings, hero title, feast titles, dates, numerals, italic leads |
| `--font-body` | **Inter** (400/500/600/700), self-hosted | body, nav, eyebrows, labels, buttons, times |

Standing in for Libre Baskerville and Work Sans, which have no Cyrillic (see Direction). Lora is itself a Cyrillic-native transitional book serif (Cyreal), so the display register survives the substitution; Inter is a Cyrillic-native humanist sans at the same weights. Both self-hosted as woff2, Cyrillic + Latin subsets, no CDN at runtime; the 700 display and 400 body Cyrillic faces are preloaded.

Body 17px / line-height 1.75. Eyebrows are 0.72rem, 600, `letter-spacing: .2em`, uppercase. Display sizes (`--fs-hero`, `--fs-2xl`, `--fs-3xl`) are `clamp()`ed so long Cyrillic headings don't break mid-word on narrow phones.

## Components

- **`.site-header`** — sticky, white, 2px accent bottom rule, 1440px bar. Two-line wordmark left, six uppercase nav items right, donate button pinned. Nothing collapses on scroll. Under 60rem it becomes a checkbox-toggled disclosure; the donate button moves inside it so exactly one is ever visible.
- **`.hero`** — 78vh full-bleed photograph under a **neutral** scrim (`rgba(0,0,0,…)` at three stops and nothing else). The absence of a colour layer is called out in the handoff as the client's own requirement, so it is honoured literally.
- **`.rhythm`** — the standing week, immediately under the hero: `Вс 09:00 / ЛИТУРГИЯ`. Cells come from `RecurringServiceRule`, the weekly template the secretary already fills in. Each cell shows the day's **principal** service — the last item, since a service day builds toward it (Часы before Литургия, Вечерня before Утреня); the first by time would show "Часы" on Sunday. The fourth cell is the founding year and appears only if `SiteSettings.founded_year` is set: it can't be invented, and without it the bar simply shows three cells.
- **`.band--deep`** — the devotional band: `120deg` navy gradient ruled top and bottom with the 3px accent. Carries the upcoming-services list and the announcement card on the home page, and the closing call to action on trebas.
- **`.feature`** — the numeral card, in light and dark variants. The numeral *is* the ornament; there are no icons on the public pages. Roman I–III for "чем церковь живёт", Arabic 01–06 for "за чем к нам приходят".
- **`.split`** — the about block: photograph left with the offset 120×120 accent square, words right.
- **`.sched`** — schedule page: sticky 320px sidebar (next service, fasting legend, PDF link) beside month-grouped rows of `date / feast + tags / times`. The times column is 220px, not the handoff's 190px — Russian service names ("Всенощное бдение") wrapped to two lines on every row at 190px.
- **`.treba-row`** — one row per rite, name left, description right, hairline between. Seven rites as rows rather than cards because the description *is* the content and a card would have to truncate it.
- **`.radio-group`** — the "вид поминовения" pills. Rendered from whatever choices the Django form carries, so adding a kind is a model change, not a template change. Django 5 renders `RadioSelect` as `div > div > label > input`, so the option wrapper is addressed by position, not tag.
- **Portal (`portal.css`)** — untouched structurally; the handoff covers the public side only. Its filled elements followed the palette off gold: fill-plus-dark-text held 5.65:1 while the fill was gold and drops to 3.11:1 on blue, so buttons, the overdue tag and the done-checkbox are now white on navy.
- **Icons** — authored SVG set in `templates/_icons.html`, used in chrome only (menu, cross, arrow, document). No emoji.

## Layout

`--shell: 1140px` content, `1440px` header bar, `--section: 90px` rhythm. Breakpoints at 74rem (4-up grids → 2-up), 60rem (two-column grids → one, nav → burger, sticky sidebars → static, section rhythm → 60px) and 40rem (card grids → 1-up, stats bar → 2-up). Verified: no horizontal overflow at 360px or at 200% zoom on any redesigned page.

## Motion

Quiet, per the design system: buttons lift 2px, cards 5px, tile images scale 1.04, all over 0.2–0.3s ease. Nothing spins or springs. `prefers-reduced-motion` disables all of it.

## Imagery

Five photographs came with the handoff. Three of them are **byte-identical to photographs already in the repository** (perceptual diff 0.03–0.08 per channel against `hero-gospel`, `font-candles`, `icon-trinity`) — the designer had taken them from the repo — so they are reused rather than duplicated. One is genuinely new; one 16MB spare is unused.

| File | Subject | Used as |
|---|---|---|
| `font-candles.jpg` | Baptismal font, candles, iconostasis | homepage hero |
| `icon-trinity.jpg` | Rublev Trinity icon among flowers | "Строим храм" band |
| `hero-gospel.jpg` | Gospel book on brocade | trebas page head |
| `liturgy-candle.jpg` | **new** — clergy at the analogion | homepage about block |
| `school-eggs.jpg` / `greenery.jpg` / `parishioners.jpg` | as before | school, ministries |

Each is a shipped default an admin upload overrides, so the site is never empty out of the box. All are served at 480/960/1600 via `{% parish_photo %}`.

## Coverage against the brief

Every section the original brief named still exists and is still admin-fillable: schedule, calendar & bulletin, building project, Russian school, parish history, first visit, clergy, newsletter, donations, trebas, commemoration notes, and the ministries + council portals. The only model change in this pass is one optional field (`SiteSettings.founded_year`); views changed only to pass the two new card lists.

The header nav is six items, as the mockups show — three fewer than before. The pages that lost their nav entry (calendar, Russian school, building, clergy, contact) are all reachable from the footer's "Быстрые ссылки" column, which is the reason that column exists.

## Known gaps / next steps

- `family-prayer-*.webp`, added one pass earlier for the trebas intro, has no slot in the new layout — the trebas page now opens with a photographic head instead. Files kept, not deleted.
- `candles-easter.jpg` from the handoff (16MB, 4000×6000) is unused; it was supplied as a spare.
- The hero scrim is fixed by the handoff. It measures 5.02:1 against the current photograph; a much brighter uploaded hero could push white text under 4.5:1. Worth re-measuring if the parish changes the photo.
- The commemoration form still offers two kinds (Обедня, Сорокоуст) — the mockup drew four pills, adding Молебен and Панихида, but the handoff also says to wire the *existing* form, and those two are trebas rather than proskomedia commemorations. Left as a question for the parish.
- `favicon.svg` / `og-image.png` are untouched by this pass.
- Clergy portraits and construction photos are still absent; those fields fall back to a drawn placeholder tile.
