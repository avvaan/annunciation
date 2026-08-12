# Design

<!-- impeccable:design-schema 1 -->

## Direction

**Parish commons** — the donor's own device, taken literally: a floating rounded white nav pill over a rounded-corner photo hero, gradient-caption photo cards, gold pill buttons, everywhere rounded and soft-shadowed rather than hairline and flat.

Donor-pinned by the user to a WordPress theme, **fse-church** ("Church WP Theme" v1.3.9, `screenshot.png` studied directly — reachable, unlike the previous direction's reference). The user chose to take the theme's shape language *literally* (not just as inspiration) and its "green" style variation's palette (deep forest-green `#4A734C` + gold `#D4A017` + cream, closest of its six variants to a liturgical register) over its default teal/amber. Copy, stock photography and lorem-ipsum content were **not** copied — only the visual system: color, shape, type pairing, card and hero composition.

Replaces the previous **"editorial parish"** direction (full-bleed photography, Old Standard TT antiqua, umber/parchment/oxblood, no rounded corners, no shadows). That world is now an anti-reference. What survives from it is product truth only: the service schedule remains the site's centre of gravity and must stay glanceable on a phone; the members-only portal (ministries + council) stays in its own plainer, denser working register rather than adopting the public site's persuasive one — though the user did ask for the portal to be "dressed up" in the same rounded/palette language, unlike the previous direction which kept it deliberately flat.

Still refuses the gilt-scrollwork church-template default in spirit: the donor's own gold is used structurally (fills, buttons, borders) rather than as applied ornament, and no ornamental motif was invented from nothing — the one decorative element left in the system is a plain CSS-drawn rule with a centred gold dot.

## Color

Strategy: **Committed** — deep forest-green bands against warm cream, one gold accent.

| Token | Value | Use |
|---|---|---|
| `--paper` | `#fbf6ed` | page ground |
| `--paper-deep` | `#f1e7d2` | image wells, progress track, placeholder tiles |
| `--surface` | `#ffffff` | cards, inputs, the floating nav pill |
| `--deep` | `#1f3419` | dark bands, page-head fallback, footer |
| `--deep-2` | `#2b4623` | cards sitting on a dark band |
| `--mid` | `#4a734c` | hero's empty-state gradient only (body text on it falls under 4.5:1, so it never carries paragraph copy) |
| `--ink` | `#1c2418` | body text |
| `--ink-2` | `#5b6754` | secondary text |
| `--ink-on-deep` | `#fbf6ed` | text on dark |
| `--ink-on-deep-2` | `#c3d0bb` | secondary text on dark |
| `--accent` | `#b8860f` | text-safe gold — underlines, borders, non-text UI |
| `--accent-bright` | `#d4a017` | the donor's own gold — button/tag fills, paired with dark text, never with white text (2.4–3.3:1, short of 4.5:1) |
| `--accent-deep` | `#7d5c0a` | gold text on cream or on `--accent-tint` (5.2–5.7:1) |
| `--accent-tint` | `#f8ecc9` | accent background pairing, major-feast card fill |
| `--line` / `--line-deep` | `#e4d9c1` / `#3c5934` | hairline rules, light and dark ground |
| `--focus` | `#1f5fd0` | focus ring only |

Every fill/text pairing was checked against WCAG: body text ≥4.5:1, non-text UI (borders, checkmarks) ≥3:1. The one trap in this palette is `--accent-bright` (the donor's vivid gold) read as white text — it doesn't clear 4.5:1 at any weight tested, so every solid gold button/tag in both `base.css` and `portal.css` pairs it with `--deep` text instead, the same way the donor's own screenshot shows dark text on its amber buttons.

## Shape

New to this direction — the donor's signature is roundedness, not hairlines:

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | `0.75rem` | inputs, small chips, checkboxes |
| `--radius-md` | `1.25rem` | cards, tiles, panels |
| `--radius-lg` | `1.75rem` | hero, page-head, the nav pill |
| `--radius-pill` | `999px` | buttons, tags, the language switch |
| `--shadow-sm` / `--shadow-md` / `--shadow-lg` | — | card lift, nav pill, hero/page-head |
| `--edge` | `0.875rem` (mobile) / `1.5rem` (≥60rem) | the gutter every floating card is inset by |

## Type

| Token | Face | Use |
|---|---|---|
| `--font-display` | **Lora** (400/500/600/700 + italic), self-hosted | every heading, hero title, feast titles, dates, timeline years, footer name |
| `--font-body` | **Inter** (400/500/600/700), self-hosted | body copy, nav, labels, buttons, times |

The donor specifies Hedvig Letters Serif for display and Inter for body. Hedvig ships **Latin-only glyphs** (verified with `fontTools`: 0 of 66 tested Cyrillic characters present) and cannot carry a Russian-first site, so Lora stands in as the closest obtainable face — itself a Cyrillic-native book serif (designed by Cyreal), keeping the same warm, moderate-contrast register without a missing-glyph fallback. Inter is the donor's own face and is Cyrillic-native by design, so it carries over unchanged.

Both self-hosted as woff2, Cyrillic + Latin subsets only (10 + 8 files, fetched once from Google's own subset endpoint rather than linked live — no Google Fonts CDN at runtime, consistent with the previous direction's fast-loading constraint). The 700-weight Cyrillic display face and 400-weight Cyrillic body face are `<link rel=preload>`ed.

Base size 19px, line-height 1.65 — unchanged, the audience still skews elderly. `--fs-hero` and now also `--fs-3xl` (the `h1` size) are `clamp()`ed rather than fixed: a fixed 52px `h1` combined with `overflow-wrap: anywhere` was splitting long Cyrillic titles like "Расписание богослужений" mid-word on narrow phones instead of at a word boundary — caught in finish review and fixed by clamping `--fs-3xl` the same way the hero title already was.

## Components

- **`.site-header__bar`** — the one floating card: white, `--radius-lg`, `--shadow-md`, inset by `--edge` from the viewport on every page (hero, page-head, or plain). Absolutely positioned over a hero or page-head; static at the top of plain pages. The mobile-toggle checkbox sits *outside* this card so `:checked ~ .site-header__bar .site-nav` (a sibling combinator into a descendant) can still open it — documented in `base.css` since it's easy to break by nesting the checkbox back inside.
- **`.hero`** / **`.page-head`** — both a rounded, inset, shadowed card (`margin: var(--edge)`, `--radius-lg`) rather than full-bleed; the donor's photo is presented as an object on the page, not the page itself. `.page-head` is bottom-anchored (`display:flex; align-items:flex-end`) with generous top padding, not just enough to clear the nav bar's *typical* height — the bar's actual height varies with how many lines the parish name wraps to, and a page-head sized to the typical case clipped under the bar on the day it wrapped a line taller.
- **`.tile`** — the donor's signature card: photo, `--radius-md`, dark gradient scrim, caption (heading + line) printed directly onto the photo's bottom edge inside `.tile__media`, not set below it as plain text.
- **`.sday`** (schedule card) — same information hierarchy as before (weekday leads, date is secondary, fasting flag in the header, per-item times in a fixed column), now a white rounded card with a soft shadow; a major feast gets the `--accent-tint` fill instead of a second border color.
- **`.btn`** — a solid rounded pill, not a drawn plate: `--surface` + `--line` border by default, `--accent-bright` fill + `--deep` text for the primary action, an outline-only `--light` variant for dark grounds. Buttons lift 1px with a stronger shadow on hover/focus rather than just darkening.
- **`.ornament`** — the entire ornamental budget, now three lines of CSS instead of an image: a hairline with a centred `0.4rem` gold dot. The previous direction's brass-drawn divider/plate/cross/border-strip PNGs (`static/images/ornament/`) are removed — none of them fit a world with no drawn ornament left to reskin, and the footer cross is now `_icons.html`'s existing authored SVG (`icon="cross"`) colored via `currentColor` instead of a raster asset baked to the old dark-umber ground.
- **`.pnav` / `.pbtn` / `.tag` / `.ppanel` / `.pempty` / `.pcheck`** (portal, `portal.css`) — reskinned into the same rounded/gold language (pill buttons and tags, rounded panels, a floating rounded nav bar) while keeping the portal's own fixed type scale, row-based lists instead of cards, and flat information density — the user asked for the portal "dressed up" to match, not converted into marketing UI. The `.pcheck` (task done-checkbox) draws its checkmark in `--deep`, not white, since white-on-gold fails the 3:1 floor for UI graphics at this token's lightness.
- **Icons** — unchanged: authored SVG set in `templates/_icons.html`, one 1.5px stroke on a 24×24 grid. No emoji.

## Layout

Mobile-first, unchanged structurally. `--wide: 74rem` content shell, `--measure: 38rem` prose. Single breakpoint at `60rem`. What changed is that every section-level surface (`band--deep`, `.hero`, `.page-head`, `.site-footer`) is now inset by `--edge` and rounded rather than running edge-to-edge, so the cream page ground is always visible as a margin around every dark block — the donor's floating-card composition applied at every scale, not just the hero.

## Motion

Unchanged: one authored moment (hero title/lede/actions rise 1.25rem out of a 6px blur, staggered), tile images scale 1.04 on hover, `prefers-reduced-motion` disables both. Buttons gained a small translateY+shadow lift on hover, consistent with the rest of this direction's soft-shadow language.

## Browser surfaces

Re-themed to the new palette rather than left over from the previous one: `::selection` (gold-bright on deep-green text), caret color, scrollbar track/thumb (now pill-radius'd), focus ring, link underline color, `font-variant-numeric: tabular-nums` on every date/time/year/money figure — all unchanged in mechanism, just repointed at the new tokens.

## Imagery

The same six parish photographs carry over unchanged (`static/images/photos/`) — nothing about the donor swap required new photography, and the brief's rule still holds: real people/places get real photography only, generated imagery stays decorative.

| File | Subject | Used as |
|---|---|---|
| `hero-gospel.jpg` | Gospel book on brocade, candles beyond | homepage hero |
| `font-candles.jpg` | Baptismal font, three candles, iconostasis | building-project hero, homepage tile |
| `school-eggs.jpg` | Painting Easter eggs with children | Russian-school hero, homepage tile |
| `greenery.jpg` | Hands preparing greenery for a feast | ministries hero and cards |
| `icon-trinity.jpg` | Rublev Trinity icon among flowers | available, not yet placed |
| `parishioners.jpg` | Two parishioners with an analogion | available, not yet placed |

Each is a shipped default that an admin upload overrides, so the site is never empty out of the box.

The previous direction's drawn brass ornament set (`divider-light/dark.png`, `plate-light/accent.png`, `cross.png`, `border-strip.png` — six Higgsfield-generated PNGs, ~132KB) is deleted: none of it belongs to a world with no drawn ornament, buttons that are solid pills rather than 9-slice plates, and a footer cross that's now an inline SVG. `favicon.svg` and `og-image.png` were left as-is (plain black-on-white, doesn't clash) rather than regenerated — a candidate for a future pass, not done here.

## Coverage against the brief

Unchanged from the previous pass — every section the original brief named exists and is admin-fillable: schedule, calendar & bulletin, building project, Russian school, parish history, first visit, clergy, newsletter sign-up, donations, and the ministries + council portals. This pass was a visual system replacement, not a content-model change; every model, view and URL is untouched.

## Known gaps / next steps

- `icon-trinity.jpg` and `parishioners.jpg` still have no home.
- Clergy portraits, exterior/construction photos are still absent; those fields fall back to a drawn placeholder tile.
- `favicon.svg` / `og-image.png` are functional but untouched by this palette swap — worth a refresh into gold-on-green if another design pass happens.
