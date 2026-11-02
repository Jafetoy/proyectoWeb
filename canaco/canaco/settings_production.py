"""Fail-closed production settings for the Azure VM deployment."""

import os
import re

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403


def required_env(name):
    value = os.environ.get(name, '').strip()
    if not value or value.startswith('<') or value.startswith('CHANGE_ME'):
        raise ImproperlyConfigured(f'{name} must contain a production value.')
    return value


DEBUG = False
SECRET_KEY = required_env('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be a new random secret of at least 50 characters.')

HOST = required_env('DJANGO_HOST')
if not re.fullmatch(r'(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}', HOST):
    raise ImproperlyConfigured('DJANGO_HOST must be a DNS hostname without a scheme, port or path.')
ALLOWED_HOSTS = [HOST]
CSRF_TRUSTED_ORIGINS = [f'https://{HOST}']
STATIC_URL = '/static/'
STATIC_ROOT = Path('/srv/static')
MEDIA_ROOT = Path('/srv/media')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# Enable gradually only after HTTPS and renewal have been verified.
SECURE_HSTS_SECONDS = 0

# Replace rather than mutate the dictionary inherited from development settings.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': required_env('DB_NAME'),
        'USER': required_env('DB_USER'),
        'PASSWORD': required_env('DB_PASSWORD'),
        'HOST': required_env('DB_HOST'),
        'PORT': required_env('DB_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}
