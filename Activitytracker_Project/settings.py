"""
Django settings for Activitytracker project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from Activitytracker_Project import passwords
from config import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'o2gyhpz9aodq95f#*=jj#(sb@0c&ss&07+8-p3k&97mhqcx349'

# Check if we're on development or production
# Not the same as DEBUG since right now we're on DEBUG=True on production as well
PRODUCTION = os.path.isfile(os.path.join(BASE_DIR, 'production.txt'))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'activitytracker',
    'requests',
    'requests_oauthlib',
    'oauth2',
    'social.apps.django_app.default',
    'djangobower',
    'compressor',

    # comments app
    'django.contrib.sites',
    'django_comments',

    # Projects app - access to CloudTeams Projects & related functionality
    'ct_projects',

    # Profile wizard app - allows customers to quickly setup their profile
    'profile',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'activitytracker.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'Activitytracker_Project.urls'

WSGI_APPLICATION = 'Activitytracker_Project.wsgi.application'

LOGIN_URL = 'login'
#LOGIN_REDIRECT_URL = '/login'
#LOGIN_ERROR_URL = 'http://local.host:8000/activitytracker'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'activity_tracker_db',
        'USER': passwords.DB_USER,
        'PASSWORD': passwords.DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Activitytracker.app@gmail.com'
DEFAULT_TO_EMAIL = 'to email'
EMAIL_HOST_USER = 'Activitytracker.app@gmail.com'
EMAIL_HOST_PASSWORD = 'Activitytrackerpassword'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = False

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'activitytracker/static'
#STATIC_ROOT = '/home/user/aggelos/final/activity-tracker/activitytracker/static/'


# Files uploaded by users (e.g avatars)
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

# django-bower. Bower components dir
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'activitytracker/static/')

INSTALLED_FINDERS = {
    'djangobower.finders.BowerFinder'
}

# django-bower. Installed js-css.
BOWER_INSTALLED_APPS = (
    'jquery#2.1.4',
    'bootstrap#3',
    'jquery-tokenize#2.5.1',
    'datatables#1.10',
    'jquery-ui#1.11.4',
    'jqueryui-touch-punch',
    'clockpicker#0.0.7',
    'moment',
    'fullcalendar',
    'chosen',
    'bootstrap-chosen',
    'bootstrap-datepicker',
    'bootstrap-tokenfield',
    'datatables-responsive',
    'bootstrap-daterangepicker'

)

STATICFILES_FINDERS = (
    # Bower
    'djangobower.finders.BowerFinder',
    # static
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Compress and minify
COMPRESS_ENABLED = False
# COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']
#COMPRESS_CSS_FILTERS = ['compressor.filters.yuglify.YUglifyCSSFilter']
#COMPRESS_JS_FILTERS = ['compressor.filters.yuglify.YUglifyJSFilter']
# COMPRESS_OFFLINE = True
COMPRESS_ROOT = 'static'



AUTH_USER_MODEL = 'activitytracker.User'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',

            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.facebook.FacebookActivityOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.instagram.InstagramOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.runkeeper.RunKeeperOAuth2',
    'social.backends.youtube.YoutubeOAuth2',
    'social.backends.googlefit.GoogleFitOAuth2',
    'social.backends.gmail.GmailOAuth2',
    'social.backends.fitbit.FitbitOAuth',
    'social.backends.foursquare.FoursquareOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

if PRODUCTION:
    ANONYMIZER_URL = 'http://cloudteams.epu.ntua.gr:8000'
else:
    ANONYMIZER_URL = 'http://localhost:8000'

