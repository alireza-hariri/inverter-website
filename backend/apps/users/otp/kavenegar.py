"""Kavenegar SMS delivery -- the channel this template will settle on.

Docs: https://kavenegar.com/rest.html

`KAVENEGAR_SENDER` is optional; leaving it blank lets Kavenegar pick one of the
shared numbers on the account. The API answers HTTP 200 even for rejections and
puts the real outcome in `return.status`, so that field is what decides success
here rather than the status code.
"""
import requests
from django.conf import settings

from .base import OtpDeliveryError

API_BASE_URL = "https://api.kavenegar.com"
STATUS_OK = 200


class KavenegarBackend:
    name = "kavenegar"

    def send(self, mobile, code):
        api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
        if not api_key:
            raise OtpDeliveryError("KAVENEGAR_API_KEY is not set.")

        data = {"receptor": mobile, "message": self.message(mobile, code)}
        sender = getattr(settings, "KAVENEGAR_SENDER", "")
        if sender:
            data["sender"] = sender

        try:
            response = requests.post(
                f"{API_BASE_URL}/v1/{api_key}/sms/send.json",
                data=data,
                timeout=getattr(settings, "KAVENEGAR_TIMEOUT", 10),
            )
            response.raise_for_status()
            body = response.json()
        except requests.RequestException as exc:
            raise OtpDeliveryError("Could not reach the SMS provider.") from exc
        except ValueError as exc:
            raise OtpDeliveryError("The SMS provider returned an unreadable response.") from exc

        if body.get("return", {}).get("status") != STATUS_OK:
            raise OtpDeliveryError(
                body.get("return", {}).get("message") or "The SMS provider rejected the message."
            )
        return body

    def message(self, mobile, code):
        # Customer-facing, so it matches the wording the UI uses.
        return f"کد ورود شما: {code}"
