"""Real Django/CSRF/browser direct uploads with a synthetic offline Blob service.

This checks browser integration, not Vercel credentials or live Blob availability.
Run with the project Python; optional Playwright and installed Edge are required.
"""
import logging
import secrets
import tempfile
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.parse import quote, unquote, urlsplit

# Reuse the workflow runner's forced isolated SQLite environment. No .env or
# existing database is loaded, and no real storage token is required.
from check_workflows_ui import ROOT
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import connections
from django.test import override_settings
from django.test.utils import get_runner
from ClassApp.models import Profile, Resource
from ClassApp.services import ensure_legacy
from ClassApp.test_blob_storage import BLOB_STORAGES, png_bytes


@override_settings(UPLOAD_STORAGE='blob', UPLOADS_ENABLED=True, STORAGES=BLOB_STORAGES)
class BlobBrowserTests(StaticLiveServerTestCase):
    host = '127.0.0.1'

    def test_private_direct_upload_browser_workflow(self):
        from playwright.sync_api import sync_playwright
        password = 'BlobWorkflow#'+secrets.token_hex(16)
        user = get_user_model().objects.create_user('demo_faculty', password=password)
        Profile.objects.filter(user=user).update(role='faculty')
        ensure_legacy(user, 'faculty')
        objects, sizes, errors, transfers = {}, [], [], []
        fail_next = [False]
        checks = 0

        class StorageHandler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send(self, status, body=b''):
                self.send_response(status)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'PUT, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'content-type, x-vercel-blob-access')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Content-Type', 'application/octet-stream')
                if self.command == 'GET':
                    self.send_header('Content-Disposition', 'attachment; filename="download.txt"')
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):
                self.send(204)

            def do_PUT(self):
                if self.headers.get('x-vercel-blob-access') != 'private':
                    return self.send(400)
                name = unquote(urlsplit(self.path).path.lstrip('/'))
                content = self.rfile.read(int(self.headers['Content-Length']))
                transfers.append(('PUT', name, len(content)))
                if fail_next[0]:
                    fail_next[0] = False
                    return self.send(503)
                objects[name] = content
                self.send(200, b'{}')

            def do_GET(self):
                name = unquote(urlsplit(self.path).path.lstrip('/'))
                self.send(200, objects[name])

        storage_server = ThreadingHTTPServer(('127.0.0.1', 0), StorageHandler)
        storage_thread = Thread(target=storage_server.serve_forever, daemon=True)
        storage_thread.start()

        def check(condition, message):
            nonlocal checks
            self.assertTrue(condition, message)
            checks += 1

        def storage_url(client, name, **kwargs):
            return f'http://127.0.0.1:{storage_server.server_port}/'+quote(name, safe='/')+'?signature=synthetic'

        def storage_read(client, name, **kwargs):
            content = objects[name]
            self.assertEqual(len(content), kwargs['expected_size'])
            return content

        def route_request(route):
            request = route.request
            parsed = urlsplit(request.url)
            if parsed.hostname in ('127.0.0.1', 'localhost'):
                if request.method == 'POST':
                    sizes.append(len(request.post_data_buffer or b''))
                return route.continue_()
            return route.abort()

        with patch('ClassApp.blob_storage.BlobClient.url', storage_url), \
                patch('ClassApp.blob_storage.BlobClient.read', storage_read), \
                ThreadPoolExecutor(max_workers=1) as worker, sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, channel='msedge')
            try:
                page = browser.new_page(accept_downloads=True, reduced_motion='reduce')
                page.set_default_timeout(15000)
                page.context.route('**/*', route_request)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: transfers.append(('failed', urlsplit(request.url).path, request.failure)))
                page.goto(self.live_server_url+'/accounts/login/')
                page.locator('#id_username').fill('demo_faculty')
                page.locator('#id_password').fill(password)
                page.locator('.auth-card button.full').click()
                page.wait_for_url('**/dashboard/')
                check(True, 'Faculty signed in')
                for filename, body in [('Workflow.png', png_bytes()), ('Large notes.txt', b'A'*(30*1024*1024))]:
                    page.goto(self.live_server_url+'/resources/upload/')
                    page.locator('#id_title').fill(filename)
                    page.locator('#id_subject').fill('Blob browser check')
                    local_file = settings.BLOB_TEST_FILE_ROOT / filename
                    local_file.write_bytes(body)
                    page.locator('#id_file').set_input_files(str(local_file), timeout=60000)
                    if filename.endswith('.png'):
                        fail_next[0] = True
                        page.get_by_role('button', name='Save & continue', exact=True).click()
                        page.get_by_role('status').filter(has_text='The upload failed').wait_for()
                        check(page.locator('#id_file').is_enabled(), 'Failed upload can retry selected file')
                        check(page.get_by_role('button', name='Save & continue', exact=True).is_enabled(), 'Retry button restored')
                    page.get_by_role('button', name='Save & continue', exact=True).click()
                    page.wait_for_url('**/resources/', timeout=45000)
                    check(page.locator('.errorlist').count() == 0, 'File saved through real form validation')
                    item = worker.submit(lambda: Resource.objects.get(title=filename)).result()
                    check(item.file.name in objects, 'Private object path stored')
                    check(objects[item.file.name] == body, 'Direct upload preserves exact bytes')
                    try:
                        with page.expect_download() as pending:
                            page.locator(f'form[action="/resources/{item.pk}/download/"] button').click()
                    except Exception as error:
                        raise AssertionError(f'Download failed; synthetic transfer log: {transfers}') from error
                    download = pending.value
                    check(Path(download.path()).read_bytes() == body, 'Authenticated redirect downloads exact file')
                    count = worker.submit(lambda: Resource.objects.get(pk=item.pk).download_count).result()
                    check(count == 1, 'Download counted once')
                check(max(sizes) < 4096, 'No binary bytes pass through application requests, including 30 MiB file')
                check(len(objects) == 2, 'Retry did not save duplicate files')
                check(not errors, 'No browser JavaScript errors: '+'; '.join(errors))
            finally:
                browser.close()
                worker.submit(connections.close_all).result()
                storage_server.shutdown()
                storage_server.server_close()
                storage_thread.join(timeout=5)
        print(f'Private Blob browser workflow passed: {checks} assertions, including 30 MiB direct upload and download. Synthetic storage only.', flush=True)


if __name__ == '__main__':
    logging.getLogger('django.request').setLevel(logging.CRITICAL)
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
    cache = (ROOT / '.pytest_cache').resolve()
    cache.mkdir(exist_ok=True)
    assert cache.is_relative_to(ROOT.resolve())
    with tempfile.TemporaryDirectory(prefix='blob-browser-', dir=cache) as folder:
        target = Path(folder).resolve()
        assert target.is_relative_to(cache)
        settings.BLOB_TEST_FILE_ROOT = target
        try:
            failures = get_runner(settings)(verbosity=1, interactive=False, debug_mode=True).run_tests(['__main__'])
        finally:
            connections.close_all()
            assert target.resolve().is_relative_to(cache)
    raise SystemExit(bool(failures))
