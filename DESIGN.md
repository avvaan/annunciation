# Design

<!-- impeccable:design-schema 1 -->

## Direction

**Табло расписания** — Soviet/Russian departure-board information design. Chosen over two alternates (narthex bulletin board, menaion wall-calendar grid) and the standing "generic church site" convention; picked specifically because the schedule page is the site's center of gravity and this world makes the schedule read like an object the audience already trusts at a glance.

Refuses the AI-cliché "church site" default (cream/parchment ground, italic serif display, gold accent, ornamental card borders). Ground is true paper-white/near-white, never cream; accent is a single reserved liturgical rubric red, never gold; cards are flat and ruled, never soft/shadowed/rounded.

## Color

Strategy: **Committed** — one reserved accent, used only where it means something.

| Token | Value | Use |
|---|---|---|
| `--color-bg` | `#f7f7f5` | page ground |
| `--color-surface` | `#ffffff` | cards, inputs |
| `--color-ink` | `#17181a` | body text, primary borders |
| `--color-ink-soft` | `#47494d` | secondary text (old-style date, meta) |
| `--color-line` | `#c9cacc` | hairline dividers |
| `--color-line-strong` | `#17181a` | structural borders (header rule, card border, buttons) |
| `--color-red` | `#ac2b1e` | liturgical rubric red — fasting/feast flags, primary CTA, active nav/lang state only |
| `--color-red-soft` | `#f4e3e0` | red's background pairing (tag fill, success message) |
| `--color-focus` | `#1457c9` | focus ring only |

Rule: red never decorates. It fires on a fasting/feast day, a primary action (Пожертвовать, submit buttons), or an active state (current language). A `.service-day` card is otherwise black-on-white; only `.service-day--fasting` gets the red left rail — the accent is conditional, not a card default (an earlier pass gave every card a colored left rail regardless of meaning; the mechanical detector flagged it as the generic "side-tab" AI tell, and it was removed from the default `.card`/`.board-row` rule for exactly that reason).

## Type

| Token | Stack | Use |
|---|---|---|
| `--font-body` | system-ui stack | body copy — zero webfont cost, matches Operate/Read guidance |
| `--font-display` | "PT Sans" (400/700), self-hosted | headings, nav, labels, buttons — Cyrillic-native grotesk |
| `--font-board` | "Martian Mono" (variable 400–700), self-hosted | every date/time numeral, service-item rows — geometric/constructivist, evokes split-flap and technical signage |

Base size 18px (`--fs-base`), line-height 1.6, for the older-skewing audience. Both display faces are self-hosted as static woff2 files under `/static/fonts/` (cyrillic + latin subsets only, 6 files, ~185KB total) rather than loaded from the Google Fonts CDN — an earlier pass linked the CDN directly and it intermittently stalled full page loads through this environment's proxy during QA, which directly conflicts with the brief's fast-loading requirement. Self-hosting removes that dependency entirely.

## Components

- **`.card` / `.board-row`** — flat white surface, 1px `--color-line` border, no shadow, no default accent border.
- **`.service-day`** — the schedule card: Martian Mono date/weekday header, old-style date in soft ink, feast title in PT Sans bold, `.service-day__items` as dashed-divided rows (time + service type + optional note), `.service-day__fasting` tag when applicable. `.service-day--fasting` adds the red left rail.
- **`.tag`** — bordered inline label (publication period, status); `.tag--accent` for the red variant.
- **`.btn`** — flat, 2px bordered, min 48px tap target; `.btn--accent` (red fill, primary action), `.btn--outline` (transparent).
- **Forms** — all inputs/labels/buttons inherit the same border-and-fill language as `.btn`; no separate form skin.
- **`.timeline`** — left-rail spine (structural connector for the history page, not a decorative card accent — kept despite the detector flagging the same border-left pattern, because it serves the standard "connecting rail" role of a timeline component rather than sitting on a card).
- **Nav** — sticky header, always-visible "Меню" text-label toggle (never icon-only) driven by a checkbox sibling of both the header row and the nav (a same-parent requirement — an earlier structure nested the checkbox inside the header row, which silently broke the `~` sibling selector and made the menu inert; fixed and re-verified by actually clicking the rendered label, not just visual inspection).
- **Language switch** — `RU`/`EN` buttons in the nav, POST to Django's `set_language`, active language gets ink-filled state.

## Layout

Mobile-first; `max-width: 62rem` content column; single breakpoint at `56rem` un-collapses the nav from the toggle menu to an inline bar. Homepage's first viewport is the next-3-services board itself (not a photo hero) — the schedule is proven in the first screenful, not described.

## Motion

None beyond a 0.2s fade-in on card mount (`prefers-reduced-motion` respected) and default browser focus/hover transitions. No sliders, no scroll-triggered choreography — matches the brief's "no heavy sliders" constraint directly.

## Known gaps / next steps

- Real photography (clergy, building, parishioners, ministry activity) is entirely absent — every image field is empty until the parish supplies real photos (see PRODUCT.md § Evidence on Hand). Decorative-only imagery is scoped for a later pass (Higgsfield prompts) and must never stand in for documentary photos.
- Currency formatting on the building-project page (`187500,00 $`) is Django's raw locale-aware decimal rendering, not yet dressed up with thousands separators — cosmetic, not structural.
- `ClergyMember`/testimonial-style content has no seeded example to verify long-bio layout; revisit once real content exists.
