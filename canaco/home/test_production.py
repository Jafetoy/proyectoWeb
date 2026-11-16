"""Production configuration checks without a database or Docker daemon."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


DJANGO_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = DJANGO_ROOT.parent


class EnvironmentConfigurationTests(unittest.TestCase):
    def test_compose_services_do_not_receive_the_entire_shared_env_file(self):
        compose_files = (
            REPOSITORY_ROOT / 'docker-compose.yml',
            DJANGO_ROOT / 'compose.yaml',
        )

        for compose_file in compose_files:
            with self.subTest(compose_file=compose_file.name):
                contents = compose_file.read_text(encoding='utf-8')
                self.assertNotIn('env_file:', contents)

    def test_compose_files_do_not_embed_environment_values(self):
        compose_files = (
            REPOSITORY_ROOT / 'docker-compose.yml',
            DJANGO_ROOT / 'compose.yaml',
        )
        keys = (
            'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
            'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD',
            'MYSQL_ROOT_PASSWORD',
        )
        assignment = re.compile(
            rf'^\s*(?:-\s*)?(?:{"|".join(keys)})\s*[:=]\s*(?!\${{)[^#\s]+',
            re.MULTILINE,
        )

        for compose_file in compose_files:
            with self.subTest(compose_file=compose_file.name):
                contents = compose_file.read_text(encoding='utf-8')
                self.assertIsNone(
                    assignment.search(contents),
                    f'{compose_file} contains a literal environment value',
                )

    def test_development_settings_load_explicit_env_file_without_overrides(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / '.env'
            env_file.write_text(
                '\n'.join((
                    'DJANGO_SECRET_KEY=file-secret-key',
                    'MYSQL_DATABASE=file_database',
                    'MYSQL_USER=file_user',
                    'MYSQL_PASSWORD=file_password',
                    'DB_HOST=file_host',
                    'DB_PORT=3307',
                )),
                encoding='utf-8',
            )
            env = {
                key: value for key, value in os.environ.items()
                if not key.startswith(('DJANGO_', 'DB_', 'MYSQL_'))
            }
            env.update({
                'PYTHONDONTWRITEBYTECODE': '1',
                'CANACO_ENV_FILE': str(env_file),
                'DJANGO_SECRET_KEY': 'process-secret-key',
            })
            script = '''
import json
from canaco import settings as s
print(json.dumps({
    'secret': s.SECRET_KEY,
    'name': s.DATABASES['default']['NAME'],
    'user': s.DATABASES['default']['USER'],
    'password': s.DATABASES['default']['PASSWORD'],
    'host': s.DATABASES['default']['HOST'],
    'port': s.DATABASES['default']['PORT'],
}))
'''
            result = subprocess.run(
                [sys.executable, '-c', script],
                cwd=DJANGO_ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertEqual(config['secret'], 'process-secret-key')
        self.assertEqual(config['name'], 'file_database')
        self.assertEqual(config['user'], 'file_user')
        self.assertEqual(config['password'], 'file_password')
        self.assertEqual(config['host'], 'file_host')
        self.assertEqual(config['port'], '3307')


class ProductionSettingsTests(unittest.TestCase):
    def load_settings(self, missing=None, overrides=None):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('DJANGO_', 'DB_', 'MYSQL_', 'CANACO_'))}
        env.update({
            'PYTHONDONTWRITEBYTECODE': '1',
            'CANACO_ENV_FILE': str(DJANGO_ROOT / '.env.test-missing'),
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
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('DJANGO_', 'DB_', 'MYSQL_', 'CANACO_'))}
        env.update({
            'PYTHONDONTWRITEBYTECODE': '1',
            'CANACO_ENV_FILE': str(DJANGO_ROOT / '.env.test-missing'),
            'DJANGO_SECRET_KEY': 'test-only-development-secret',
        })
        result = subprocess.run(
            [sys.executable, '-c',
             'from canaco import settings; assert settings.DEBUG is True'],
            cwd=DJANGO_ROOT, text=True, capture_output=True,
            env=env,
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
