"""Private direct-upload permissions, content validation and download regressions."""
import base64
import io
import json
import os
import time
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from PIL import Image

from Classroom.uploads import upload_storage_config
from .blob_storage import (BlobClient, BlobUnavailable, MAX_FILE_SIZE, PrivateBlobStorage,
                           VerifiedBlobFile, new_blob_path, sign_url)
from .blob_uploads import TICKET_SALT
from .models import Announcement, Doubt, Download, Profile, Question, Quiz, Resource, ResourceFile
from .services import ensure_legacy

BLOB_STORAGES = {
    'default': {'BACKEND': 'ClassApp.blob_storage.PrivateBlobStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
FILE_PATH = 'blob/123/'+'a'*32+'/AI notes.png'
SIGNED_GET = 'https://teststore.private.blob.vercel-storage.com/file?vercel-blob-signature=scoped'


def png_bytes():
    output = io.BytesIO()
    Image.new('RGB', (3, 3), 'blue').save(output, format='PNG')
    return output.getvalue()


class BlobProtocolTests(SimpleTestCase):
    def test_blob_configuration_and_auto_detection(self):
        for env in ({'BLOB_READ_WRITE_TOKEN': 'configured'},
                    {'BLOB_STORE_ID': 'store_test', 'VERCEL_OIDC_TOKEN': 'configured'}):
            self.assertEqual(upload_storage_config(False, env)[0], 'blob')
            self.assertEqual(upload_storage_config(False, dict(env, UPLOAD_STORAGE='blob'))[1]['BACKEND'],
                             'ClassApp.blob_storage.PrivateBlobStorage')
        with self.assertRaisesMessage(Exception, 'BLOB_READ_WRITE_TOKEN'):
            upload_storage_config(False, {'UPLOAD_STORAGE': 'blob'})
        self.assertEqual(upload_storage_config(True, {'UPLOAD_STORAGE': 'local',
                                                     'BLOB_READ_WRITE_TOKEN': 'configured'})[0], 'local')

    def test_signing_matches_official_javascript_sdk_contract(self):
        fixture = json.loads((Path(__file__).parent/'fixtures'/'blob_signing_contract.json').read_text())
        with patch('ClassApp.blob_storage.time.time', return_value=fixture['now']/1000):
            for case in fixture['cases']:
                result = sign_url(fixture['material'], FILE_PATH, case['operation'],
                                  content_type='image/png', maximum_size=MAX_FILE_SIZE)
                expected, actual = urlsplit(case['url']), urlsplit(result)
                self.assertEqual((actual.scheme, actual.netloc, actual.path),
                                 (expected.scheme, expected.netloc, expected.path))
                self.assertEqual(parse_qs(actual.query), parse_qs(expected.query))

    def test_signer_rejects_wrong_path_operation_and_expiry(self):
        scope = {'storeId': 'store_test', 'pathname': FILE_PATH,
                 'operations': ['get'], 'validUntil': int(time.time()*1000)+100000}
        def material():
            token = base64.urlsafe_b64encode(json.dumps(scope).encode()).decode().rstrip('=')+'.signature'
            return {'delegationToken': token, 'clientSigningToken': 'fixture-secret'}
        with self.assertRaises(BlobUnavailable):
            sign_url(material(), FILE_PATH+'wrong', 'get')
        with self.assertRaises(BlobUnavailable):
            sign_url(material(), FILE_PATH, 'put')
        scope['validUntil'] = 1
        with self.assertRaises(BlobUnavailable):
            sign_url(material(), FILE_PATH, 'get')

    def test_credential_resolution_never_exposes_token_in_errors(self):
        with patch.dict(os.environ, {'BLOB_READ_WRITE_TOKEN': 'vercel_blob_rw_teststore_secret',
                                    'BLOB_STORE_ID': '', 'VERCEL_OIDC_TOKEN': ''}):
            self.assertEqual(BlobClient()._auth_headers()['x-vercel-blob-store-id'], 'teststore')
        with patch.dict(os.environ, {'BLOB_READ_WRITE_TOKEN': 'private-invalid-secret',
                                    'BLOB_STORE_ID': '', 'VERCEL_OIDC_TOKEN': ''}):
            with self.assertRaisesMessage(BlobUnavailable, 'credentials are invalid') as error:
                BlobClient()._auth_headers()
            self.assertNotIn('private-invalid-secret', str(error.exception))

    def test_blob_path_fits_legacy_fields_and_keeps_extension(self):
        name = new_blob_path(12345678901234567890, '../'+'long name '*50+'.jpeg')
        self.assertLessEqual(len(name), 100)
        self.assertTrue(name.endswith('.jpeg'))
        self.assertNotIn('..', name)

    def test_storage_only_accepts_verified_direct_uploads(self):
        storage = PrivateBlobStorage()
        with self.assertRaises(BlobUnavailable):
            storage.save('file.png', SimpleUploadedFile('file.png', png_bytes()))
        file = VerifiedBlobFile(content=png_bytes(), filename='AI notes.png', pathname=FILE_PATH, content_type='image/png')
        self.assertEqual(storage.save('unused.png', file, max_length=100), FILE_PATH)
        with self.assertRaises(FileNotFoundError):
            storage.open('resources/old-local.png')

    def test_read_bounds_and_exact_size_are_enforced(self):
        for body, expected, succeeds in [(b'abc', 3, True), (b'abc', 4, False),
                                         (b'x'*(MAX_FILE_SIZE+1), None, False)]:
            with patch.object(BlobClient, 'url', return_value=SIGNED_GET), \
                    patch.object(BlobClient, '_open_request', return_value=io.BytesIO(body)):
                if succeeds:
                    self.assertEqual(BlobClient().read(FILE_PATH, expected_size=expected), body)
                else:
                    with self.assertRaises(BlobUnavailable):
                        BlobClient().read(FILE_PATH, expected_size=expected)


@override_settings(UPLOAD_STORAGE='blob', UPLOADS_ENABLED=True, STORAGES=BLOB_STORAGES)
class DirectBlobUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {}
        for role in ('student', 'faculty', 'director', 'other_student', 'other_faculty'):
            user = get_user_model().objects.create_user(role, password='TestingPassword#57')
            Profile.objects.filter(user=user).update(role=role.replace('other_', ''))
            ensure_legacy(user, role.replace('other_', ''))
            cls.users[role] = user

    def setUp(self):
        self.client.force_login(self.users['faculty'])

    def details(self, **kwargs):
        return dict({'path': '/resources/upload/', 'field': 'file', 'filename': 'AI notes.png',
                     'size': len(png_bytes())}, **kwargs)

    def start(self, **kwargs):
        return self.client.post('/uploads/blob/', data=json.dumps(self.details(**kwargs)), content_type='application/json')

    def ticket(self, *, user='faculty', view='resource_create', field='file', content=None, filename='AI notes.png'):
        content = png_bytes() if content is None else content
        return signing.dumps({'user': self.users[user].pk, 'view': view, 'field': field,
                              'pathname': FILE_PATH, 'filename': filename, 'size': len(content),
                              'content_type': 'image/png'}, salt=TICKET_SALT)

    def resource_data(self, **kwargs):
        return dict({'title': 'AI workflow', 'subject': 'AI', 'category': '__custom__',
                     'custom_category': 'Blob documents', 'description': 'Private upload',
                     '_blob_file': self.ticket()}, **kwargs)

    def test_upload_token_is_private_scoped_and_size_constrained(self):
        with patch.object(BlobClient, 'url', return_value='https://vercel.com/api/blob/?signed') as url:
            response = self.start()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url.call_args.kwargs, {'operation': 'put', 'content_type': 'image/png',
                                               'maximum_size': len(png_bytes())})
        data = response.json()
        self.assertNotIn('clientSigningToken', data)
        self.assertNotIn('BLOB_READ_WRITE_TOKEN', response.content.decode())
        self.assertIn('no-store', response['Cache-Control'])
        ticket = signing.loads(data['ticket'], salt=TICKET_SALT)
        self.assertEqual((ticket['user'], ticket['view'], ticket['field']),
                         (self.users['faculty'].pk, 'resource_create', 'file'))

    def test_upload_start_requires_login_csrf_and_correct_role(self):
        self.client.logout()
        self.assertEqual(self.start().status_code, 302)
        self.client.force_login(self.users['student'])
        self.assertEqual(self.start().status_code, 403)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.users['faculty'])
        self.assertEqual(client.post('/uploads/blob/', data=json.dumps(self.details()),
                                     content_type='application/json').status_code, 403)

    def test_invalid_files_destinations_and_size_are_rejected_before_storage(self):
        with patch.object(BlobClient, 'url') as url:
            for details in ({'filename': 'file.exe'}, {'filename': '../file.png'}, {'size': MAX_FILE_SIZE+1},
                            {'size': 0}, {'size': True}, {'path': 'https://evil.test/resources/upload/'},
                            {'field': 'document'}, {'path': '/accounts/manage/new/'}):
                with self.subTest(details=details):
                    self.assertIn(self.start(**details).status_code, (400, 403))
            url.assert_not_called()

    def test_all_supported_form_targets_and_legacy_aliases(self):
        with patch.object(BlobClient, 'url', return_value=SIGNED_GET):
            for role, path, field in [('director', '/resources/upload/', 'file'),
                                      ('faculty', '/announcements/create/', 'document'),
                                      ('faculty', '/announcements/add/', 'document'),
                                      ('student', '/doubts/new/', 'attachment'),
                                      ('student', '/doubt/', 'attachment'),
                                      ('faculty', '/quizzes/create/', 'questions-49-image'),
                                      ('faculty', '/create-quiz/', 'questions-0-image')]:
                self.client.force_login(self.users[role])
                self.assertEqual(self.start(path=path, field=field).status_code, 200)
            self.client.force_login(self.users['faculty'])
            self.assertEqual(self.start(path='/quizzes/create/', field='questions-50-image').status_code, 403)
            self.assertEqual(self.start(path='/quizzes/create/', field='questions-0-image', filename='text.txt').status_code, 400)

    def test_resource_upload_validates_bytes_and_saves_private_blob_path(self):
        with patch.object(BlobClient, 'read', return_value=png_bytes()) as read:
            response = self.client.post('/resources/upload/', self.resource_data())
        self.assertEqual(response.status_code, 302)
        resource = Resource.objects.get()
        self.assertEqual((resource.file.name, resource.original_name, resource.category),
                         (FILE_PATH, 'AI notes.png', 'Blob documents'))
        self.assertFalse(ResourceFile.objects.exists())
        read.assert_called_once_with(FILE_PATH, expected_size=len(png_bytes()))

    def test_full_30_mib_file_is_submitted_by_receipt_without_binary_request(self):
        content = b'A'*MAX_FILE_SIZE
        ticket = self.ticket(content=content, filename='large.txt')
        with patch.object(BlobClient, 'read', return_value=content):
            response = self.client.post('/resources/upload/', self.resource_data(_blob_file=ticket))
        self.assertEqual(response.status_code, 302)
        self.assertLess(int(response.wsgi_request.META['CONTENT_LENGTH']), 4096)
        self.assertEqual(Resource.objects.get().original_name, 'large.txt')

    def test_forged_expired_or_cross_user_receipts_do_not_read_or_save_files(self):
        with patch.object(BlobClient, 'read') as read:
            with patch('django.core.signing.time.time', return_value=time.time()-1900):
                expired = self.ticket()
            for ticket in (self.ticket()+'tampered', self.ticket(user='other_faculty'), expired,
                           self.ticket(view='announcement_create'), self.ticket(field='document')):
                response = self.client.post('/resources/upload/', self.resource_data(_blob_file=ticket))
                self.assertIn(response.status_code, (400, 403))
            read.assert_not_called()
        self.assertFalse(Resource.objects.exists())

    def test_duplicate_receipts_raw_uploads_and_invalid_content_are_rejected(self):
        with patch.object(BlobClient, 'read', return_value=b'not an image'):
            response = self.client.post('/resources/upload/', self.resource_data())
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Choose a valid PDF')
        self.assertFalse(Resource.objects.exists())
        self.assertEqual(self.client.post('/resources/upload/', self.resource_data(
            _blob_file=[self.ticket(), self.ticket()])).status_code, 400)
        data = self.resource_data()
        data['file'] = SimpleUploadedFile('test.png', png_bytes())
        self.assertEqual(self.client.post('/resources/upload/', data).status_code, 400)

    def test_storage_failures_are_retryable_and_do_not_create_records(self):
        with patch.object(BlobClient, 'url', side_effect=BlobUnavailable('private internal error')):
            response = self.start()
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('private internal error', response.content.decode())
        for error, status in [(BlobUnavailable('unavailable'), 503), (FileNotFoundError('missing'), 400)]:
            with patch.object(BlobClient, 'read', side_effect=error):
                self.assertEqual(self.client.post('/resources/upload/', self.resource_data()).status_code, status)
        self.assertFalse(Resource.objects.exists())

    def test_announcement_and_doubt_attachments_use_existing_permission_checks(self):
        faculty = self.users['faculty'].legacy_faculty
        with patch.object(BlobClient, 'read', return_value=png_bytes()):
            response = self.client.post('/announcements/create/', {
                'title': 'Private announcement', 'content': 'Students only', 'audience': 'student',
                '_blob_document': self.ticket(view='announcement_create', field='document')})
            self.assertEqual(response.status_code, 302)
            announcement = Announcement.objects.get()
            self.assertEqual(announcement.document.name, FILE_PATH)
            self.client.force_login(self.users['student'])
            response = self.client.post('/doubts/new/', {'faculty': faculty.pk, 'subject': 'AI',
                'doubt': 'Explain this diagram', '_blob_attachment': self.ticket(
                    user='student', view='doubt_create', field='attachment')})
            self.assertEqual(response.status_code, 302)
            doubt = Doubt.objects.get()
            self.assertEqual(doubt.attachment.name, FILE_PATH)
        with patch.object(BlobClient, 'url', return_value=SIGNED_GET):
            self.assertEqual(self.client.post(f'/attachments/doubt/{doubt.pk}/').status_code, 302)
            self.client.force_login(self.users['other_student'])
            self.assertEqual(self.client.post(f'/attachments/doubt/{doubt.pk}/').status_code, 404)
            self.client.force_login(self.users['other_faculty'])
            self.assertEqual(self.client.post(f'/attachments/announcement/{announcement.pk}/').status_code, 404)

    def test_blob_download_redirect_is_private_and_counted_once(self):
        resource = Resource.objects.create(title='Notes', subject='AI', category='notes',
            uploaded_by=self.users['faculty'], file=FILE_PATH, original_name='AI notes.png')
        with patch.object(BlobClient, 'url', return_value=SIGNED_GET):
            self.client.force_login(self.users['student'])
            response = self.client.post(f'/resources/{resource.pk}/download/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('download=1', response['Location'])
        self.assertIn('no-store', response['Cache-Control'])
        resource.refresh_from_db()
        self.assertEqual(resource.download_count, 1)
        self.assertEqual(Download.objects.count(), 1)
        with patch.object(BlobClient, 'url', side_effect=BlobUnavailable()):
            self.assertEqual(self.client.post(f'/resources/{resource.pk}/download/').status_code, 503)
        self.assertEqual(Download.objects.count(), 1)

    def test_old_database_backed_resource_still_downloads_after_switching_storage(self):
        resource = Resource.objects.create(title='Old notes', subject='AI', category='notes',
            uploaded_by=self.users['faculty'], file='resources/old.png', original_name='original.png')
        ResourceFile.objects.create(resource=resource, storage_name=resource.file.name, content=png_bytes())
        with patch.object(BlobClient, 'url') as url:
            response = self.client.post(f'/resources/{resource.pk}/download/')
            self.assertEqual(b''.join(response.streaming_content), png_bytes())
            url.assert_not_called()

    def test_quiz_images_validate_permissions_before_signing_download(self):
        quiz = Quiz.objects.create(title='Quiz', creator=self.users['faculty'], subject='AI',
            is_active=True, starts_at=timezone.now()-timedelta(hours=1), expiry_time=timezone.now()+timedelta(hours=1))
        question = Question.objects.create(quiz=quiz, text='Identify the workflow', image=FILE_PATH)
        with patch.object(BlobClient, 'url', return_value=SIGNED_GET) as url:
            self.client.force_login(self.users['other_faculty'])
            self.assertEqual(self.client.get(f'/question-images/{question.pk}/').status_code, 403)
            url.assert_not_called()
            self.client.force_login(self.users['student'])
            self.assertEqual(self.client.get(f'/question-images/{question.pk}/').status_code, 302)

    def test_quiz_creation_stores_a_verified_private_image(self):
        now = timezone.localtime()
        data = {'title': 'Blob quiz', 'subject': 'AI',
                'starts_at': (now-timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
                'expiry_time': (now+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
                'questions-TOTAL_FORMS': '1', 'questions-INITIAL_FORMS': '0',
                'questions-0-text': 'Identify this workflow', 'questions-0-option_count': '2',
                'questions-0-option_a': 'Correct', 'questions-0-option_b': 'Incorrect',
                'questions-0-correct': ['A'],
                '_blob_questions-0-image': self.ticket(view='quiz_create', field='questions-0-image')}
        with patch.object(BlobClient, 'read', return_value=png_bytes()):
            response = self.client.post('/quizzes/create/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.get().image.name, FILE_PATH)

    def test_total_direct_attachment_limit_is_checked_before_read(self):
        data = {}
        for index in range(2):
            field = f'questions-{index}-image'
            data['_blob_'+field] = self.ticket(view='quiz_create', field=field, content=b'x'*(17*1024*1024))
        with patch.object(BlobClient, 'read') as read:
            self.assertEqual(self.client.post('/quizzes/create/', data).status_code, 413)
            read.assert_not_called()
