# Configuration is read in config/env.py, which loads `.env.sample` then `.env`
# then the process environment. Add a new knob as a typed field there rather
# than reaching for os.getenv() here, so it is validated at startup, documented
# in `.env.sample`, and visible to everything that reads the same files.
from config.env import BASE_DIR, env

SECRET_KEY = env.SECRET_KEY
DEBUG = env.DEBUG
ALLOWED_HOSTS = env.allowed_hosts

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles", "rest_framework", "rest_framework_simplejwt",
    "django_filters", "corsheaders", "apps.common", "apps.users",
    "apps.content", "apps.inquiries", "apps.seo",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
# The frontend is served from its own origin (a different local port in
# development), so browser fetches are cross-origin. Allow everything while
# DEBUG is on; otherwise take the explicit list from CORS_ALLOWED_ORIGINS.
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env.cors_allowed_origins
CORS_ALLOW_CREDENTIALS = True

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend", "rest_framework.filters.SearchFilter", "rest_framework.filters.OrderingFilter"),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.DefaultPagination",
    "EXCEPTION_HANDLER": "apps.common.exceptions.api_exception_handler",
}



# Mobile login codes. The channel is pluggable (see apps/users/otp/) and the
# validated list of names lives in config/env.py.
OTP_BACKEND = env.OTP_BACKEND
OTP_CODE_LENGTH = env.OTP_CODE_LENGTH

# Telegram relay.
TELEGRAM_BOT_TOKEN = env.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = env.TELEGRAM_CHAT_ID
TELEGRAM_TIMEOUT = env.TELEGRAM_TIMEOUT
TELEGRAM_PROXY = env.TELEGRAM_PROXY
TELEGRAM_BASE_URL = env.TELEGRAM_BASE_URL

# Kavenegar SMS. Keep the API key server-side; it must never reach the frontend.
KAVENEGAR_API_KEY = env.KAVENEGAR_API_KEY
KAVENEGAR_SENDER = env.KAVENEGAR_SENDER
KAVENEGAR_TIMEOUT = env.KAVENEGAR_TIMEOUT

# Seeding -- `manage.py seed` reads these through django.conf.settings.
IMAGE_FINDER_URL = env.IMAGE_FINDER_URL
IMAGE_FINDER_TIMEOUT = env.IMAGE_FINDER_TIMEOUT
SEED_CUSTOMER_EMAIL = env.SEED_CUSTOMER_EMAIL
SEED_CUSTOMER_PASSWORD = env.SEED_CUSTOMER_PASSWORD
SEED_ADMIN_EMAIL = env.SEED_ADMIN_EMAIL
SEED_ADMIN_PASSWORD = env.SEED_ADMIN_PASSWORD
