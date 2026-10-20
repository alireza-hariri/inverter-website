import hmac

from django.conf import settings
from django.db.models import F
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.common.i18n import get_language
from apps.content.models import Article, Brand, Service
from apps.seo.models import PAGE_CHOICES, GlobalSeoSetting, NotFoundLog, PageSeo, Redirect, normalise_path
from apps.seo.serializers import (
    GlobalSeoSettingSerializer,
    NotFoundReportSerializer,
    RedirectSerializer,
    page_block,
    site_block,
)


class SeoSettingsView(APIView):
    """Everything the frontend's <head> needs that is not specific to one page."""
    permission_classes = []

    def get(self, request):
        lang = get_language(request)
        pages = {p.page: page_block(p, lang) for p in PageSeo.objects.all()}
        return Response({
            "language": lang,
            "site": site_block(lang),
            "global": GlobalSeoSettingSerializer(GlobalSeoSetting.load()).data,
            "pages": pages,
        })


class RedirectListView(APIView):
    """Every active redirect, unpaginated -- the frontend proxy matches against all of them."""
    permission_classes = []

    def get(self, request):
        qs = Redirect.objects.filter(active=True)
        return Response({"results": RedirectSerializer(qs, many=True).data})


class RobotsView(APIView):
    permission_classes = []

    def get(self, request):
        setting = GlobalSeoSetting.load()
        content = "User-agent: *\nDisallow: /" if setting.discourage_search_engines else setting.robots_txt
        return Response({"content": content.replace("\r\n", "\n").strip()})


class NotFoundThrottle(AnonRateThrottle):
    rate = "120/min"


class NotFoundReportView(APIView):
    """The frontend reports each 404 it serves; the admin shows them as the 404 monitor."""
    permission_classes = []
    throttle_classes = [NotFoundThrottle]

    def post(self, request):
        token = settings.SEO_INGEST_TOKEN
        sent = request.headers.get("X-Seo-Token", "")
        if token:
            if not hmac.compare_digest(token, sent):
                raise PermissionDenied("Bad SEO ingest token.")
        elif not settings.DEBUG:
            raise PermissionDenied("404 reporting is disabled: set SEO_INGEST_TOKEN.")
        data = NotFoundReportSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        path = normalise_path(data.validated_data["path"].split("?", 1)[0])
        referrer = data.validated_data.get("referrer", "")[:500]
        updated = NotFoundLog.objects.filter(path=path).update(
            hits=F("hits") + 1, last_referrer=referrer or F("last_referrer"), resolved=False)
        if not updated:
            NotFoundLog.objects.get_or_create(path=path, defaults={"last_referrer": referrer})
        return Response(status=204)


class SitemapView(APIView):
    permission_classes = []

    def get(self, request):
        lang = get_language(request)
        hidden_pages = set(PageSeo.objects.filter(no_index=True).values_list("page", flat=True))
        records = [
            {"route": page, "slug": "", "updated_at": "", "no_index": False}
            for page, _ in PAGE_CHOICES
            if page not in hidden_pages
        ]
        for s in Service.objects.filter(published=True, no_index=False):
            records.append({"route": "service", "slug": s.slug,
                            "updated_at": s.updated_at.isoformat(), "no_index": False})
        for b in Brand.objects.filter(published=True, no_index=False):
            records.append({"route": "brand", "slug": b.slug,
                            "updated_at": b.updated_at.isoformat(), "no_index": False})
        for a in Article.objects.live().filter(no_index=False):
            # An edit after publishing is a modification search engines should recrawl.
            stamp = max(filter(None, (a.published_at, a.updated_at)))
            records.append({"route": "article", "slug": a.slug,
                            "updated_at": stamp.isoformat(), "no_index": False})
        return Response({"language": lang, "results": records})
