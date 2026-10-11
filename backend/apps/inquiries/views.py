from rest_framework import generics
from rest_framework.throttling import AnonRateThrottle

from apps.inquiries.models import ContactInquiry
from apps.inquiries.serializers import ContactInquirySerializer


class InquiryBurstThrottle(AnonRateThrottle):
    rate = "20/min"


class ContactInquiryCreateView(generics.CreateAPIView):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer
    permission_classes = []
    throttle_classes = [InquiryBurstThrottle]
