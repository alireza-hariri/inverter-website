from django.urls import path

from apps.content.views import (
    ArticleDetailView,
    ArticleListView,
    BrandDetailView,
    BrandListView,
    HomeContentView,
    ServiceDetailView,
    ServiceListView,
)

urlpatterns = [
    path("content/home/", HomeContentView.as_view()),
    path("services/", ServiceListView.as_view()),
    path("services/<slug:slug>/", ServiceDetailView.as_view()),
    path("brands/", BrandListView.as_view()),
    path("brands/<slug:slug>/", BrandDetailView.as_view()),
    path("articles/", ArticleListView.as_view()),
    path("articles/<slug:slug>/", ArticleDetailView.as_view()),
]
