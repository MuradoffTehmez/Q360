import datetime
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _ # type: ignore
from dotenv import load_dotenv # type: ignore

# ===================================================================
# ƏSAS QURĞULAR VƏ YOLLAR (BASE  CONFIGURATIONS & PATHS)
# ===================================================================

load_dotenv()  # .env faylını yükləyirik

BASE_DIR = Path(__file__).resolve().parent.parent  # Layihənin əsas direktoriyası

# ===================================================================
# TƏHLÜKƏSİZLİK (SECURITY SETTINGS)
# ===================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = (
    os.getenv("DEBUG", "False").lower() == "true"
)  # .env faylından DEBUG dəyərini oxuyuruq
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"]

AUTHENTICATION_BACKENDS = [
    "core.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ===================================================================
# TƏTBİQLƏR (INSTALLED APPLICATIONS)
# ===================================================================

INSTALLED_APPS = [
    # Xarici tətbiqlər (dizayn və s.)
    'jazzmin',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
    'django_celery_beat',  # Celery Beat üçün
    
    # REST API tətbiqləri
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    
    # Django-nun daxili tətbiqləri
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bizim lokal tətbiqimiz
    'core.apps.CoreConfig',
]

# ===================================================================
# MİDDLEWARE (ORTA QAT FUNKSİYALARI)
# ===================================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

# ===================================================================
# URL, WSGI
# ===================================================================

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ===================================================================
# GEMINI AI KONFİQURASİYASI (GOOGLE GEMINI AI CONFIGURATION)
# ===================================================================

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


# ===================================================================
# VERİLƏNLƏR BAZASI (DATABASE)
# ===================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ===================================================================
# ŞİFRƏ TƏHLÜKƏSİZLİYİ (PASSWORD VALIDATORS)
# ===================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===================================================================
# DİL VƏ SAAT ZONU (INTERNATIONALIZATION)
# ===================================================================

LANGUAGE_CODE = "az"
TIME_ZONE = "Asia/Baku"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("az", _("Azərbaycan")),
    ("en", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# ===================================================================
# STATİK FAYLLAR (STATIC FILES)
# ===================================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===================================================================
# AUTHENTICATION VƏ USER MODEL
# ===================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "core.Ishchi"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ===================================================================
# E-MAIL TƏNZİMLƏMƏLƏRİ (EMAIL CONFIGURATION)
# ===================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===================================================================
# CRISPY FORMS TƏNZİMLƏRİ
# ===================================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ===================================================================
# JAZZMIN – ADMIN PANELİ DİZAYNI
# ===================================================================

JAZZMIN_SETTINGS = {
    # Saytın brauzer başlığı
    "site_title": "360° İdarəetmə Paneli",
    # Navbar və login səhifəsindəki başlıq
    "site_header": "Qiymətləndirmə Sistemi",
    # Panel brendi
    "site_brand": "360° Dəyərləndirmə",
    # Admin başlığının sol üst hissəsi
    "site_header_short": "Dəyərləndirmə",
    # Xoş gəlmisiniz mətni
    "welcome_sign": "360° Qiymətləndirmə Sisteminə Xoş Gəlmisiniz",
    # Admin səhifəsinin alt hissəsi
    "copyright": "© 2025 Muradov İT MMC",
    # UI Builder-i göstərmək
    "show_ui_builder": True,
    # Yuxarı menyuya faydalı linklər əlavə edirik
    "topmenu_links": [
        # Əsas sayta keçid
        {"name": "Ana Səhifə", "url": "/", "permissions": ["auth.view_user"]},
        # Bütün istifadəçilərin siyahısı (bizim Ishchi modeli)
        {"model": "core.Ishchi"},
    ],
    # Yan menyunu avtomatik qruplaşdırmaq
    "order_with_respect_to": [
        "core",
        "core.Ishchi",
        "core.Qiymetlendirme",
        "core.InkishafPlani",
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-lime",
    "navbar": "navbar-success navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "slate",
    "dark_mode_theme": "slate",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-outline-success",
    },
    "actions_sticky_top": False,
}

# ===================================================================
# TEMPLATES (ŞABLONLARIN KONFİQURASİYASI)
# ===================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.language_switcher_context",
                "core.context_processors.global_context",
                "core.context_processors.notification_context",
            ],
        },
    },
]

# ===================================================================
# CAPTCHA KONFİQURASİYASI
# ===================================================================

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# ===================================================================
# CACHE (MÜVƏQQƏTİ YADDAŞ)
# ===================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ===================================================================
# LOGGING (GÜNLÜK GÖZƏTİM SİSTEMİ)
# ===================================================================

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)  # Əgər qovluq yoxdursa, onu yaradır

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Logların formatını təyin edirik
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    # Logları hara yazacağımızı təyin edirik (handlerlər)
    "handlers": {
        # Konsola (terminala) çıxan loglar
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        # Fayla yazılan loglar
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "debug.log",  # Log faylının adı və yeri
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    # Hansı logları harada göstərəcəyimizi təyin edirik
    "loggers": {
        # Django-nun öz logları
        "django": {
            "handlers": ["console", "file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        # Bizim tətbiqin (və ya digərlərinin) logları
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}
# ===================================================================
# CELERY KONFİQURASİYASI
# ===================================================================

# Celery tətbiqi yalnız Redis mövcud olduqda işə salınır
# Əgər Redis mövcud deyilsə, e-poçt göndərmə sinxron işləyəcək
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TIME_LIMIT = 5 * 60  # Tapşırığın maksimum icra müddəti (5 dəqiqə)
CELERY_TASK_SOFT_TIME_LIMIT = 60  # Tapşırığın bitirilməsi üçün xəbərdarlıq (1 dəqiqə)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Production-da Celery-ni tam aktivləşdir
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"

# Celery worker konfiqurasiyası
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ROUTES = {
    'core.tasks.send_activation_email_task': {'queue': 'email'},
    'core.tasks.generate_report_task': {'queue': 'reports'},
}

# Celery logging
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# ===================================================================
# AUDIT LOGGING KONFİQURASİYASI
# ===================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'audit': {
            'format': '{asctime} - AUDIT - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/audit.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'audit',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'general_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/general.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'audit': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['general_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['general_file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Logs qovluğunu yaratmaq üçün
import os
if not os.path.exists('logs'):
    os.makedirs('logs')

# ===================================================================
# DJANGO REST FRAMEWORK KONFİQURASİYASI
# ===================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ===================================================================
# JWT (JSON Web Token) KONFİQURASİYASI
# ===================================================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ===================================================================
# API DOKUMENTASİYA KONFİQURASİYASI (drf-spectacular)
# ===================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Q360 Performance Management API',
    'DESCRIPTION': 'Q360 360 dərəcə performans idarəetmə sistemi üçün REST API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
}

# ===================================================================
# CORS KONFİQURASİYASI (Cross-Origin Resource Sharing)
# ===================================================================

# Development üçün bütün domainlərə icazə ver
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Production-da daha məhdud konfiqurasiya istifadə edin
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        # Production domainlərinizi burada qeyd edin
    ]
