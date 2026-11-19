"""Turns an editor's body field into HTML that is safe to put on the page.

Bodies are written in the admin's visual editor, so they are HTML -- but older
records (and anything pasted into the HTML tab) may be plain text or contain
markup no page should carry. Everything goes through `render`, which:

- treats text with no tags as paragraphs, so legacy content keeps its breaks;
- sanitizes against an allowlist (nh3), so a stray <script> or onclick never
  reaches a visitor; off-site links get rel="noopener";
- gives every h2/h3 a stable id and returns them as a table of contents.
"""
import html
import re

import nh3

ALLOWED_TAGS = {
    "p", "br", "h2", "h3", "h4", "strong", "b", "em", "i", "u", "s", "a", "ul", "ol", "li",
    "blockquote", "img", "figure", "figcaption", "table", "thead", "tbody", "tr", "th", "td",
    "hr", "code", "pre", "span", "mark", "sub", "sup",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "th": {"colspan", "rowspan", "scope"},
    "td": {"colspan", "rowspan"},
    "*": {"dir"},
}
TAG = re.compile(r"<\s*[a-zA-Z][^>]*>")
HEADING = re.compile(r"<(h[23])>(.*?)</\1>", re.DOTALL)
STRIP_TAGS = re.compile(r"<[^>]+>")
CTA_PLACEHOLDER = re.compile(
    r"\[(?=[^\]\r\n]*(?:دکمه|تماس|مشاوره|شماره|درخواست|بازدید|لینک|واتس|فرم|button|call|contact|request|visit|link|form|whatsapp))[^\]\r\n]+\]",
    re.IGNORECASE,
)
CONTACT_SENTENCE = re.compile(r"(?:تماس بگیرید|تماس با کارشناسان|call (?:our|the) experts)", re.IGNORECASE)
DEFAULT_CONTACT_PHONE = "02140228578"
# Internal links keep their referrer for analytics; only off-site ones get rel.
EXTERNAL_LINK = re.compile(r'<a((?=[^>]*href="https?://)[^>]*?)(?=>)')


def _paragraphs(text):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return "".join(f"<p>{html.escape(b).replace(chr(10), '<br>')}</p>" for b in blocks)


def _slug(text, used):
    base = re.sub(r"[^\w؀-ۿ]+", "-", text, flags=re.UNICODE).strip("-").lower()[:60] or "section"
    slug, n = base, 2
    while slug in used:
        slug, n = f"{base}-{n}", n + 1
    used.add(slug)
    return slug


def _call_button(label, phone):
    number = re.sub(r"[^\d+]", "", str(phone or DEFAULT_CONTACT_PHONE))
    if not number:
        number = DEFAULT_CONTACT_PHONE
    label = html.unescape(STRIP_TAGS.sub("", label)).strip()
    label = re.sub(r"^(?:شماره\s*تماس\s*/\s*)?(?:دکمه|button)\s*:?\s*", "", label, flags=re.IGNORECASE)
    label = html.escape(label or "تماس با الکتروگلد")
    return f'<a href="tel:{html.escape(number, quote=True)}">{label}</a>'


def _request_button(label, contact_url):
    label = html.unescape(STRIP_TAGS.sub("", label)).strip()
    label = re.sub(r"^(?:شماره\s*تماس\s*/\s*)?(?:دکمه|button)\s*:?\s*", "", label, flags=re.IGNORECASE)
    label = html.escape(label or "درخواست مشاوره")
    if not contact_url.startswith("/") or contact_url.startswith("//"):
        contact_url = "/fa/contact"
    return f'<a href="{html.escape(contact_url, quote=True)}">{label}</a>'


def render(raw, contact_phone="", contact_url="/fa/contact"):
    """Return `(html, toc)` where toc is `[{"id", "text", "level"}]`."""
    raw = (raw or "").strip()
    if not raw:
        return "", []
    source = raw if TAG.search(raw) else _paragraphs(raw)
    has_button_placeholder = bool(CTA_PLACEHOLDER.search(source))
    def cta_button(match):
        label = match.group(0)[1:-1]
        if re.search(r"(?:درخواست|بازدید|لینک|واتس|فرم|request|visit|link|form|whatsapp)", label, re.IGNORECASE) and not re.search(
                r"(?:تماس|call|phone)", label, re.IGNORECASE):
            return _request_button(label, contact_url)
        return _call_button(label, contact_phone)

    source = CTA_PLACEHOLDER.sub(cta_button, source)
    if not has_button_placeholder:
        paragraph = re.compile(r"<p>(.*?)</p>", re.DOTALL)

        def link_contact_paragraph(match):
            content = match.group(1)
            plain = html.unescape(STRIP_TAGS.sub(" ", content))
            if not CONTACT_SENTENCE.search(plain) or 'href="tel:' in content:
                return match.group(0)
            return f"<p>{_call_button(content, contact_phone)}</p>"

        source = paragraph.sub(link_contact_paragraph, source)
    clean = nh3.clean(
        source,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto", "tel"},
        link_rel=None,
    )
    clean = EXTERNAL_LINK.sub(r'<a\1 rel="noopener"', clean)
    toc, used = [], set()

    def anchor(match):
        tag, inner = match.group(1), match.group(2)
        text = html.unescape(STRIP_TAGS.sub("", inner)).strip()
        if not text:
            return match.group(0)
        slug = _slug(text, used)
        toc.append({"id": slug, "text": text, "level": int(tag[1])})
        return f'<{tag} id="{slug}">{inner}</{tag}>'

    return HEADING.sub(anchor, clean), toc


def plain_text(raw):
    """The visible words of a body, for word counts and keyphrase checks."""
    return html.unescape(STRIP_TAGS.sub(" ", raw or "")).strip()


def reading_minutes(raw):
    words = len(plain_text(raw).split())
    return max(1, round(words / 200)) if words else 0
