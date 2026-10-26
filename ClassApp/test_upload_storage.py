from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from Classroom.uploads import upload_storage_config


class UploadStorageConfigurationTests(SimpleTestCase):
    def test_local_storage_does_not_require_debug_or_cloud(self):
        for debug in (True, False):
            mode, backend = upload_storage_config(debug, {'UPLOAD_STORAGE': 'local'})
            self.assertEqual(mode, 'local')
            self.assertEqual(backend['BACKEND'], 'django.core.files.storage.FileSystemStorage')

    def test_explicit_local_mode_ignores_cloud_bucket(self):
        mode, backend = upload_storage_config(False, {
            'UPLOAD_STORAGE': 'local', 'GS_BUCKET_NAME': 'unused-bucket',
        })
        self.assertEqual(mode, 'local')
        self.assertNotIn('OPTIONS', backend)

    def test_auto_keeps_existing_development_and_hosted_defaults(self):
        for debug, env, expected in [
            (True, {}, 'local'),
            (False, {}, 'disabled'),
            (False, {'GS_BUCKET_NAME': 'private-notes'}, 'gcs'),
        ]:
            with self.subTest(debug=debug, env=env):
                self.assertEqual(upload_storage_config(debug, env)[0], expected)

    def test_gcs_mode_requires_bucket_and_keeps_private_files(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'GS_BUCKET_NAME'):
            upload_storage_config(True, {'UPLOAD_STORAGE': 'gcs'})
        mode, backend = upload_storage_config(False, {
            'UPLOAD_STORAGE': 'gcs', 'GS_BUCKET_NAME': 'private-notes',
        })
        self.assertEqual(mode, 'gcs')
        self.assertIsNone(backend['OPTIONS']['default_acl'])
        self.assertTrue(backend['OPTIONS']['querystring_auth'])

    def test_disabled_mode_can_override_development_or_cloud(self):
        mode, backend = upload_storage_config(True, {
            'UPLOAD_STORAGE': 'disabled', 'GS_BUCKET_NAME': 'unused-bucket',
        })
        self.assertEqual(mode, 'disabled')
        self.assertEqual(backend['BACKEND'], 'ClassApp.storage.DisabledUploadStorage')

    def test_invalid_mode_fails_at_startup(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'UPLOAD_STORAGE'):
            upload_storage_config(True, {'UPLOAD_STORAGE': 'unknown'})
