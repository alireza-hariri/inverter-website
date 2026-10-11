from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Article, Brand, Service


class SitemapView(APIView):
    permission_classes = []

    def get(self, request):
        lang = request.query_params.get("language", "fa")
        if lang not in ("fa", "en"):
            raise ValidationError({"language": "Must be 'fa' or 'en'."})
        records = [
            {"route": "home", "slug": "", "updated_at": "", "no_index": False},
            {"route": "services", "slug": "", "updated_at": "", "no_index": False},
            {"route": "brands", "slug": "", "updated_at": "", "no_index": False},
            {"route": "articles", "slug": "", "updated_at": "", "no_index": False},
            {"route": "about", "slug": "", "updated_at": "", "no_index": False},
            {"route": "contact", "slug": "", "updated_at": "", "no_index": False},
        ]
        for s in Service.objects.filter(published=True, no_index=False):
            records.append({"route": "service", "slug": s.slug,
                            "updated_at": s.updated_at.isoformat(), "no_index": False})
        for b in Brand.objects.filter(published=True, no_index=False):
            records.append({"route": "brand", "slug": b.slug,
                            "updated_at": b.updated_at.isoformat(), "no_index": False})
        for a in Article.objects.filter(published=True, no_index=False):
            updated = (a.published_at or a.updated_at).isoformat() if (a.published_at or a.updated_at) else ""
            records.append({"route": "article", "slug": a.slug,
                            "updated_at": updated, "no_index": False})
        return Response({"language": lang, "results": records})
