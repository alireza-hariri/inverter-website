"""Development delivery: write the code to the application log.

Selected with `OTP_BACKEND=console`, which makes mobile login work with no
provider account at all. It refuses to run unless `DEBUG` is on, because a
console backend in production means every code sits in the log and no customer
ever receives one.
"""
import logging

from django.conf import settings

from .base import OtpDeliveryError

logger = logging.getLogger(__name__)


class ConsoleBackend:
    name = "console"

    def send(self, mobile, code):
        if not settings.DEBUG:
            raise OtpDeliveryError("The console OTP backend requires DEBUG.")
        logger.warning("Login code for %s: %s", mobile, code)
        return {"ok": True, "backend": self.name}
