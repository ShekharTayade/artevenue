"""
Django settings for estore project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from decouple import config, Csv
import dj_database_url

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
EXEC_ENV = config('EXEC_ENV', default='DEV')
SMS_API_KEY = config('SMS_API_KEY', default='')

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fgn-iuumkx7nu-yymz(n_kecklq9+v!gmu%xt!j08h$0o*1crb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SITE_ID = 2
TEMPLATE_DEBUG = True

# Store ID
STORE_ID = 1


# Application definition

INSTALLED_APPS = [
	'artevenue.apps.ArtevenueConfig',
	'artist.apps.ArtistConfig',
	'blog.apps.BlogConfig',
	'channelsales.apps.ChannelsalesConfig',
	'review.apps.ReviewConfig',	
	'gallerywalls.apps.GallerywallsConfig',	
	'returns.apps.ReturnsConfig',
	'spinwheel.apps.SpinwheelConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'django.contrib.sites',
	'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.amazon',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.instagram',	
    'allauth.socialaccount.providers.twitter',
	'rest_framework',
	'rest_framework.authtoken',
	'django.contrib.sitemaps',
	'indian_numbers',
	'webmaster_verification',
	'django.contrib.redirects',
	]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

ROOT_URLCONF = 'estore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                 'django.template.context_processors.request',
				'django.template.context_processors.media',
           ],
        },
    },
]

WSGI_APPLICATION = 'estore.wsgi.application'


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
		'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework.authentication.TokenAuthentication',  # <-- And here
	],
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

USE_L10N = False
LANGUAGE_CODE = 'en-IN'
USE_TZ = True
TIME_ZONE = 'Asia/Calcutta'
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = (3, 2, 0)


ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_UNIQUE_EMAIL = True

#ACCOUNT_SIGNUP_FORM_CLASS = 'NextSteps.forms.SignUpForm'

SOCIALACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_REQUIRED
#SOCIALACCOUNT_AUTO_SIGNUP = False

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'js_sdk',
        'SCOPE': ['email', 'public_profile', 'user_friends'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        #'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.8',
    },
    
    
 'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
        
}


# Authentication Backends added for social media
AUTHENTICATION_BACKENDS = (

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

    'django.contrib.auth.backends.ModelBackend',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIR = [
    os.path.join(BASE_DIR, 'static'),
]
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

LOGOUT_REDIRECT_URL = 'index'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_URL = 'logout'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
LOGIN_URL = 'login'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# Cookie expiry in 5 days
SESSION_COOKIE_AGE = 432000

SOCIAL_AUTH_FACEBOOK_KEY = '2449878791952932'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = '890a83fd34bca4ddcd81842203ad16ad'  # App Secret

SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=80, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = 'support@artevenue.com'
EMAIL_SUBJECT_PREFIX = 'ArteVenue.com: '

MEDIA_URL = ('/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MOULDING_ROOT = os.path.join(BASE_DIR, 'artevenue/static/img/')
TMP_FILES = os.path.join(BASE_DIR, 'artevenue/static/tmp/')
CSS_FILES = os.path.join(BASE_DIR, 'artevenue/static/css/')
VENDOR_FILES = os.path.join(BASE_DIR, 'artevenue/static/vendor/')
EGIFT_DESIGNS = os.path.join(BASE_DIR, 'artevenue/static/img/')

GOOGLE_RECAPTCHA_SECRET_KEY = '6Le2ZqAUAAAAALbzG6uSjImGZ2hHY_B6r_Cug74i'

WEBMASTER_VERIFICATION = {
    'bing': 'C0A40BC9E7C942FC76951D60DC9355A9',
    'google': '<google verification code>',
    'majestic': '<majestic verification code>',
    'yandex': '<yandex verification code>',
    'alexa': '<alexa verification code>',
}

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True
TINYMCE_EXTRA_MEDIA = {
    'css': {
        'all': [
            ...
        ],
    },
    'js': [
        ...
    ],
}