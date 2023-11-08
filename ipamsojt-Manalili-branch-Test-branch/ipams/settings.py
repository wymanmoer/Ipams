import os
from datetime import timedelta
# import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or '6Ld-guEbAAAAANAgbmQI2Ph6knhKsOglaOEEuyp3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'accounts.User'

LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Application definition

INSTALLED_APPS = [
    'accounts',
    'records',
    'notifications',
    "crispy_forms",
    'crispy_bootstrap4',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'django_extensions',
    'axes',
    # 'channels',
    "sslserver",
    "debug_toolbar",
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'django_auto_logout.middleware.auto_logout',
]

ROOT_URLCONF = 'ipams.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'ipams/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # client-side script to redirect the user to the login page immediately after the idle-time expires
                'django_auto_logout.context_processors.auto_logout_client',
                'notifications.context_processors.notificationCount',
            ],
        },
    },
]

WSGI_APPLICATION = 'ipams.wsgi.application'
# ASGI_APPLICATION = 'ipams.asgi.application'
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ipamsdjango',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'my.ini'),
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'mydatabase',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_L10N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]
# if DEBUG:
#   STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# else:
#   STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = '/'

# Activate Django-Heroku.
# django_heroku.settings(config=locals())

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 10 # 30 minutes expiry when inactive
SESSION_SAVE_EVERY_REQUEST = True

# DJANGO AUTO LOGOUT
AUTO_LOGOUT = {
    'IDLE_TIME': 1800, #logout a user if there are no requests for 30 mins
    'MESSAGE': 'You have been idle for too long. Please login again to continue.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}

# limit login attempts
AXES_FAILURE_LIMIT = 3
AXES_ENABLE_ADMIN = True #show axes tables on django admin
AXES_ONLY_USER_FAILURES = True #only lock based on username if limit exceeded
AXES_LOCKOUT_URL = '/lockout'
AXES_RESET_ON_SUCCESS = True

# recaptcha
GOOGLE_RECAPTCHA_SECRET_KEY = '6Lckj-EbAAAAAEKoK1quZBP62i5NY57NlqDko-kL'
GOOGLE_RECAPTCHA_SITE_KEY = '6Lckj-EbAAAAAHKCPuWWZCsDMD48xYL8XYc0OPOt'
TEST_FORM = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

EMAIL_HOST_USER = 'johnbenedictdamalers69@gmail.com'
EMAIL_HOST_PASSWORD = 'epixcocpelxvnffr'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#EMAIL_HOST_USER = 'ipamsdevteam22@gmail.com'
#EMAIL_HOST_PASSWORD = 'fxmdxdbactlknwia'
#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Channels
# ASGI_APPLICATION = 'ipams.asgi.application'
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }


CSRF_TRUSTED_ORIGINS = ['https://*.ap.ngrok.io/']

INTERNAL_IPS = ['127.0.0.1', ]

X_FRAME_OPTIONS = 'SAMEORIGIN'

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

MIGRATION_MODULES = {'accounts': 'accounts.disable_migrations',
                    'records': 'records.disable_migrations',
                    'notifications': 'notifications.disable_migrations',
                    }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}