"""
Django settings for pms project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-swoz&c-93ph^poydopinvp0)=pn0uph!*mb4*1c(_)j3myx50g'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'pharmacy.apps.PharmacyConfig',

    # Third-party
    'ckeditor',
    'ckeditor_uploader',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],   # you can add BASE_DIR / "templates" here later
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pms.wsgi.application'

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------------
STATIC_URL = '/static/'

# Folder for your development static files (optional)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Folder where collectstatic will put all files (MUST be defined!)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
CKEDITOR_UPLOAD_PATH = 'uploads/'
# ---------------------------------------------------------------------
# Other settings
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/redirect-dashboard/'
