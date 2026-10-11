from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .otp import OtpDeliveryError, OtpThrottled
from .serializers import (
    MobileCodeRequestSerializer,
    MobileCodeVerifySerializer,
    RegistrationSerializer,
    UserSerializer,
)
from .services import (
    get_or_create_mobile_user,
    issue_login_code,
    verify_login_code,
)


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MobileCodeRequestView(generics.GenericAPIView):
    serializer_class = MobileCodeRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            issue_login_code(serializer.validated_data["mobile"])
        except OtpThrottled:
            return Response(
                {"detail": "A code was just sent. Please wait before asking for another."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except OtpDeliveryError:
            # Deliberately generic: the reply must not name the delivery channel,
            # leak provider detail, or reveal whether the number is registered.
            return Response(
                {"detail": "Unable to send the login code. Please try again shortly."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"detail": "If this number can receive SMS, a login code was sent."},
            status=status.HTTP_202_ACCEPTED,
        )


class MobileCodeVerifyView(generics.GenericAPIView):
    serializer_class = MobileCodeVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = verify_login_code(
            serializer.validated_data["mobile"], serializer.validated_data["code"]
        )
        if not code:
            return Response(
                {"detail": "The login code is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = get_or_create_mobile_user(code.mobile)
        except IntegrityError:
            # A concurrent first login may have created this mobile user.
            user = get_or_create_mobile_user(code.mobile)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )
