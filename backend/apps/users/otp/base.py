"""Shared contract for OTP delivery backends.

A backend is a callable object with a single `send(mobile, code)` method. It
formats the message itself, because the wording differs per channel: an SMS goes
to the customer in Persian, while the Telegram operator relay is read by staff
and needs the destination number spelled out.

Backends raise `OtpDeliveryError` for anything the caller cannot fix -- an
unset token, a refused request, an unreachable provider. The view turns that
into a 503 without echoing provider detail to the client.
"""


class OtpDeliveryError(Exception):
    """The login code could not be handed to the delivery channel."""


class OtpThrottled(Exception):
    """A code was already sent to this number too recently."""
