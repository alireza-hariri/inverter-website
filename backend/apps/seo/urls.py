from django.urls import path

from apps.seo.views import SitemapView

urlpatterns = [
    path("seo/sitemap/", SitemapView.as_view()),
]
