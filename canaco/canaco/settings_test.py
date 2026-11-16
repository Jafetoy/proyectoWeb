"""Isolated settings for the automated test suite."""

import os
import secrets

os.environ.setdefault('DJANGO_SECRET_KEY', secrets.token_urlsafe(50))

from .settings import *  # noqa: F403


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
