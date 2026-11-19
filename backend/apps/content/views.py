from django.db.models import Exists, OuterRef, Q
from django.http import Http404
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.i18n import get_language
from apps.content.models import CATEGORY_CHOICES, Article, Brand, FaqItem, Service
from apps.content.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    BrandDetailSerializer,
    BrandListSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    faq_list,
)
from apps.seo.serializers import site_block

CATEGORIES = [value for value, _ in CATEGORY_CHOICES]


class PublicContentMixin:
    """Public, read-only, and answered in the request's `?language=`."""
    permission_classes = []
    lookup_field = "slug"
    # Detail views name their record in the 404 body, e.g. "Service not found."
    not_found_message = "Not found."

    def get_serializer_context(self):
        return {"language": get_language(self.request)}

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise NotFound(self.not_found_message) from exc


class ServiceListView(PublicContentMixin, generics.ListAPIView):
    serializer_class = ServiceListSerializer
    queryset = Service.objects.filter(published=True).order_by("ordering", "-updated_at")


class ServiceDetailView(PublicContentMixin, generics.RetrieveAPIView):
    serializer_class = ServiceDetailSerializer
    queryset = Service.objects.filter(published=True)
    not_found_message = "Service not found."


class BrandListView(PublicContentMixin, generics.ListAPIView):
    serializer_class = BrandListSerializer

    def get_queryset(self):
        qs = Brand.objects.filter(published=True).prefetch_related("services")
        category = self.request.query_params.get("category")
        if category:
            if category not in CATEGORIES:
                raise ValidationError({"category": f"Must be {', '.join(CATEGORIES[:-1])} or {CATEGORIES[-1]}."})
            public_services = Service.objects.filter(brands=OuterRef("pk"), published=True)
            qs = qs.annotate(has_public_services=Exists(public_services)).filter(
                Q(services__published=True, services__category=category)
                | Q(category=category, has_public_services=False)
            ).distinct()
        return qs.order_by("ordering", "-updated_at")


class BrandDetailView(PublicContentMixin, generics.RetrieveAPIView):
    serializer_class = BrandDetailSerializer
    queryset = Brand.objects.filter(published=True)
    not_found_message = "Brand not found."


class ArticleListView(PublicContentMixin, generics.ListAPIView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        qs = Article.objects.live()
        article_type = self.request.query_params.get("article_type")
        if article_type:
            valid_types = {value for value, _ in Article.ARTICLE_TYPE_CHOICES}
            if article_type not in valid_types:
                raise ValidationError({"article_type": f"Must be one of: {', '.join(sorted(valid_types))}."})
            qs = qs.filter(article_type=article_type)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title_fa__icontains=search) | Q(title_en__icontains=search)
                | Q(excerpt_fa__icontains=search) | Q(excerpt_en__icontains=search)
                | Q(body_fa__icontains=search) | Q(body_en__icontains=search)
            )
        return qs.order_by("-published_at", "-updated_at")


class ArticleDetailView(PublicContentMixin, generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    not_found_message = "Article not found."

    def get_queryset(self):
        # Evaluated per request: `live()` compares against the current time.
        return Article.objects.live()


class HomeContentView(APIView):
    permission_classes = []

    def get(self, request):
        lang = get_language(request)
        ctx = {"language": lang}
        services = Service.objects.filter(published=True).order_by("ordering")[:10]
        brands = Brand.objects.filter(published=True).prefetch_related("services").order_by("ordering")[:50]
        articles = Article.objects.live().order_by("-published_at")[:6]
        return Response({
            "language": lang,
            "site": site_block(lang),
            "services": ServiceListSerializer(services, many=True, context=ctx).data,
            "brands": BrandListSerializer(brands, many=True, context=ctx).data,
            "articles": ArticleListSerializer(articles, many=True, context=ctx).data,
            "faqs": faq_list(FaqItem.objects.filter(show_on_home=True), lang),
        })
