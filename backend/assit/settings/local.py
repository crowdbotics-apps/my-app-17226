import os
from .base import *  # noqa


DEBUG = True

SECRET_KEY = config('SECRET_KEY')

AUTH_PASSWORD_VALIDATORS = []  # allow easy passwords only on local

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_ROOT = base_dir_join('staticfiles')
STATIC_URL = '/static/'
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Email
INSTALLED_APPS += ('naomi',)
EMAIL_BACKEND = 'naomi.mail.backends.naomi.NaomiBackend'
EMAIL_FILE_PATH = base_dir_join('tmp_email')
