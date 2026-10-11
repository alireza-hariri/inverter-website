"""Telegram Bot API delivery, relayed through a single operator chat.

Docs: https://core.telegram.org/bots/api#sendmessage

A Telegram bot cannot address a phone number -- it can only post into a chat
that already exists on its side. So this backend does not message the customer
directly. Every login code is posted into one fixed chat (`TELEGRAM_CHAT_ID`),
which an operator watches and relays to the customer by hand. That is the whole
reason this is a stopgap: it is a staffed channel, not self-service delivery.

To get the two required settings: talk to @BotFather to create the bot and copy
its token, then add the bot to the group (or DM it) that should receive the
codes, send it a message, and read the numeric chat id out of
`<base>/bot<TOKEN>/getUpdates`. Group ids are negative.

Because the codes pass through a human, keep that chat private to staff -- a
member of it can log in as any customer who requests a code.

Where `api.telegram.org` is filtered, two settings open a path to it without
changing anything else. `TELEGRAM_PROXY` sends the request through a proxy, and
`TELEGRAM_BASE_URL` swaps the host for a mirror you control. They compose, and
both default to off.
"""
import requests
from django.conf import settings

from .base import OtpDeliveryError

API_BASE_URL = "https://api.telegram.org"


def base_url():
    """The Bot API root, overridable for mirrors and self-hosted servers.

    Point `TELEGRAM_BASE_URL` at a reverse proxy you run or at a local
    telegram-bot-api server. It must be a name the TLS certificate covers: a
    bare IP such as `https://149.154.167.220` reaches Telegram but fails
    verification, so bypass poisoned DNS with a hosts entry, not this setting.
    """
    return (getattr(settings, "TELEGRAM_BASE_URL", "") or API_BASE_URL).rstrip("/")


def proxies():
    """`requests` proxy mapping, or None for a direct connection.

    One URL covers both schemes because every Bot API call is HTTPS. A SOCKS
    URL needs the PySocks extra, which `requests[socks]` in pyproject pulls in.
    """
    proxy = getattr(settings, "TELEGRAM_PROXY", "")
    return {"http": proxy, "https": proxy} if proxy else None


class TelegramBackend:
    name = "telegram"

    def send(self, mobile, code):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            raise OtpDeliveryError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must both be set."
            )

        proxy = proxies()
        try:
            response = requests.post(
                f"{base_url()}/bot{token}/sendMessage",
                data={"chat_id": chat_id, "text": self.message(mobile, code)},
                timeout=getattr(settings, "TELEGRAM_TIMEOUT", 10),
                proxies=proxy,
            )
            body = response.json()
        except requests.RequestException as exc:
            # Name the proxy when one is configured; otherwise a dead proxy and a
            # blocked direct route are indistinguishable from the log.
            hop = "the configured proxy" if proxy else "Telegram"
            raise OtpDeliveryError(f"Could not reach {hop}.") from exc
        except ValueError as exc:
            raise OtpDeliveryError("Telegram returned an unreadable response.") from exc

        if not body.get("ok"):
            # `description` names the real cause: a bad token, a chat the bot was
            # never added to, or a bot blocked by the group.
            raise OtpDeliveryError(
                body.get("description") or "Telegram rejected the message."
            )
        return body

    def message(self, mobile, code):
        return f"Login code for {mobile}: {code}"
