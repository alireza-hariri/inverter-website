from django.urls import path
from .views import (
    MeView,
    MobileCodeRequestView,
    MobileCodeVerifyView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view()),
    path("me/", MeView.as_view()),
    path("mobile/request-code/", MobileCodeRequestView.as_view()),
    path("mobile/verify-code/", MobileCodeVerifyView.as_view()),
]
