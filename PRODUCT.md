# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: Russian-speaking Orthodox parishioners of the Annunciation of the Most Holy Theotokos parish (Jacksonville, FL) — skews older, checking service times on a phone, often on the go before a service. Secondary, explicitly confirmed as not a distinct design audience: none — the user confirmed there is no second audience the design must explicitly account for beyond parishioners.

Two smaller but real user roles use the same site: the parish secretary, who maintains the service schedule and page content from the Django admin without developer help; and ministry leaders/members, who use a login-gated portal (join/leave, discussion, documents, photo/schedule sharing) nested under the public site.

## Product Purpose

A rebuild of the parish's aging website. Central source for: the weekly/monthly service schedule (the highest-traffic page), calendar & bulletin PDFs, a building-fund progress page, a Russian language school page, a parish history page, newsletter sign-up, and a ministries portal — plus outbound links to the parish's external Realm system for membership and giving (no embedded payment flow).

## Positioning

Not a marketing site — a parish operations site. What a generic "church template" could not truthfully copy: a service-schedule view built to be read one-handed on a phone in seconds (new/old calendar style, feast, fasting grade, per-service times, all at a glance, no zoom), and a content model a non-technical secretary can fill in herself in the Django admin every month.

## Operating Context

- Parishioners check service times on a phone, frequently in a hurry or on the go, sometimes on a spotty connection.
- The secretary updates the schedule roughly monthly from the Django admin (schedule entries, calendar/bulletin PDFs, building-fund updates, announcements) — not a developer.
- Ministry leaders and members use a members-only portal (separate from the public marketing pages) for discussion threads, shared documents/reports, photos, and rotas.
- The Russian school section is read by parents arranging enrollment/schedule, not by children.

## Capabilities and Constraints

- Django admin (already built) drives every content type: `ServiceDay`/`ServiceItem` (date, computed old-style date, feast title, per-item time + service-type choice, fasting-level choice), `Publication` (calendar/bulletin PDFs), `BuildingProject` (goal/raised amount, updates, photos), `RussianSchoolPage`, `HistoryMilestone` timeline, `Announcement`, `ClergyMember`, newsletter `Subscriber` (double opt-in), and a full `Ministry` portal (membership roles, projects, topics/comments, documents/reports with visibility tiers, photos, schedule entries, supply requests), a parish-council portal (two access tiers driven by approved membership requests: meetings, minutes, financial reports, tasks, projects, BCC group mailings), and commemoration notes (`Commemoration` submitted from the public site, batched by the secretary into a `CommemorationBatch` that prints as one PDF for the altar).
- Commemoration notes are a public write path, so the submission form carries anti-spam by construction (off-canvas honeypot, a minimum elapsed-time check, per-list name-count and name-length caps) rather than a CAPTCHA an elderly parishioner would struggle with.
- Printed batches and council documents are personal data (names plus the submitter's contact details). They are stored outside `MEDIA_ROOT` in `PRIVATE_MEDIA_ROOT` and are only reachable through a view that checks rights first — never by URL.
- Bilingual: Russian is the default/source language (unprefixed URLs), English is secondary (`/en/...`).
- External Realm system handles membership and donations — the site only link-outs to it (`SiteSettings.realm_giving_url` / `realm_membership_url`), no payment UI to design.
- No heavy carousels/sliders; page weight and load speed are explicit constraints (target: page loads under a second).
- Currently zero real photography exists (clergy, the church building, parishioners, ministry activities) — all such imagery is a placeholder until the parish supplies real photos. AI-generated imagery is reserved for clearly decorative use (ornament, texture, hero backgrounds), never presented as a photo of real people or the actual building.

## Brand Commitments

None. Confirmed with the user: no existing logo, no fixed icon of the Annunciation, no diocesan (OCA) color mandate to preserve — the visual system is being designed from scratch.

## Evidence on Hand

No real content or photography supplied yet beyond the schema above (which is original — the structure was informed by studying the parish's current site and an unrelated donor codebase, but no text or images from either were copied). Future design and content work must not fabricate photos of clergy, the building, or parishioners, and must not invent testimonials, donor names, or dollar figures.

## Product Principles

1. Legibility for older readers outranks decoration — large type, high contrast, no ornamental clutter (explicitly: no gold-swirl kitsch).
2. Mobile-first, and the service-schedule page is the design's center of gravity: glanceable, no pinch-zoom required.
3. Fast over flashy — no heavy sliders, minimal client-side weight.
4. The design must hold up with plain, secretary-entered content (unpolished text, inconsistent photo sizes), not just curated hero copy.
5. Real people/places get real photography only; generated imagery stays legibly decorative and is never presented as documentary.

## Accessibility & Inclusion

Primary audience skews elderly: high contrast, generous base font size, large tap targets, no interactions that depend on hover, and layouts that hold up under OS-level text scaling.
