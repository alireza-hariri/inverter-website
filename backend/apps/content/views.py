from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import DefaultPagination
from apps.content.models import Article, Brand, Service
from apps.content.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    BrandDetailSerializer,
    BrandListSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
)

VALID_LANGUAGES = ("fa", "en")


def get_language(request):
    lang = request.query_params.get("language", "fa")
    if lang not in VALID_LANGUAGES:
        raise ValidationError({"language": "Must be 'fa' or 'en'."})
    return lang


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceListSerializer
    permission_classes = []
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {"language": get_language(self.request)}

    def get_queryset(self):
        return Service.objects.filter(published=True).order_by("ordering", "-updated_at")


class ServiceDetailView(APIView):
    permission_classes = []

    def get(self, request, slug):
        lang = get_language(request)
        try:
            obj = Service.objects.get(slug=slug, published=True)
        except Service.DoesNotExist:
            raise NotFound("Service not found.")
        return Response(ServiceDetailSerializer(obj, context={"language": lang}).data)


class BrandListView(generics.ListAPIView):
    serializer_class = BrandListSerializer
    permission_classes = []
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {"language": get_language(self.request)}

    def get_queryset(self):
        qs = Brand.objects.filter(published=True)
        category = self.request.query_params.get("category")
        if category:
            if category not in ("elevator", "industrial", "solar"):
                raise ValidationError({"category": "Must be elevator, industrial or solar."})
            qs = qs.filter(category=category)
        return qs.order_by("ordering", "-updated_at")


class BrandDetailView(APIView):
    permission_classes = []

    def get(self, request, slug):
        lang = get_language(request)
        try:
            obj = Brand.objects.get(slug=slug, published=True)
        except Brand.DoesNotExist:
            raise NotFound("Brand not found.")
        return Response(BrandDetailSerializer(obj, context={"language": lang}).data)


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = []
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {"language": get_language(self.request)}

    def get_queryset(self):
        qs = Article.objects.filter(published=True)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title_fa__icontains=search) | Q(title_en__icontains=search)
                | Q(excerpt_fa__icontains=search) | Q(excerpt_en__icontains=search)
                | Q(body_fa__icontains=search) | Q(body_en__icontains=search)
            )
        return qs.order_by("-published_at", "-updated_at")


class ArticleDetailView(APIView):
    permission_classes = []

    def get(self, request, slug):
        lang = get_language(request)
        try:
            obj = Article.objects.get(slug=slug, published=True)
        except Article.DoesNotExist:
            raise NotFound("Article not found.")
        return Response(ArticleDetailSerializer(obj, context={"language": lang}).data)


class HomeContentView(APIView):
    permission_classes = []

    def get(self, request):
        lang = get_language(request)
        ctx = {"language": lang}
        services = Service.objects.filter(published=True).order_by("ordering")[:10]
        brands = Brand.objects.filter(published=True).order_by("ordering")[:12]
        articles = Article.objects.filter(published=True).order_by("-published_at")[:6]
        from apps.seo.models import SiteSetting
        try:
            setting = SiteSetting.objects.get(language=lang)
            site = {"site_title": setting.site_title, "tagline": setting.tagline,
                    "meta_description": setting.meta_description, "og_image": setting.og_image,
                    "phone": setting.phone, "address": setting.address,
                    "org_name": setting.org_name}
        except SiteSetting.DoesNotExist:
            site = {"site_title": "الکتروگلد" if lang == "fa" else "ElectroGold",
                    "tagline": "", "meta_description": "", "og_image": "",
                    "phone": "", "address": "", "org_name": ""}
        return Response({
            "language": lang,
            "site": site,
            "services": ServiceListSerializer(services, many=True, context=ctx).data,
            "brands": BrandListSerializer(brands, many=True, context=ctx).data,
            "articles": ArticleListSerializer(articles, many=True, context=ctx).data,
        })
