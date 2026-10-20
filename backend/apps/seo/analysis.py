"""Yoast-style SEO checks for one record in one language.

The admin editor runs the same checks live in `static/seo/admin/seo-box.js` as
the editor types; this module scores saved records for the list-view dots and
the dashboard. Keep the two in step: a rule added here should be added there,
with the same thresholds, or the dot in the list will disagree with the box.
"""
from apps.content.richtext import plain_text

TITLE_MIN, TITLE_MAX = 30, 60
DESC_MIN, DESC_MAX = 120, 160

# Which model field plays which part, per model.
FIELD_MAP = {
    "service": {"title": "title", "intro": "summary", "body": "body", "image": "image", "min_words": 300},
    "brand": {"title": "name", "intro": "description", "body": "content", "image": "logo", "min_words": 200},
    "article": {"title": "title", "intro": "excerpt", "body": "body", "image": "image", "min_words": 600},
}


def _has(text, phrase):
    return bool(phrase) and phrase.lower() in (text or "").lower()


def analyse(obj, lang, site_title=""):
    """Return a list of `(status, message)` where status is good|ok|bad."""
    fields = FIELD_MAP[obj._meta.model_name]
    title = getattr(obj, f"{fields['title']}_{lang}", "") or ""
    intro = getattr(obj, f"{fields['intro']}_{lang}", "") or ""
    body = getattr(obj, f"{fields['body']}_{lang}", "") or ""
    seo_title = getattr(obj, f"seo_title_{lang}", "") or (f"{title} | {site_title}" if site_title else title)
    desc = getattr(obj, f"seo_description_{lang}", "") or ""
    kw = (getattr(obj, f"focus_keyword_{lang}", "") or "").strip()
    text = plain_text(body)
    words = len(text.split())
    results = []

    if not kw:
        results.append(("bad", "No focus keyphrase set."))
    else:
        results.append(("good" if _has(seo_title, kw) else "bad", "Keyphrase in SEO title."))
        results.append(("good" if _has(desc, kw) else "bad", "Keyphrase in meta description."))
        first_para = (plain_text(intro) or text)[:400]
        results.append(("good" if _has(first_para, kw) else "ok", "Keyphrase in the introduction."))
        if words:
            count = text.lower().count(kw.lower())
            density = count * len(kw.split()) / words * 100
            status = "good" if 0.5 <= density <= 3 else ("ok" if count else "bad")
            results.append((status, f"Keyphrase density {density:.1f}% (aim for 0.5–3%)."))
        if lang == "en":
            slug_kw = "-".join(kw.lower().split())
            results.append(("good" if slug_kw in obj.slug else "ok", "Keyphrase in the URL slug."))

    n = len(seo_title)
    results.append(("good" if TITLE_MIN <= n <= TITLE_MAX else ("ok" if n else "bad"),
                    f"SEO title is {n} characters (aim for {TITLE_MIN}–{TITLE_MAX})."))
    n = len(desc)
    results.append(("good" if DESC_MIN <= n <= DESC_MAX else ("ok" if n else "bad"),
                    f"Meta description is {n} characters (aim for {DESC_MIN}–{DESC_MAX})."))
    results.append(("good" if words >= fields["min_words"] else ("ok" if words >= 100 else "bad"),
                    f"Body has {words} words (aim for {fields['min_words']}+)."))
    results.append(("good" if "<h2" in body.lower() else "ok", "Body uses H2 subheadings."))
    results.append(("good" if 'href="/' in body or "href='/" in body else "ok",
                    "Body links to another page on this site."))
    if getattr(obj, fields["image"], "") or obj.og_image:
        alt = getattr(obj, f"image_alt_{lang}", "")
        results.append(("good" if alt else "ok", "Main image has alt text."))
    else:
        results.append(("ok", "No image set."))
    return results


def score(results):
    """Overall traffic light: good when ≥ 80% of checks pass, bad under 50%."""
    if not results:
        return "bad"
    points = sum({"good": 1, "ok": 0.5, "bad": 0}[s] for s, _ in results) / len(results)
    if any(s == "bad" for s, m in results if m.startswith("No focus")):
        return "bad"
    return "good" if points >= 0.8 else ("ok" if points >= 0.5 else "bad")
