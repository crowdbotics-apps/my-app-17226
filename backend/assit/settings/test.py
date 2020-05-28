from .base import *  # noqa

SECRET_KEY = config('SECRET_KEY', 'test')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': base_dir_join('db.sqlite3'),
    }
}

# Speed up password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
