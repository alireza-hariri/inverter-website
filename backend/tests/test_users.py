from unittest.mock import patch

import requests
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.users import otp
from apps.users.models import MobileLoginCode
from apps.users.services import DEFAULT_CODE_LENGTH, _hash_code

# The digits the OTP tests drive verification with. Built from the configured
# default length so changing `DEFAULT_CODE_LENGTH` cannot silently break them.
VALID_CODE = "1" * DEFAULT_CODE_LENGTH
WRONG_CODE = "0" * DEFAULT_CODE_LENGTH


@override_settings(OTP_BACKEND="console", DEBUG=True)
class MobileLoginTests(TestCase):
    """Mobile OTP login, exercised over the console delivery backend.

    `console` keeps these tests off the network; the Telegram and Kavenegar
    backends are the same code path with a real HTTP call at the end.
    """

    def setUp(self):
        self.client = APIClient()

    def _request_code(self, mobile="09123456789", code=VALID_CODE):
        """Ask for a code, then overwrite the hash so the test knows the digits.

        The real code is never returned by the API and only the HMAC is stored,
        so replacing the hash is the only way to drive verification from a test.
        """
        response = self.client.post("/api/users/mobile/request-code/", {"mobile": mobile}, format="json")
        self.assertEqual(response.status_code, 202)
        login_code = MobileLoginCode.objects.get(mobile="09123456789", consumed_at__isnull=True)
        login_code.code_hash = _hash_code(code)
        login_code.save(update_fields=["code_hash"])
        return login_code

    def test_mobile_login(self):
        # `+98...` must land on the same account as the canonical `09...` form.
        self._request_code(mobile="+989123456789")
        response = self.client.post(
            "/api/users/mobile/verify-code/",
            {"mobile": "09123456789", "code": VALID_CODE},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["mobile"], "09123456789")

    def test_mobile_code_cannot_be_reused(self):
        self._request_code()
        payload = {"mobile": "09123456789", "code": VALID_CODE}
        self.assertEqual(self.client.post("/api/users/mobile/verify-code/", payload, format="json").status_code, 200)
        self.assertEqual(self.client.post("/api/users/mobile/verify-code/", payload, format="json").status_code, 400)

    def test_wrong_mobile_code_is_rejected(self):
        self._request_code()
        response = self.client.post(
            "/api/users/mobile/verify-code/",
            {"mobile": "09123456789", "code": WRONG_CODE},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(MobileLoginCode.objects.get(mobile="09123456789").attempts, 1)

    def test_mobile_code_resend_is_throttled(self):
        self._request_code()
        response = self.client.post("/api/users/mobile/request-code/", {"mobile": "09123456789"}, format="json")
        self.assertEqual(response.status_code, 429)

    def test_invalid_mobile_is_rejected(self):
        response = self.client.post("/api/users/mobile/request-code/", {"mobile": "12345"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(MobileLoginCode.objects.exists())

    def test_generated_codes_never_start_with_zero(self):
        """A leading zero is lost somewhere between here and the keypad.

        It survives generation, but not being read aloud, pasted through a field
        that trims it, or coerced to an integer by an SMS gateway -- and each of
        those turns a valid code into one that cannot be entered. 200 draws puts
        the odds of a padded generator slipping past this at about 1 in 10^9.
        """
        with patch("apps.users.services.otp.send_code") as send_code:
            for index in range(200):
                MobileLoginCode.objects.all().delete()
                response = self.client.post(
                    "/api/users/mobile/request-code/",
                    {"mobile": "09123456789"},
                    format="json",
                )
                self.assertEqual(response.status_code, 202)
                code = send_code.call_args.args[1]
                self.assertEqual(len(code), DEFAULT_CODE_LENGTH)
                self.assertNotEqual(code[0], "0", f"draw {index} produced {code}")

    @override_settings(OTP_BACKEND="console", DEBUG=True, OTP_CODE_LENGTH=8)
    def test_configured_code_length_is_generated_and_verified(self):
        with patch("apps.users.services.otp.send_code") as send_code:
            response = self.client.post(
                "/api/users/mobile/request-code/",
                {"mobile": "09123456789"},
                format="json",
            )
        self.assertEqual(response.status_code, 202)
        code = send_code.call_args.args[1]
        self.assertRegex(code, r"^[1-9]\d{7}$")

        login_code = MobileLoginCode.objects.get(
            mobile="09123456789", consumed_at__isnull=True
        )
        login_code.code_hash = _hash_code(code)
        login_code.save(update_fields=["code_hash"])
        response = self.client.post(
            "/api/users/mobile/verify-code/",
            {"mobile": "09123456789", "code": code},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    @override_settings(OTP_BACKEND="kavenegar", KAVENEGAR_API_KEY="")
    def test_unconfigured_backend_reports_unavailable(self):
        """A misconfigured channel must fail closed, and never name the provider."""
        response = self.client.post("/api/users/mobile/request-code/", {"mobile": "09123456789"}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(MobileLoginCode.objects.exists())


class OtpBackendTests(TestCase):
    """The delivery seam itself: selection, and the Telegram operator relay."""

    def test_unknown_backend_name_is_rejected(self):
        with override_settings(OTP_BACKEND="carrier-pigeon"):
            with self.assertRaises(ImproperlyConfigured):
                otp.get_backend()

    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_BASE_URL="",
    )
    def test_telegram_posts_the_code_to_the_operator_chat(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": True}
            otp.send_code("09123456789", "424242")
        url, = post.call_args.args
        self.assertEqual(url, "https://api.telegram.org/bot123:abc/sendMessage")
        data = post.call_args.kwargs["data"]
        self.assertEqual(data["chat_id"], "-100777")
        # The operator needs the destination number as well as the code.
        self.assertIn("09123456789", data["text"])
        self.assertIn("424242", data["text"])

    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_PROXY="socks5h://127.0.0.1:1080",
    )
    def test_telegram_routes_through_the_configured_proxy(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": True}
            otp.send_code("09123456789", "424242")
        self.assertEqual(
            post.call_args.kwargs["proxies"],
            {"http": "socks5h://127.0.0.1:1080", "https": "socks5h://127.0.0.1:1080"},
        )

    # `TELEGRAM_PROXY` must be overridden, not assumed: env seeding copies the
    # developer's own proxy into the generated `.env`, and this test asserts the
    # unproxied default.
    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_PROXY="",
    )
    def test_telegram_sends_direct_when_no_proxy_is_set(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": True}
            otp.send_code("09123456789", "424242")
        self.assertIsNone(post.call_args.kwargs["proxies"])

    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_BASE_URL="https://tg.example.com/",
    )
    def test_telegram_honours_a_custom_base_url(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": True}
            otp.send_code("09123456789", "424242")
        # The trailing slash must not produce a double slash in the path.
        self.assertEqual(post.call_args.args[0], "https://tg.example.com/bot123:abc/sendMessage")

    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_BASE_URL="",
    )
    def test_blank_base_url_falls_back_to_the_public_api(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": True}
            otp.send_code("09123456789", "424242")
        self.assertEqual(post.call_args.args[0], "https://api.telegram.org/bot123:abc/sendMessage")

    @override_settings(
        OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777",
        TELEGRAM_PROXY="socks5h://127.0.0.1:9",
    )
    def test_unreachable_proxy_names_the_proxy_in_the_error(self):
        with patch("apps.users.otp.telegram.requests.post", side_effect=requests.ConnectionError("nope")):
            with self.assertRaises(otp.OtpDeliveryError) as ctx:
                otp.send_code("09123456789", "424242")
        self.assertIn("proxy", str(ctx.exception))

    @override_settings(OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100777")
    def test_telegram_rejection_raises_delivery_error(self):
        with patch("apps.users.otp.telegram.requests.post") as post:
            post.return_value.json.return_value = {"ok": False, "description": "chat not found"}
            with self.assertRaises(otp.OtpDeliveryError):
                otp.send_code("09123456789", "424242")

    @override_settings(OTP_BACKEND="telegram", TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    def test_telegram_without_credentials_raises_delivery_error(self):
        with self.assertRaises(otp.OtpDeliveryError):
            otp.send_code("09123456789", "424242")

    @override_settings(OTP_BACKEND="console", DEBUG=False)
    def test_console_backend_refuses_to_run_outside_debug(self):
        with self.assertRaises(otp.OtpDeliveryError):
            otp.send_code("09123456789", "424242")
