"""Pluggable delivery for mobile login codes.

`OTP_BACKEND` picks the channel. Today it defaults to `telegram`, which relays
codes through a staffed operator chat; the intended end state is `kavenegar`,
real SMS to the customer's own phone. Nothing outside this package knows which
one is active, and no user-visible string names the channel, so the switch is an
env change and a redeploy.

Adding a channel means writing a class with `send(mobile, code)` that raises
`OtpDeliveryError` on failure, then registering it in `BACKENDS` below.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import OtpDeliveryError, OtpThrottled
from .console import ConsoleBackend
from .kavenegar import KavenegarBackend
from .telegram import TelegramBackend

__all__ = ["OtpDeliveryError", "OtpThrottled", "get_backend", "send_code"]

BACKENDS = {
    TelegramBackend.name: TelegramBackend,
    KavenegarBackend.name: KavenegarBackend,
    ConsoleBackend.name: ConsoleBackend,
}

DEFAULT_BACKEND = TelegramBackend.name


def get_backend():
    """Instantiate the configured backend.

    Resolved per call rather than cached at import time so `override_settings`
    works in tests and a redeploy is enough to change channels.
    """
    name = getattr(settings, "OTP_BACKEND", DEFAULT_BACKEND) or DEFAULT_BACKEND
    try:
        return BACKENDS[name]()
    except KeyError:
        raise ImproperlyConfigured(
            f"OTP_BACKEND={name!r} is not one of {sorted(BACKENDS)}."
        ) from None


def send_code(mobile, code):
    return get_backend().send(mobile, code)
