"""Production configuration checks without a database or Docker daemon."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


DJANGO_ROOT = Path(__file__).resolve().parents[1]


class ProductionSettingsTests(unittest.TestCase):
    def load_settings(self, missing=None, overrides=None):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('DJANGO_', 'DB_'))}
        env.update({
            'PYTHONDONTWRITEBYTECODE': '1',
            'DJANGO_HOST': 'news.example.com',
            'DJANGO_SECRET_KEY': 'test-only-' + 'a' * 64,
            'DB_NAME': 'test_db', 'DB_USER': 'test_user',
            'DB_PASSWORD': 'test-password', 'DB_HOST': 'db', 'DB_PORT': '3306',
        })
        if missing:
            env.pop(missing)
        env.update(overrides or {})
        script = '''
import json
from canaco import settings_production as s
print(json.dumps({
    'debug': s.DEBUG, 'hosts': s.ALLOWED_HOSTS,
    'origins': s.CSRF_TRUSTED_ORIGINS,
    'redirect': s.SECURE_SSL_REDIRECT,
    'cookies': [s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE],
    'proxy': s.SECURE_PROXY_SSL_HEADER,
    'static': s.STATIC_ROOT.as_posix(), 'media': s.MEDIA_ROOT.as_posix(),
    'db_host': s.DATABASES['default']['HOST'],
    'hsts_seconds': s.SECURE_HSTS_SECONDS,
}))
'''
        return subprocess.run([sys.executable, '-c', script], cwd=DJANGO_ROOT,
                              env=env, text=True, capture_output=True)

    def test_production_requires_explicit_secrets_and_database(self):
        for name in ('DJANGO_SECRET_KEY', 'DJANGO_HOST', 'DB_NAME', 'DB_USER',
                     'DB_PASSWORD', 'DB_HOST', 'DB_PORT'):
            with self.subTest(name=name):
                result = self.load_settings(missing=name)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(name, result.stderr)

    def test_production_enforces_https_and_separate_storage(self):
        result = self.load_settings()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertFalse(config['debug'])
        self.assertEqual(config['hosts'], ['news.example.com'])
        self.assertEqual(config['origins'], ['https://news.example.com'])
        self.assertTrue(config['redirect'])
        self.assertEqual(config['cookies'], [True, True])
        self.assertEqual(config['proxy'], ['HTTP_X_FORWARDED_PROTO', 'https'])
        self.assertEqual(config['static'], '/srv/static')
        self.assertEqual(config['media'], '/srv/media')
        self.assertEqual(config['db_host'], 'db')
        self.assertEqual(config['hsts_seconds'], 0)

    def test_development_settings_still_work_without_production_environment(self):
        result = subprocess.run(
            [sys.executable, '-c',
             'from canaco import settings; assert settings.DEBUG is True'],
            cwd=DJANGO_ROOT, text=True, capture_output=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_placeholder_secrets_and_untrusted_hosts(self):
        for name, value in (
            ('DJANGO_SECRET_KEY', 'CHANGE_ME_REPLACE_THIS'),
            ('DJANGO_SECRET_KEY', 'short'),
            ('DJANGO_HOST', '*'),
            ('DJANGO_HOST', 'https://news.example.com'),
            ('DB_PASSWORD', ''),
            ('DB_PASSWORD', '<GENERATE_SECRET>'),
        ):
            with self.subTest(name=name, value=value):
                result = self.load_settings(overrides={name: value})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(name, result.stderr)


if __name__ == '__main__':
    unittest.main()
