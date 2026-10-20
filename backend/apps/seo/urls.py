from django.urls import path

from apps.seo.views import NotFoundReportView, RedirectListView, RobotsView, SeoSettingsView, SitemapView

urlpatterns = [
    path("seo/settings/", SeoSettingsView.as_view()),
    path("seo/redirects/", RedirectListView.as_view()),
    path("seo/robots/", RobotsView.as_view()),
    path("seo/not-found/", NotFoundReportView.as_view()),
    path("seo/sitemap/", SitemapView.as_view()),
]
