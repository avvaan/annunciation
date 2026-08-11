# Design

<!-- impeccable:design-schema 1 -->

## Direction

**Editorial parish** — full-bleed photography, Russian book-printing antiqua, warm parchment ground, one liturgical oxblood accent.

Brief-pinned by the user to the Vestry church reference (Awwwards Honorable Mention, Feb 2022 — documented art direction: big background images, clean flat design, typography-led). The reference site itself is unreachable from the build sandbox (`awwwards.com` and `themeforest.net` are blocked by the egress proxy); the user chose to proceed from its documented direction rather than supply screenshots, and that substitution was disclosed before any code was written.

Replaces the previous **"Табло расписания"** direction (flat ruled departure-board timetable, paper-white/black/rubric-red). That world is now an anti-reference: it is not polished, it is discarded. What survives from it is product truth only — the schedule remains the site's centre of gravity and must stay glanceable on a phone.

Equally refuses the gilt-scrollwork church-template default. There is no gold fill anywhere; brass appears only as hairline ornament, and the single ornamental motif in the entire system is one rule with a centred diamond.

## Color

Strategy: **Committed** — deep umber bands against warm parchment, one reserved accent.

| Token | Value | Use |
|---|---|---|
| `--paper` | `#f3ece0` | page ground |
| `--paper-deep` | `#e9dfcd` | image wells, progress track |
| `--surface` | `#fffdf8` | cards, inputs |
| `--deep` | `#16120f` | dark bands, hero scrim, footer, page heads |
| `--deep-2` | `#241d18` | cards on a dark band |
| `--ink` | `#1c1712` | body text |
| `--ink-2` | `#5d5346` | secondary text |
| `--ink-on-deep` | `#f3ece0` | text on dark |
| `--ink-on-deep-2` | `#bdb1a0` | secondary text on dark |
| `--accent` | `#7a2230` | oxblood — fasting/feast flags, primary action, active language |
| `--accent-deep` | `#5b1622` | accent hover/pressed |
| `--accent-tint` | `#f0e0dc` | accent background pairing |
| `--brass` | `#a5813f` | hairline ornament, link underlines, progress on dark — never a fill |
| `--line` / `--line-deep` | `#d6c9b3` / `#3a2f26` | hairline rules, light and dark ground |
| `--focus` | `#1f5fd0` | focus ring only |

## Type

| Token | Face | Use |
|---|---|---|
| `--font-display` | **Old Standard TT** (400/700 + italic), self-hosted | every heading, hero title, feast titles, dates, timeline years, footer name |
| `--font-body` | **PT Sans** (400/700), self-hosted | body copy, nav, labels, buttons, times |

Old Standard TT is a revival of the late-19th/early-20th-century Russian book typefaces — the typographic world this audience actually reads liturgical and academic books in, and a face outside the model-default display set. PT Sans is Cyrillic-native by design.

Both self-hosted as woff2, Cyrillic + Latin subsets only (5 + 4 files). No Google Fonts CDN: an earlier pass linked it directly and it intermittently stalled page loads through this environment's proxy, against the brief's fast-loading constraint. The 700-weight Cyrillic display face and 400-weight Cyrillic body face are `<link rel=preload>`ed.

Base size 19px, line-height 1.65 — the audience skews elderly. Hero display is `clamp(2rem, 5vw, 3.75rem)`, well under the 6rem ceiling; the parish name is four long Russian words and larger sizes collided with the header.

## Components

- **`.hero`** — full-bleed photograph, `min-height: min(86svh, 46rem)`, bottom-weighted three-stop scrim, content bottom-aligned with 8.5rem (mobile) / 11rem (desktop) top padding so it clears the transparent header. `.hero__media--empty` is the ruled fallback ground when no photograph exists.
- **`.page-head`** — deep umber block for inner pages that carry no photograph.
- **`.service-day`** — the schedule card: Old Standard tabular date, uppercase weekday, italic old-style date, feast title, hairline-divided time rows with a fixed 4.25rem time column, `.fast-flag` when applicable. No colored side rail — the flag itself carries the signal.
- **`.tile`** — image + heading + line; the 3/2 media well scales its image 1.04 on hover.
- **`.doc-list`** — hairline-ruled rows for PDFs, icon + title + period.
- **`.btn`** — wears a drawn letterpress plate as a 9-slice `border-image` (`plate-light.png` / `plate-accent.png`), uppercase tracked label, 48px min height. The plate supplies the printed surface and its impressed inner rule; the label stays live text, so it scales with OS text size, translates between RU and EN, and is read by screen readers. `.btn--light` (on dark grounds) drops the plate for a plain hairline — a parchment plate glares against umber. `button[type=submit]` inherits the accent plate, explicitly excluding `.lang-switch__btn`, whose job is to show the active language rather than look like a primary action.
- **`.ornament`** — the entire ornamental budget: a drawn brass rule with a centred diamond (`divider-light.png`; `divider-dark.png` swaps in on dark bands, since each asset carries its own ground).
- **`.timeline`**, **`.facts`**, **`.rota`**, **`.photo-grid`**, **`.portrait`**, **`.status`**, **`.fund`** — see `static/css/base.css`.
- **Icons** — authored SVG set in `templates/_icons.html`, one 1.5px stroke on a 24×24 grid, sized to the surrounding text. No emoji (the previous build used 🔒 in ministry templates; replaced).
- **Nav** — transparent over a hero (`body.has-hero`), solid otherwise. Checkbox toggle with an always-visible "Меню" text label; the checkbox is a sibling of both the header row and the nav, which the `~` selector requires.

## Layout

Mobile-first. `--wide: 74rem` content shell, `--measure: 38rem` prose. Single breakpoint at `60rem` un-collapses the nav. Sections alternate parchment `.band` and umber `.band--deep` to pace the scroll.

## Motion

One authored moment: the hero title, lede and actions rise 1.25rem out of a 6px blur on an exponential ease-out, staggered 90ms. Nothing else animates on scroll — no per-section entrances, no sliders. Tile images have a 0.6s hover scale. `prefers-reduced-motion` disables the hero entrance and smooth scrolling.

## Browser surfaces

Themed rather than left to the browser: `::selection` (oxblood on parchment), caret color, scrollbar track and thumb (both WebKit and standard properties), focus ring, link underline color and offset, and `font-variant-numeric: tabular-nums` on every date, time, year and money figure.

## Imagery

Six photographs supplied by the parish, resized and re-encoded into `static/images/photos/`:

| File | Subject | Used as |
|---|---|---|
| `hero-gospel.jpg` | Gospel book on brocade, candles beyond | homepage hero |
| `font-candles.jpg` | Baptismal font, three candles, iconostasis | building-project hero, homepage tile |
| `school-eggs.jpg` | Painting Easter eggs with children | Russian-school hero, homepage tile |
| `greenery.jpg` | Hands preparing greenery for a feast | ministries hero and cards |
| `icon-trinity.jpg` | Rublev Trinity icon among flowers | available, not yet placed |
| `parishioners.jpg` | Two parishioners with an analogion | available, not yet placed |

Each is a shipped default that an admin upload overrides (`SiteSettings.hero_image`, `BuildingProject.cover_image`, `RussianSchoolPage.cover_image`, `Ministry.image`), so the site is never empty out of the box and never blocks the secretary from replacing a photo.

A seventh supplied file — an Annunciation icon graphic — was **not** used: it carries another monastery's watermark and burnt-in lettering, so it is third-party branded artwork rather than parish material.

Favicon and OG card are hand-authored assets from the previous pass and are due a refresh into this world.

### Drawn ornament (Higgsfield)

Generated at the user's request in this design's palette, then trimmed, downscaled and palette-quantised into `static/images/ornament/` — 140KB for the whole set, against the brief's loading budget. The Higgsfield CDN is blocked by this session's egress policy, so the user exported them and handed them back as files.

| File | Use |
|---|---|
| `divider-light.png` / `divider-dark.png` | `.ornament` on parchment / on umber |
| `plate-light.png` / `plate-accent.png` | 9-slice button plates |
| `cross.png` | three-bar cross emblem in the footer |
| `border-strip.png` | Byzantine band along the footer's top edge, 1.75rem tall, nowhere else |

Two further generations — a corner interlace flourish and a wheat-and-vine motif — were rendered well but not installed: both are dense enough to read as the gilt-scrollwork the brief rules out, and neither had a place the design actually needed. They remain in the Higgsfield history if a use appears.

## Known gaps / next steps

- `icon-trinity.jpg` and `parishioners.jpg` have no home yet — candidates for the history page and the about page once real captions exist.
- Clergy portraits, exterior shots of the building, and construction-progress photos are still absent; those fields fall back to a drawn placeholder tile.
