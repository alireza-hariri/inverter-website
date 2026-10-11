from django.urls import path

from apps.inquiries.views import ContactInquiryCreateView

urlpatterns = [
    path("contact-inquiries/", ContactInquiryCreateView.as_view()),
]
