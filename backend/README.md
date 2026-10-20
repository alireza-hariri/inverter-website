# Observability Run Project

Django REST Framework backend. Requires Python 3.12+ and Cookiecutter. Install dependencies with `pip install -e .`, run `python manage.py makemigrations` then `python manage.py migrate` (this template ships no migration files; they are generated per project), create an admin with `python manage.py createsuperuser`, then run `python manage.py runserver`.

## Seed data

`python manage.py seed` fills an empty database and is safe to rerun: every row is upserted on a stable key (slug, email), so a second run updates what the first one made. It seeds demo accounts -- a customer and an admin -- and is where this site's own content belongs. Add `--no-demo` to skip the accounts.

Photography comes from the image-finder service at `IMAGE_FINDER_URL`. The lookup runs before the transaction opens and is best effort -- with the service down, seeding still completes and existing images are left alone. `--refresh-images` looks images up again for records that already have one.

A rerun deliberately does not touch what a running site owns: existing passwords. `--fresh` overrides that for local development, and `python scripts/reset_database.py` deletes the SQLite file, migrates, and seeds from nothing.

Add this site's records as constants at the top of `apps/common/management/commands/seed.py` and upsert them from a `seed_<thing>` method called inside `handle`'s transaction.

## Configuration

Every setting the project reads is declared once, as a typed field, in `config/env.py`, and `config/settings.py` does nothing but hand those values to Django. Three sources are layered, each overriding the one before it:

1. **`.env.sample`** — committed, and the documented default for every key. It is read as configuration rather than kept as decoration, so a fresh checkout with no `.env` at all still starts with a coherent set of values.
2. **`.env`** — git-ignored, this machine's real values (tokens, a proxy, a merchant id). Only the keys it actually sets are overridden, so there is no need to restate a default just to keep the file complete. Copy `.env.sample` to `.env` if you would rather start from the full list.
3. **The process environment** — highest priority, so `OTP_BACKEND=console python manage.py runserver` wins over both files without editing either.

Values are validated on import, so a misspelled boolean or an out-of-range `OTP_CODE_LENGTH` stops the project at startup with a message naming the field, instead of failing much later inside a request.

To add a setting: declare a typed field on `Settings` in `config/env.py`, document it with a default in `.env.sample`, and expose it in `config/settings.py` if Django or an app needs to read it through `django.conf.settings`. Reaching for `os.getenv()` instead skips the validation, leaves the key undocumented, and is caught by `tests/test_settings.py`.

Health: `GET /api/health/`. JWT endpoints are `/api/token/` and `/api/token/refresh/`. Admin uses Django sessions; customer APIs use Bearer JWTs.



## Mobile login

Customers sign in with a five-digit code by default (configurable with `OTP_CODE_LENGTH`, from 4 to 10) sent to their phone: `POST /api/users/mobile/request-code/` with `{"mobile": "0912..."}`, then `POST /api/users/mobile/verify-code/` with `{"mobile", "code"}`, which returns JWTs and creates the account if the number is new. Codes live two minutes, allow five wrong guesses, and can be re-requested once every 60 seconds. Only an HMAC of each code is stored, so the digits cannot be read back out of the database — including by the admin.

`OTP_BACKEND` picks how the code is delivered, and nothing outside `apps/users/otp/` depends on the choice. The API and the UI only ever say SMS, so switching channels is an env change and a redeploy.

- `telegram` (default) — **a stopgap, not self-service.** A Telegram bot cannot message a phone number, only a chat it has already been added to, so every code is posted into one chat (`TELEGRAM_CHAT_ID`) that an operator watches and relays to the customer by hand. Get `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather), add the bot to the staff chat, then read that chat's numeric id from `https://api.telegram.org/bot<TOKEN>/getUpdates` (group ids are negative). **Anyone in that chat can log in as any customer who requests a code — keep it staff-only.**
- `kavenegar` — real SMS to the customer, and the intended end state. Set `KAVENEGAR_API_KEY`; leave `KAVENEGAR_SENDER` blank to use a shared number from the account. This is the only backend that scales past a staffed chat.
- `console` — logs the code instead of sending it, and refuses to run unless `DEBUG` is on. The quickest way to exercise mobile login locally with no provider account.

Adding a channel means writing a class with `send(mobile, code)` that raises `OtpDeliveryError` on failure and registering it in `BACKENDS` in `apps/users/otp/__init__.py`.

## SEO admin

The admin at `/admin/` is laid out like WordPress (dark admin bar and left menu, Dashboard, white postboxes, a Publish box beside every editor) so an SEO specialist used to WordPress + Yoast finds things where they expect them.

| WordPress / Yoast | Here |
|---|---|
| Dashboard, Site Health | **Dashboard**: at a glance, SEO overview (good/needs work/poor), pages needing work, 404s, new repair requests, links to Search Console, Rich Results and PageSpeed |
| Posts / Pages editor | **Articles, Services, Brands**: Visual/HTML editor, Featured image, Publish box with schedule date, FAQ blocks |
| Yoast SEO box | **SEO — فارسی / English** boxes under every editor: focus keyphrase, SEO title, meta description, image alt, live Google preview (mobile/desktop), length meters and a checklist. The list pages show the same score as coloured dots |
| Yoast → Search Appearance | **SEO → Pages SEO** for the fixed pages (home, services list, brands, blog, about, contact), **SEO → Site identity** for the homepage H1, intro and contact details |
| Yoast → General / Webmaster tools | **SEO → SEO settings**: title separator, default share image, robots.txt, "discourage search engines", Google/Bing/Yandex verification, GTM / GA4, LocalBusiness schema, social profiles |
| Redirection plugin | **SEO → Redirects** (301/302/307/308/410, loop-checked) and **SEO → 404 monitor** with a one-click "Add redirect" |
| Media Library | **SEO → Media library**, also opened from every image field and the editor's 🖼 button |

What the site does with it, automatically: absolute titles (`SEO title`, or `Title | Site name`), canonical + hreflang (`fa`, `en`, `x-default`), Open Graph/Twitter cards, noindex where asked (and on search results and login pages), `/sitemap.xml` with hreflang alternates, `/robots.txt`, and JSON-LD for LocalBusiness, WebSite, Service, BlogPosting, BreadcrumbList and FAQPage. Redirects apply within a minute of saving, without a deploy.

The checks in the SEO box live twice -- `static/seo/admin/seo-box.js` (live, while typing) and `apps/seo/analysis.py` (list dots, dashboard) -- and must be kept in step. Body HTML from the editor is sanitized on the way out by `apps/content/richtext.py`.

`manage.py seed` never overwrites content or SEO fields an editor has changed: on an existing row it only fills fields that are still blank. `--fresh` restores the seeded values.
