# Observability Run Project API

Base URL: `/api`. JSON errors use `{ "error": { "code": 400, "detail": ... } }`.

## Public endpoints

- `GET /health/` → `{ "status": "ok" }`.
- `POST /token/` with `{ "email", "password" }` → `{ "access", "refresh" }`.
- `POST /token/refresh/` with `{ "refresh" }` → a new access token.

This backend ships no domain endpoints of its own beyond authentication and health: the site's own resources are built during implementation. New list endpoints should return the same paginated envelope the shared pagination class produces, `{ "count": number, "next": string|null, "previous": string|null, "results": [...] }`, and detail endpoints one object.

## Content and SEO endpoints (public)

Every content endpoint takes `?language=fa|en` (default `fa`).

- `GET /content/home/` → `{ language, site, services[], brands[], articles[], faqs[] }`. `site` is the per-language identity (`site_title`, `tagline`, `hero_title`, `hero_subtitle`, `meta_description`, `og_image`, `phone`, `whatsapp`, `email`, `address`, `city`, `org_name`, `opening_hours_text`); `faqs` are the FAQs marked "show on homepage".
- `GET /services/`, `/brands/?category=`, `/articles/?search=` → paginated lists. Every item carries `seo: { title, description, canonical_url, og_image, no_index, schema_type, image_alt }`; articles also carry `reading_minutes`. Articles whose publish date is in the future are hidden everywhere (scheduled).
- `GET /services/<slug>/`, `/brands/<slug>/`, `/articles/<slug>/` → one record plus `body_html` (brands: `content_html`), `toc: [{ id, text, level }]` and `faqs: [{ question, answer }]`. `body_html` is sanitized HTML from the admin's visual editor, safe to render as-is; every h2/h3 has the `id` its `toc` entry links to. The raw `body`/`content` is still returned.
- `GET /seo/settings/` → `{ language, site, global, pages }`: `global` is the SEO settings singleton (title separator, default share image, organisation/LocalBusiness schema fields, `same_as[]`, `verification: { google, bing, yandex }`, `gtm_id`, `ga4_id`, `discourage_search_engines`); `pages` maps `home|services|brands|articles|about|contact` to `{ title, description, intro, og_image, no_index }`.
- `GET /seo/sitemap/` → `{ language, results: [{ route, slug, updated_at, no_index }] }`, already filtered to indexable pages.
- `GET /seo/redirects/` → `{ results: [{ old_path, new_path, status_code }] }`, every active redirect, unpaginated. `status_code` 410 has an empty `new_path`.
- `GET /seo/robots/` → `{ content }`, the robots.txt body without its Sitemap line.
- `POST /seo/not-found/` with `{ path, referrer? }` and header `X-Seo-Token: <SEO_INGEST_TOKEN>` → `204`; records a 404 in the admin's 404 monitor. `403` without the token (allowed tokenless only while `DEBUG`). Called by the frontend server, never by browsers.

## Authenticated customer endpoints

Send `Authorization: Bearer <access>`.

- `POST /users/register/` (public) with `{ "email", "username", "password", "mobile?", "first_name?", "last_name?" }`.
- `POST /users/mobile/request-code/` (public) with `{ "mobile": "0912..." }` → `202`; sends a login code to the number by SMS (`OTP_CODE_LENGTH` digits, five by default). Always `202` when the number is well-formed, whether or not it is registered. `429` if a code was sent in the last 60 seconds, `503` if the code could not be sent.
- `POST /users/mobile/verify-code/` (public) with `{ "mobile": "0912...", "code": "12345" }` → `{ "access", "refresh", "user" }`. A verified new mobile number creates an account automatically. `400` if the code is wrong, expired (2 minutes), already used, or out of attempts (5).
- `GET/PATCH /users/me/`.

The Django admin is at `/admin/`: a WordPress-style editor for content, SEO (Yoast-style analysis, Pages SEO, redirects, 404 monitor, media library) and users. See `README.md` → SEO admin.
