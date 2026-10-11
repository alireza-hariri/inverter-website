import django_filters

from apps.content.models import Article, Brand, Service


class ServiceFilter(django_filters.FilterSet):
    class Meta:
        model = Service
        fields = {"category": ["exact"], "published": ["exact"]}


class BrandFilter(django_filters.FilterSet):
    class Meta:
        model = Brand
        fields = {"category": ["exact"], "published": ["exact"]}


class ArticleFilter(django_filters.FilterSet):
    class Meta:
        model = Article
        fields = {"published": ["exact"]}
