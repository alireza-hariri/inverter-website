"""Mobile login: normalising numbers, issuing codes, and verifying them.

Codes are stored only as an HMAC of the digits, so a database dump does not hand
over live login codes. The delivery channel lives in `apps.users.otp` and is
chosen by `OTP_BACKEND`; nothing here knows or cares which one is active.
"""
import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from . import otp
from .models import MobileLoginCode

DEFAULT_CODE_LENGTH = 5
MIN_CODE_LENGTH = 4
MAX_CODE_LENGTH = 10
CODE_TTL = timedelta(minutes=2)
# Wrong guesses allowed per code before it is dead. Five digits with no leading
# zero is 90,000 codes, so five tries is a 1-in-18,000 chance, and the
# two-minute TTL closes the rest.
MAX_ATTEMPTS = 5
RESEND_INTERVAL = timedelta(seconds=60)


def normalize_mobile(value):
    """Return an Iranian mobile number in canonical `09xxxxxxxxx` form.

    Accepts what people actually type -- `+98`, `0098`, `98`, or a bare `9`
    prefix, with spaces or dashes -- so that one number cannot end up stored
    twice under two spellings.
    """
    mobile = str(value or "").strip().replace(" ", "").replace("-", "")
    if mobile.startswith("+98"):
        mobile = "0" + mobile[3:]
    elif mobile.startswith("0098"):
        mobile = "0" + mobile[4:]
    elif mobile.startswith("98"):
        mobile = "0" + mobile[2:]
    elif mobile.startswith("9") and len(mobile) == 10:
        mobile = "0" + mobile
    if len(mobile) != 11 or not mobile.startswith("09") or not mobile.isdigit():
        raise ValueError("Enter a valid Iranian mobile number.")
    return mobile


def _hash_code(code):
    return hmac.new(
        settings.SECRET_KEY.encode(), code.encode(), hashlib.sha256
    ).hexdigest()


def issue_login_code(mobile):
    """Invalidate any outstanding code for `mobile`, then send a fresh one.

    Raises `otp.OtpThrottled` if the last code is younger than
    `RESEND_INTERVAL`, and `otp.OtpDeliveryError` if the channel refuses it.

    Delivery happens inside the transaction on purpose: if the channel fails,
    the new code row rolls back and the previous code stays valid, so a provider
    outage cannot strand a customer who already has a working code.
    """
    now = timezone.now()
    if MobileLoginCode.objects.filter(
        mobile=mobile, created_at__gte=now - RESEND_INTERVAL
    ).exists():
        raise otp.OtpThrottled("Please wait before requesting another code.")

    code_length = getattr(settings, "OTP_CODE_LENGTH", DEFAULT_CODE_LENGTH)
    if not MIN_CODE_LENGTH <= code_length <= MAX_CODE_LENGTH:
        raise ValueError(
            f"OTP_CODE_LENGTH must be between {MIN_CODE_LENGTH} and {MAX_CODE_LENGTH}."
        )
    # Drawn from [10^(n-1), 10^n) so the first digit is never 0. A leading zero
    # survives here but not the trip out and back: it is read aloud and typed
    # back by a person, pasted through fields that trim it, and coerced to an
    # integer by more than one SMS gateway -- each of which turns a valid code
    # into a rejected one. The cost is a tenth of the code space, which the
    # two-minute TTL and MAX_ATTEMPTS already dominate.
    span = 10**code_length - 10 ** (code_length - 1)
    code = str(secrets.randbelow(span) + 10 ** (code_length - 1))
    with transaction.atomic():
        MobileLoginCode.objects.filter(
            mobile=mobile, consumed_at__isnull=True
        ).update(consumed_at=now)
        login_code = MobileLoginCode.objects.create(
            mobile=mobile,
            code_hash=_hash_code(code),
            expires_at=now + CODE_TTL,
        )
        otp.send_code(mobile, code)
    return login_code


def verify_login_code(mobile, code):
    """Consume the outstanding code for `mobile`, or return None.

    Returns None for every failure -- no code, expired, out of attempts, wrong
    digits -- so the caller cannot accidentally tell a client which it was.
    """
    # Lock the row so two simultaneous verification requests cannot both use
    # the same one-time code.
    with transaction.atomic():
        login_code = MobileLoginCode.objects.select_for_update().filter(
            mobile=mobile, consumed_at__isnull=True
        ).first()
        now = timezone.now()
        if not login_code or login_code.expires_at <= now or login_code.attempts >= MAX_ATTEMPTS:
            return None

        login_code.attempts += 1
        if not hmac.compare_digest(login_code.code_hash, _hash_code(code)):
            login_code.save(update_fields=("attempts",))
            return None

        login_code.consumed_at = now
        login_code.save(update_fields=("attempts", "consumed_at"))
        return login_code


def get_or_create_mobile_user(mobile):
    User = get_user_model()
    user = User.objects.filter(mobile=mobile).first()
    if user:
        return user
    # Email and username remain required by the existing custom user model.
    # The generated values are private implementation details and users can
    # update their profile after signing in. `.invalid` is reserved by RFC 2606,
    # so these addresses can never collide with a real one or be mailed.
    suffix = mobile[-10:]
    return User.objects.create_user(
        email=f"mobile-{suffix}@users.invalid",
        username=f"mobile-{suffix}",
        password=secrets.token_urlsafe(32),
        mobile=mobile,
    )
