"""Widgets for the admin dashboard (templates/admin/index.html)."""
from django import template
from django.conf import settings
from django.urls import reverse

from apps.content.models import Article, Brand, Service
from apps.inquiries.models import ContactInquiry
from apps.seo import analysis
from apps.seo.models import GlobalSeoSetting, NotFoundLog, PageSeo, Redirect, SiteSetting

register = template.Library()


@register.inclusion_tag("admin/seo/dashboard.html", takes_context=True)
def seo_dashboard(context):
    titles = dict(SiteSetting.objects.values_list("language", "site_title"))
    scores = {"good": 0, "ok": 0, "bad": 0}
    needs_work = []
    for model in (Service, Brand, Article):
        for obj in model.objects.filter(published=True):
            results = analysis.analyse(obj, "fa", titles.get("fa", ""))
            verdict = analysis.score(results)
            scores[verdict] += 1
            if verdict != "good":
                failing = [m for s, m in results if s == "bad"] or [m for s, m in results if s == "ok"]
                needs_work.append({
                    "label": str(getattr(obj, "title_fa", "") or getattr(obj, "name_fa", "") or obj.slug),
                    "kind": model._meta.verbose_name,
                    "verdict": verdict,
                    "reason": failing[0] if failing else "",
                    "url": reverse(f"admin:content_{model._meta.model_name}_change", args=[obj.pk]),
                })
    needs_work.sort(key=lambda r: r["verdict"] != "bad")
    total = sum(scores.values()) or 1
    seo = GlobalSeoSetting.load()
    site = settings.FRONTEND_URL
    missing_pages = PageSeo.objects.filter(seo_description_fa="").count()
    return {
        "glance": [
            ("Services", Service.objects.filter(published=True).count(), "admin:content_service_changelist"),
            ("Brands", Brand.objects.filter(published=True).count(), "admin:content_brand_changelist"),
            ("Articles", Article.objects.live().count(), "admin:content_article_changelist"),
            ("Redirects", Redirect.objects.filter(active=True).count(), "admin:seo_redirect_changelist"),
        ],
        "scores": scores,
        "bars": {k: round(v * 100 / total) for k, v in scores.items()},
        "needs_work": needs_work[:8],
        "noindex": sum(m.objects.filter(published=True, no_index=True).count() for m in (Service, Brand, Article)),
        "missing_pages": missing_pages,
        "discouraged": seo.discourage_search_engines,
        "verified": bool(seo.google_site_verification),
        "analytics": bool(seo.gtm_id or seo.ga4_id),
        "not_found": NotFoundLog.objects.filter(resolved=False)[:6],
        "not_found_count": NotFoundLog.objects.filter(resolved=False).count(),
        "inquiries": ContactInquiry.objects.all()[:5],
        "new_inquiries": ContactInquiry.objects.filter(status="new").count(),
        "links": [
            ("Sitemap", f"{site}/sitemap.xml"),
            ("robots.txt", f"{site}/robots.txt"),
            ("Rich results test", f"https://search.google.com/test/rich-results?url={site}/fa"),
            ("PageSpeed Insights", f"https://pagespeed.web.dev/analysis?url={site}/fa"),
            ("Search Console", "https://search.google.com/search-console"),
        ],
    }
