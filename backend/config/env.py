"""Typed configuration, loaded from the environment and the project's env files.

Django itself reads nothing but `os.environ`, so a generated project used to
ignore its own `.env` entirely and silently fall back to the defaults written
into `config/settings.py` -- a bot token sitting in `.env` never reached
Telegram, and only the serve pipeline papered over it by pushing the file's
values into each child process. Everything is read here instead, once, through
pydantic-settings.

Three layers, each overriding the one before it:

1. `.env.sample` -- committed, and the documented default for every key. It is
   read as configuration rather than kept as decoration, so a checkout with no
   `.env` at all still starts with a coherent set of values.
2. `.env` -- git-ignored, this machine's real values (tokens, a proxy, a
   merchant id). Only the keys it actually sets are overridden; anything it
   leaves out keeps the sample's value.
3. The process environment -- highest priority, so a caller that exports
   `OTP_BACKEND=console` for one run wins over both files without editing them.

Values are validated on import, which means a bad `OTP_CODE_LENGTH` or a
misspelled boolean stops the project at startup with a message naming the field
instead of failing much later inside a request.
"""
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


def _csv(value: str) -> list[str]:
    """Split a comma-separated setting, dropping blanks and surrounding space."""
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    # Complex types are deliberately declared as `str` and split by the
    # properties below. pydantic-settings parses a `list[str]` field as JSON,
    # which would reject the plain `ALLOWED_HOSTS=*` form the env files use.
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env.sample", BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        # The env files are shared with tooling outside Django (the serve
        # pipeline reads them too), so unknown keys are data, not errors.
        extra="ignore",
    )

    # -- core ------------------------------------------------------------

    SECRET_KEY: str = "unsafe-development-key-change-in-production"
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "*"
    # Blank means "no explicit list"; combined with DEBUG this allows any
    # origin in development. See config/settings.py.
    CORS_ALLOWED_ORIGINS: str = ""

    @property
    def allowed_hosts(self) -> list[str]:
        return _csv(self.ALLOWED_HOSTS)

    @property
    def cors_allowed_origins(self) -> list[str]:
        return _csv(self.CORS_ALLOWED_ORIGINS)

    # -- mobile login codes ----------------------------------------------

    # The channel is pluggable (see apps/users/otp/) so it can be swapped
    # without touching the API or the frontend -- no user-visible string names
    # the channel, and the UI always says SMS.
    #   telegram  relays each code into one staffed operator chat (today's default)
    #   kavenegar real SMS to the customer, the intended end state
    #   console   logs the code, DEBUG only, no provider account needed
    OTP_BACKEND: str = "telegram"
    OTP_CODE_LENGTH: int = Field(default=5, ge=4, le=10)

    @field_validator("OTP_BACKEND")
    @classmethod
    def _known_otp_backend(cls, value: str) -> str:
        known = {"telegram", "kavenegar", "console"}
        channel = value.strip().lower()
        if channel not in known:
            raise ValueError(f"must be one of {', '.join(sorted(known))}")
        return channel

    # -- Telegram relay --------------------------------------------------

    # A bot cannot message a phone number, only a chat it is already in, so
    # codes go to TELEGRAM_CHAT_ID and an operator passes them on. Anyone in
    # that chat can log in as any customer who requests a code -- keep it
    # staff-only.
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_TIMEOUT: int = Field(default=10, gt=0)
    # Where api.telegram.org is filtered, these two open a route to it. Both
    # are off by default and they compose. TELEGRAM_PROXY takes any URL
    # `requests` understands -- socks5h://127.0.0.1:1080,
    # http://user:pass@host:3128 -- and SOCKS needs the requests[socks] extra
    # that pyproject already requires.
    TELEGRAM_PROXY: str = ""
    # TELEGRAM_BASE_URL swaps the Bot API host for a reverse proxy you run or a
    # self-hosted telegram-bot-api server. The TLS certificate must cover the
    # name used, so a bare IP will not work here -- override poisoned DNS with
    # a hosts entry instead.
    TELEGRAM_BASE_URL: str = "https://api.telegram.org"

    # -- Kavenegar SMS ---------------------------------------------------

    # Keep the API key server-side; it must never reach the frontend. A blank
    # sender lets Kavenegar pick a shared number from the account.
    KAVENEGAR_API_KEY: str = ""
    KAVENEGAR_SENDER: str = ""
    KAVENEGAR_TIMEOUT: int = Field(default=10, gt=0)

    # -- seeding ---------------------------------------------------------

    # The image-finder service supplies photography for `manage.py seed`; if it
    # is not running, seeding still succeeds, just without new images.
    IMAGE_FINDER_URL: str = "http://127.0.0.1:3900"
    IMAGE_FINDER_TIMEOUT: int = Field(default=30, gt=0)
    SEED_CUSTOMER_EMAIL: str = "customer@example.com"
    SEED_CUSTOMER_PASSWORD: str = "customer-password"
    SEED_ADMIN_EMAIL: str = "admin@example.com"
    SEED_ADMIN_PASSWORD: str = "admin-password"


env = Settings()
