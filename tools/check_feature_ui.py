"""Check current templates and JavaScript offline, without a running app or database."""
from argparse import ArgumentParser
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit, unquote


ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--browser-executable', help='Optional installed Chromium/Edge executable.')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    os.environ.update(
        DJANGO_SETTINGS_MODULE='Classroom.settings', DEBUG='True',
        DATABASE_URL='sqlite:///:memory:', SECRET_KEY='offline-ui-check-only',
        UPLOAD_STORAGE='local', GS_BUCKET_NAME='',
    )
    from django.conf import settings
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
    import django
    django.setup()
    from django.template.loader import render_to_string
    from ClassApp.forms import ContactForm, QuizForm, QuestionFormSet, ResourceForm
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.error('Install the optional browser dependency: python -m pip install playwright')

    user = SimpleNamespace(
        is_authenticated=True, username='offline-faculty', first_name='Faculty',
        profile=SimpleNamespace(get_role_display='Faculty'),
    )
    context = {'user': user, 'role': 'faculty', 'uploads_enabled': True, 'unread_count': 0,
               'csrf_token': 'offline-ui-check-only'}
    pages = {}
    for path, template, kind, extra in [
        ('/', 'index.html', 'home', {}),
        ('/campus-life/', 'campus_life.html', 'campus', {}),
        ('/contact/', 'contact.html', 'contact', {'form': ContactForm()}),
        ('/dashboard/', 'dashboard.html', '', {}),
        ('/quizzes/create/', 'quiz_create.html', '', {
            'form': QuizForm(), 'formset': QuestionFormSet(prefix='questions'),
        }),
        ('/resources/upload/', 'form.html', '', {
            'title': 'Upload a resource',
            'form': ResourceForm(category_choices=[
                ('notes', 'Notes'), ('pyq', 'PYQs'), ('assignment', 'Assignments'),
                ('Reference books', 'Reference books'),
            ]),
        }),
    ]:
        pages[path] = render_to_string(template, {**context, 'public_page': kind, **extra})
    guest_home = render_to_string('index.html', {
        'user': SimpleNamespace(is_authenticated=False), 'public_page': 'home', 'uploads_enabled': True,
        'csrf_token': 'offline-ui-check-only',
    })
    check_count = 0

    def check(condition, message):
        nonlocal check_count
        if not condition:
            raise AssertionError(message)
        check_count += 1

    executable = args.browser_executable
    if not executable:
        candidates = [
            Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'),
            Path('C:/Program Files/Microsoft/Edge/Application/msedge.exe'),
        ]
        executable = next((str(path) for path in candidates if path.exists()), None)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable)
        try:
            page = browser.new_page()
            page.set_default_timeout(5000)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            guest = False

            def route_request(route):
                url = urlsplit(route.request.url)
                if url.hostname == 'www.google.com' and url.path == '/maps/search/':
                    route.fulfill(body='Offline map destination check', content_type='text/plain')
                elif url.hostname == 'teachtrack.test' and url.path in pages:
                    body = guest_home if guest and url.path == '/' else pages[url.path]
                    route.fulfill(body=body, content_type='text/html')
                elif url.hostname == 'teachtrack.test' and url.path.startswith('/static/'):
                    static_root = (ROOT / 'ClassApp/static').resolve()
                    asset = (static_root / unquote(url.path[len('/static/'):])).resolve()
                    if asset.is_relative_to(static_root) and asset.is_file():
                        route.fulfill(path=str(asset))
                    else:
                        route.abort()
                else:
                    route.abort()

            browser.contexts[0].route('**/*', route_request)
            for width in (1440, 768, 390, 360):
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto('http://teachtrack.test/')
                workspace = page.locator('header').get_by_role('link', name='WORKSPACE', exact=True)
                check(not workspace.is_visible(), f'Home hides WORKSPACE at {width}px')
                page.locator('header').get_by_role('link', name='Features', exact=True).click()
                workspace.wait_for(state='visible')
                check(workspace.is_visible(), f'Features shows WORKSPACE at {width}px')
                workspace.click()
                check(urlsplit(page.url).path == '/dashboard/', 'WORKSPACE opens dashboard')
                if width <= 680:
                    page.locator('.menu-toggle').click()
                page.get_by_role('link', name='TeachTrack home', exact=True).click()
                check(urlsplit(page.url).path == '/', 'Signed-in logo opens Home')
                for path in ('/campus-life/', '/contact/'):
                    page.goto('http://teachtrack.test' + path)
                    check(workspace.is_visible(), f'{path} shows WORKSPACE at {width}px')
                    check(workspace.get_attribute('href') == '/dashboard/', 'Dashboard destination is correct')
                    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),
                          f'{path} fits at {width}px')

            page.goto('http://teachtrack.test/campus-life/')
            check(page.locator('a[href^="https://www.aurogroup.ac/"]').count() == 0,
                  'Campus life has no official-site navigation links')
            map_link = page.get_by_role('link', name='View location on Google Maps', exact=False)
            destination = map_link.get_attribute('href')
            check(parse_qs(urlsplit(destination).query).get('query') == [
                'Sri Aurobindo Institute of Technology Indore Madhya Pradesh',
            ], 'Map search targets the named institute')
            with page.expect_popup() as opened:
                map_link.click()
            popup = opened.value
            popup.wait_for_load_state()
            check(popup.url == destination, 'Location link opens its destination in a new tab')
            popup.close()

            page.goto('http://teachtrack.test/quizzes/create/')
            question = page.locator('#question-forms .question-form').first
            count = question.locator('input[name$="-option_count"]')
            add = question.get_by_role('button', name='+ Add option', exact=True)
            remove = question.get_by_role('button', name='Remove last option', exact=True)
            check(count.input_value() == '4', 'Questions start with four options')
            add.click()
            question.locator('input[name$="-correct"][value="A"]').check()
            answer_e = question.locator('input[name$="-correct"][value="E"]')
            answer_e.check()
            check(question.locator('input[name$="-is_multiple"]').is_checked(),
                  'Multiple correct answers enable multiple-answer mode')
            remove.click()
            check(answer_e.is_disabled() and not answer_e.is_checked(),
                  'Removing an option removes it from the answer key')
            for _ in range(22):
                add.click()
            check(count.input_value() == '26' and add.is_disabled(), 'Maximum option count is 26')
            for _ in range(24):
                remove.click()
            check(count.input_value() == '2' and remove.is_disabled(), 'Minimum option count is two')
            page.get_by_role('button', name='+ Add question', exact=True).click()
            check(page.locator('#question-forms .question-form').count() == 2,
                  'New questions receive their own option controls')

            page.goto('http://teachtrack.test/resources/upload/')
            custom = page.locator('#id_custom_category')
            check(not custom.is_visible(), 'Custom category field starts hidden')
            page.locator('#id_category').select_option('__custom__')
            check(custom.is_visible() and custom.get_attribute('required') is not None,
                  'Custom category selection shows a required name field')
            custom.fill('Reference books')
            page.locator('#id_category').select_option('notes')
            check(not custom.is_visible(), 'Built-in category hides the custom field')
            page.locator('#id_category').select_option('__custom__')
            check(custom.input_value() == 'Reference books', 'Category text survives selection changes')
            check(custom.get_attribute('maxlength') == '100', 'Custom names have a 100-character limit')
            check('.jpeg' in page.locator('#id_file').get_attribute('accept'), 'Picture types are selectable')
            check('30 MB' in page.locator('#id_file_helptext').inner_text(), 'Upload help shows 30 MB')
            guest = True
            page.goto('http://teachtrack.test/')
            check(page.locator('header').get_by_role('link', name='Sign in', exact=True).is_visible(),
                  'Guests retain sign-in navigation')
            check(page.locator('header').get_by_role('link', name='WORKSPACE', exact=True).count() == 0,
                  'Guests are not shown WORKSPACE')
            check(not errors, 'No JavaScript errors: ' + '; '.join(errors))
        finally:
            browser.close()
    print(f'Offline feature UI checks passed: {check_count} assertions; widths 1440/768/390/360px.')
    print('Current templates and local assets only; map destination intercepted; no app, database or external network access.')


if __name__ == '__main__':
    main()
