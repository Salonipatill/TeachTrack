"""Exercise real browser workflows against a disposable Django test server."""
import io
import logging
import os
from pathlib import Path
import secrets
import sys
import tempfile
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.update(
    DJANGO_SETTINGS_MODULE='Classroom.settings',
    TEACHTRACK_ENV_FILE='.env.isolated-tests-unused',
    DATABASE_URL='sqlite:///:memory:', DEBUG='True',
    SECRET_KEY='disposable-browser-workflows-only', UPLOAD_STORAGE='local', GS_BUCKET_NAME='',
)
from django.conf import settings
settings.STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
import django
django.setup()
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.db import connections
from django.test.utils import get_runner
from django.utils import timezone
from ClassApp.models import (
    Complaint, Contact, Doubt, Faculty, Notification, Quiz, Rating, Resource, Submission,
)


class WorkflowBrowserTests(StaticLiveServerTestCase):
    host = '127.0.0.1'

    def test_complete_role_workflows(self):
        from PIL import Image
        from playwright.sync_api import sync_playwright
        password = 'Workflow#' + secrets.token_hex(16)
        os.environ['DEMO_PASSWORD'] = password
        call_command('seed_demo', stdout=io.StringIO())
        users = get_user_model()
        faculty = Faculty.objects.get(user__username='demo_faculty')
        checks = 0
        errors = []

        def check(condition, message):
            nonlocal checks
            self.assertTrue(condition, message)
            checks += 1

        def visit(page, path):
            response = page.goto(self.live_server_url + path)
            check(response.status == 200, f'HTTP page {path}')

        def submit(page, name='Save & continue'):
            page.get_by_role('button', name=name, exact=True).click()
            page.wait_for_load_state('networkidle')
            check(page.locator('main .errorlist').count() == 0, 'Form validation succeeded')

        # Playwright's sync driver runs an event loop; keep ORM reads on a
        # separate synchronous thread rather than disabling Django's async guard.
        with ThreadPoolExecutor(max_workers=1) as database_worker, sync_playwright() as playwright:
            def orm(action):
                return database_worker.submit(action).result()
            browser = playwright.chromium.launch(headless=True, channel='msedge')
            pages = {}
            try:
                for role in ('director', 'faculty', 'student'):
                    context = browser.new_context(accept_downloads=True, reduced_motion='reduce',
                                                  viewport={'width': 1440, 'height': 1000})
                    context.route('**/*', lambda route: route.continue_()
                                  if urlsplit(route.request.url).hostname in ('127.0.0.1', 'localhost')
                                  else route.abort())
                    page = context.new_page()
                    page.set_default_timeout(8000)
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    pages[role] = page
                    visit(page, '/accounts/login/')
                    page.locator('#id_username').fill('demo_' + role)
                    page.locator('#id_password').fill(password)
                    page.locator('.auth-card button.full').click()
                    page.wait_for_url('**/dashboard/')
                    check(page.locator('h1').count() == 1, f'{role} login')
                    for path in ('/resources/', '/quizzes/', '/submission-details/', '/announcements/',
                                 '/doubts/', '/complaints/', '/feedback/', '/notifications/', '/accounts/profile/'):
                        visit(page, path)

                director, teacher, student = (pages[role] for role in ('director', 'faculty', 'student'))
                visit(teacher, '/resources/upload/')
                teacher.locator('#id_title').fill('Workflow browser picture')
                teacher.locator('#id_subject').fill('Browser testing')
                teacher.locator('#id_category').select_option('__custom__')
                teacher.locator('#id_custom_category').fill('Browser manuals')
                image = io.BytesIO()
                Image.new('RGB', (8, 8), color='green').save(image, format='PNG')
                content = image.getvalue()
                teacher.locator('#id_file').set_input_files({
                    'name': 'browser-note.png', 'mimeType': 'image/png', 'buffer': content,
                })
                submit(teacher)
                resource = orm(lambda: Resource.objects.get(title='Workflow browser picture'))
                check(resource.category == 'Browser manuals', 'Custom category stored')
                check(orm(lambda: bytes(resource.stored_file.content)) == content, 'Database file copy stored')
                file_path = Path(resource.file.path).resolve()
                check(file_path.is_relative_to(Path(settings.MEDIA_ROOT).resolve()), 'Only test media is deleted')
                resource.file.storage.delete(resource.file.name)
                visit(student, '/resources/?category=Browser+manuals')
                card = student.locator('.resource-card').filter(has_text='Workflow browser picture')
                with student.expect_download() as downloaded:
                    card.get_by_role('button').click()
                download = downloaded.value
                check(download.suggested_filename == 'browser-note.png', 'Original image filename')
                check(Path(download.path()).read_bytes() == content, 'Image download without filesystem file')
                orm(resource.refresh_from_db)
                check(resource.download_count == 1, 'Download count updated')

                visit(teacher, '/quizzes/create/')
                teacher.locator('#id_title').fill('Workflow browser quiz')
                teacher.locator('#id_subject').fill('Browser testing')
                now = timezone.localtime()
                teacher.locator('#id_starts_at').fill((now - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'))
                teacher.locator('#id_expiry_time').fill((now + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'))
                first = teacher.locator('#question-forms .question-form').first
                first.get_by_role('button', name='Remove last option', exact=True).click()
                first.get_by_role('button', name='Remove last option', exact=True).click()
                first.locator('textarea[name$="-text"]').fill('Choose the first option')
                first.locator('input[name$="-option_a"]').fill('Correct first answer')
                first.locator('input[name$="-option_b"]').fill('Incorrect first answer')
                first.locator('input[name$="-correct"][value="A"]').check()
                teacher.get_by_role('button', name='+ Add question', exact=True).click()
                second = teacher.locator('#question-forms .question-form').nth(1)
                second.locator('textarea[name$="-text"]').fill('Choose both correct options')
                for key in 'abcd':
                    second.locator(f'input[name$="-option_{key}"]').fill('Second option ' + key)
                for key in 'AC':
                    second.locator(f'input[name$="-correct"][value="{key}"]').check()
                check(second.locator('input[name$="-is_multiple"]').is_checked(), 'Multiple answers enabled')
                submit(teacher, 'Create quiz')
                quiz = orm(lambda: Quiz.objects.get(title='Workflow browser quiz'))
                check(orm(quiz.questions.count) == 2, 'Quiz question forms saved')
                visit(student, f'/quizzes/{quiz.pk}/attempt/')
                student.locator('#id_roll_no').fill('BROWSER-001')
                student.locator('#id_course').fill('Computer Science')
                selected = orm(lambda: [(question.pk, list(question.options.filter(is_correct=True).values_list('pk', flat=True)))
                                        for question in quiz.questions.all()])
                for question_id, option_ids in selected:
                    for option_id in option_ids:
                        student.locator(f'input[name="q_{question_id}"][value="{option_id}"]').check()
                submit(student, 'Submit quiz')
                result = orm(lambda: Submission.objects.get(quiz=quiz, student__username='demo_student'))
                check(result.score == 2 and result.total == 2, 'Exact-set quiz scoring')
                visit(student, f'/quizzes/{quiz.pk}/attempt/')
                check('/result/' in student.url, 'Duplicate attempt prevented')

                visit(student, '/feedback/')
                student.locator('#id_faculty').select_option(str(faculty.pk))
                student.locator('#id_rating').select_option('5')
                student.locator('#id_comment').fill('Workflow browser feedback')
                submit(student, 'Save feedback')
                check(orm(lambda: Rating.objects.filter(comment='Workflow browser feedback', rating=5).exists()), 'Feedback saved')
                visit(student, '/doubts/new/')
                student.locator('#id_faculty').select_option(str(faculty.pk))
                student.locator('#id_subject').fill('Workflow browser doubt')
                student.locator('#id_doubt').fill('How does the browser download fallback work?')
                submit(student)
                doubt = orm(lambda: Doubt.objects.get(subject='Workflow browser doubt'))
                visit(teacher, f'/doubts/{doubt.pk}/answer/')
                teacher.locator('#id_answer').fill('A matching private database copy is used.')
                submit(teacher)
                orm(doubt.refresh_from_db)
                check(bool(doubt.answer), 'Assigned faculty answered doubt')

                visit(student, '/complaints/new/')
                student.locator('#id_faculty').select_option(str(faculty.pk))
                student.locator('#id_title').fill('Workflow browser complaint')
                student.locator('#id_body').fill('A disposable complaint for workflow testing.')
                submit(student)
                complaint = orm(lambda: Complaint.objects.get(title='Workflow browser complaint'))
                visit(teacher, f'/complaints/{complaint.pk}/')
                teacher.locator('#id_message').fill('Investigating the disposable issue.')
                submit(teacher, 'Post update')
                orm(complaint.refresh_from_db)
                check(complaint.status == 'in_progress', 'Faculty complaint reply')
                visit(director, f'/complaints/{complaint.pk}/')
                director.locator('#id_message').fill('Resolved during the browser test.')
                director.locator('#id_status').select_option('resolved')
                submit(director, 'Post update')
                orm(complaint.refresh_from_db)
                check(complaint.status == 'resolved' and orm(complaint.events.count) == 3, 'Complaint resolution/history')

                visit(director, '/announcements/create/')
                director.locator('#id_title').fill('Workflow browser announcement')
                director.locator('#id_content').fill('A disposable browser announcement.')
                director.locator('#id_audience').select_option('all')
                submit(director)
                visit(student, '/announcements/')
                check('Workflow browser announcement' in student.locator('main').inner_text(), 'Announcement audience')
                visit(director, '/notifications/send/')
                director.locator('#id_title').fill('Workflow browser notification')
                director.locator('#id_message').fill('A disposable notification.')
                director.locator('#id_audience').select_option('student')
                submit(director)
                check(orm(lambda: Notification.objects.filter(title='Workflow browser notification').count()) == 2, 'Notification audience')

                visit(director, '/accounts/manage/new/?role=faculty')
                for field, value in {
                    'username': 'workflow_teacher', 'first_name': 'Workflow Teacher',
                    'email': 'workflow-teacher@example.test', 'department': 'Computer Science',
                    'password1': password, 'password2': password,
                }.items():
                    director.locator('#id_' + field).fill(value)
                submit(director, 'Create account')
                created = orm(lambda: users.objects.select_related('profile').get(username='workflow_teacher'))
                check(created.profile.role == 'faculty', 'Director created faculty account')
                director.locator(f'form[action="/accounts/manage/{created.pk}/toggle/"] button').click()
                director.wait_for_load_state('networkidle')
                orm(created.refresh_from_db)
                check(not created.is_active, 'Director deactivated disposable faculty account')
                visit(director, '/reports/')
                for kind in ('resources', 'quizzes', 'feedback', 'complaints'):
                    with director.expect_download() as exported:
                        director.locator(f'a[href="/reports/{kind}/export/"]').click()
                    check(Path(exported.value.path()).stat().st_size > 0, f'{kind} CSV export')

                for role, page in pages.items():
                    visit(page, '/accounts/profile/')
                    page.locator('#id_first_name').fill('Updated ' + role)
                    submit(page, 'Save changes')
                    check(orm(lambda: users.objects.get(username='demo_' + role).first_name) == 'Updated ' + role, f'{role} profile edit')
                    page.set_viewport_size({'width': 390, 'height': 844})
                    for path in ('/dashboard/', '/resources/', '/quizzes/', '/doubts/', '/complaints/'):
                        visit(page, path)
                        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{role} mobile {path}')
                    page.locator('.menu-toggle').click()
                    check(page.locator('.sidebar').is_visible(), f'{role} mobile navigation')
                    page.keyboard.press('Escape')
                    check(not page.locator('.sidebar').is_visible(), f'{role} Escape closes navigation')

                guest = browser.new_context(reduced_motion='reduce')
                guest.route('**/*', lambda route: route.continue_()
                            if urlsplit(route.request.url).hostname in ('127.0.0.1', 'localhost') else route.abort())
                page = guest.new_page()
                page.set_default_timeout(8000)
                visit(page, '/contact/')
                for field, value in {'name': 'Browser Visitor', 'email': 'visitor@example.test',
                                     'title': 'Workflow browser contact', 'message': 'Disposable contact test.'}.items():
                    page.locator('#id_' + field).fill(value)
                submit(page, 'Send message')
                check(orm(lambda: Contact.objects.filter(title='Workflow browser contact').exists()), 'Public contact saved')
                visit(page, '/accounts/register/')
                for field, value in {
                    'username': 'workflow_student', 'first_name': 'Workflow Student',
                    'email': 'workflow-student@example.test', 'enrollment': 'WF-NEW-001',
                    'department': 'Computer Science', 'password1': password, 'password2': password,
                }.items():
                    page.locator('#id_' + field).fill(value)
                submit(page)
                check(orm(lambda: users.objects.get(username='workflow_student').profile.role) == 'student', 'Public student registration')
                visit(page, '/accounts/password/change/')
                changed_password = 'Changed#' + secrets.token_hex(16)
                for field, value in {'old_password': password, 'new_password1': changed_password,
                                     'new_password2': changed_password}.items():
                    page.locator('#id_' + field).fill(value)
                submit(page)
                check('/password/change/done/' in page.url, 'Password changed')
                page.get_by_role('button', name='Sign out', exact=True).click()
                page.wait_for_url('**/accounts/login/')
                page.locator('#id_username').fill('workflow_student')
                page.locator('#id_password').fill(changed_password)
                page.locator('.auth-card button.full').click()
                page.wait_for_url('**/dashboard/')
                check('/dashboard/' in page.url, 'Changed password login works')
                check(not errors, 'No JavaScript errors: ' + '; '.join(errors))
            except Exception:
                if pages:
                    next(reversed(pages.values())).screenshot(path=str(ROOT / '.pytest_cache/workflow-failure.png'))
                raise
            finally:
                browser.close()
                database_worker.submit(connections.close_all).result()
        print(f'Real HTTP role workflow checks passed: {checks} assertions. Disposable SQLite/media only.', flush=True)


def main():
    cache = (ROOT / '.pytest_cache').resolve()
    cache.mkdir(exist_ok=True)
    assert cache.is_relative_to(ROOT.resolve())
    logging.getLogger('django.request').setLevel(logging.CRITICAL)
    with tempfile.TemporaryDirectory(prefix='workflow-ui-', dir=cache) as folder:
        target = Path(folder).resolve()
        assert target.is_relative_to(cache)
        settings.MEDIA_ROOT = target / 'media'
        try:
            failures = get_runner(settings)(verbosity=1, interactive=False, debug_mode=True).run_tests(['__main__'])
        finally:
            connections.close_all()
            assert target.resolve().is_relative_to(cache)
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
