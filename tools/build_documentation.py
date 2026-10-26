r"""Build TeachTrack's references and offline handbook without extra dependencies.

Run with the project interpreter: .venv\Scripts\python.exe tools/build_documentation.py
This reads model metadata and source files. It does not query or modify user data.
"""
from __future__ import annotations

import ast
import base64
import html
import json
import os
from pathlib import Path
import re
import sys
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
REVIEW_DATE = '22 October 2026'
sys.path.insert(0, str(ROOT))
os.environ['DEBUG'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'documentation-build-only-not-a-runtime-secret'
os.environ['UPLOAD_STORAGE'] = 'disabled'
os.environ['GS_BUCKET_NAME'] = ''
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Classroom.settings')

import django
django.setup()
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import NOT_PROVIDED
from django import forms
from django.urls import URLResolver
from ClassApp import forms as project_forms
from ClassApp.urls import urlpatterns as app_urls
from Classroom.urls import urlpatterns as root_urls

MODEL_PURPOSES = {
    'Student': 'Original student academic record. Its Django user link connects legacy details to current authentication.',
    'Faculty': 'Original faculty contact record; also the assignment target for doubts and feedback.',
    'Director': 'Original director contact record. Application authorization is determined by Profile.role.',
    'Profile': 'One profile for every Django user; stores the application role, department and enrollment.',
    'Contact': 'Messages submitted through the public TeachTrack contact form. Saving a message does not send an email.',
    'ImageUploader': 'Retained historical image model. No current public upload workflow routes to it.',
    'PasswordResetOTP': 'Retained historical OTP table. Public password reset and outbound email are disabled.',
    'Quiz': 'Quiz metadata, creator, availability, publication flag and student-detail requirements.',
    'Question': 'A quiz question, optional image and single-selection/multiple-selection setting.',
    'Option': 'An answer option and its correctness flag, attached to one question.',
    'Submission': 'A recorded quiz attempt with identity and academic snapshots, aggregate score and a saved grading review.',
    'SubmissionAnswer': 'Original per-question answer relationship, including the selected Option many-to-many relation.',
    'SubmissionDetail': 'Original detailed answer record, retained alongside SubmissionAnswer for historical compatibility.',
    'Doubt': 'A student question assigned to faculty, with an optional attachment and an editable faculty answer.',
    'Announcement': 'A staff-authored update for a selected role or everyone, optionally with a document.',
    'Rating': 'Student feedback about faculty. A student can update their existing rating and comment.',
    'AuthenticatedStudent': 'Original complaint-system student wrapper, linked to a Django user.',
    'Teacher': 'Original complaint-system faculty wrapper, linked to a Django user.',
    'Complaint': 'A student concern assigned to a teacher, with a current status and latest faculty reply.',
    'ComplaintEvent': 'Chronological complaint messages and the status recorded for each event.',
    'Resource': 'A private document or picture upload with a built-in/custom category, descriptive metadata and download count.',
    'ResourceFile': 'A private database copy of a locally uploaded resource, allowing other instances to serve it when their filesystem lacks the original.',
    'Download': 'An authenticated resource-download initiation. Repeat downloads create additional rows.',
    'Notification': 'An individual recipient inbox item. Broadcasts create a separate row for each recipient.',
    'LoginThrottle': 'Hashed username/IP failure counters for the 15-minute login-attempt window.',
}

FIELD_NOTES = {
    'id': 'Automatically generated primary key.',
    'sname': 'Student full name.', 'sen': 'Student enrollment number.',
    'sphone': 'Student phone text; maximum 10 characters.', 'semail': 'Student email address.',
    'fname': 'Faculty full name.', 'fphone': 'Faculty phone text; maximum 15 characters.',
    'femail': 'Faculty email; nullable for retained legacy records.',
    'dname': 'Director full name.', 'dphone': 'Director phone text; maximum 15 characters.',
    'demail': 'Director email address.',
    'unm': 'Retained legacy username value; current login uses Django User.username.',
    'sem': 'Legacy student semester value.', 'year': 'Student academic year text.',
    'section': 'Student section text.', 'course': 'Student course/department text.',
    'role': 'student, faculty or director; authorization reads this value.',
    'enrollment': 'Enrollment metadata; required by student registration forms.',
    'department': 'Course/department metadata.',
    'created_at': 'Creation timestamp, set automatically.', 'submitted_at': 'Submission timestamp, set automatically.',
    'updated_at': 'Timestamp updated by the relevant application workflow; it is not auto_now.',
    'read_at': 'Null until the recipient marks this notification as read.',
    'expiry_time': 'Quiz closing timestamp; attempts require current time strictly before this value.',
    'starts_at': 'Quiz opening timestamp; the opening instant itself is eligible.',
    'is_active': 'Quiz publication/visibility flag, separate from its time window.',
    'require_name': 'Whether the quiz-attempt name field is mandatory.',
    'require_roll': 'Whether the quiz-attempt roll/enrollment field is mandatory.',
    'require_email': 'Whether the quiz-attempt email field is mandatory.',
    'require_class': 'Whether the quiz-attempt course/class field is mandatory. New quiz forms enable this automatically.',
    'code': 'Six uppercase hexadecimal characters, generated when a quiz is saved without a code.',
    'is_multiple': 'True enables selection of multiple correct options.',
    'is_correct': 'Correct-answer flag; students do not receive it before the review is released.',
    'selected_options': 'Selected answers, stored through an automatically created join table.',
    'review': 'Saved question/option text and selected/correct answer IDs used by the results view.',
    'total': 'Number of questions in the saved attempt.',
    'score': 'Correct-answer count; on SubmissionDetail this is 0 or 1 for one question.',
    'roll_no': 'Roll/enrollment value copied into an attempt.', 'class_div': 'Legacy combined academic summary, limited to 50 characters; full separate values are in academic_details.',
    'batch': 'Student batch/cohort text, editable at registration and in My profile.',
    'academic_details': 'Submission JSON snapshot containing course, year, semester, section and batch separately.',
    'student_name': 'Student display-name snapshot, including historical records.',
    'student_email': 'Student email snapshot, including historical records.',
    'answer': 'Latest faculty answer text; the form allows an existing answer to be updated.',
    'answered_at': 'Time of the most recent saved faculty answer.',
    'teacher_reply': 'Latest faculty reply; full conversation is stored in ComplaintEvent.',
    'reply_time': 'Time of the latest faculty reply.',
    'status': 'Complaint state: pending, in_progress or resolved.',
    'audience': 'all, student, faculty or director; faculty forms restrict selection to student.',
    'category': 'Resource category: notes, pyq, assignment or a custom name up to 100 characters. Existing built-in values retain their display labels.',
    'original_name': 'Uploaded filename after removing directory components; used for attachment downloads.',
    'storage_name': 'Resource file key that this database copy belongs to; a copy is served only when this key matches the current resource.',
    'content': 'Private resource file bytes, stored separately from list-page metadata and read only for an unavailable file download.',
    'download_count': 'Download-response initiations, including repeats; not proof of completed transfers.',
    'link': 'Optional notification navigation target; the read endpoint only redirects to safe local paths.',
    'key': 'SHA-256 digest of an ip: or user: throttle key; not a plaintext password.',
    'failures': 'Invalid authentication attempts counted in the current window.',
    'window_start': 'Beginning of the stored throttle window.',
    'otp': 'Historical reset OTP text; no current public OTP/reset workflow.',
    'rating': 'Integer rating from 1 to 5, with form and database constraints.',
}

ACCESS = {
    'upload_url': ('POST', 'Authenticated; permitted role/form/field only; private Blob mode'),
    'index': ('GET', 'Public'), 'campus_life': ('GET', 'Public'), 'contact': ('GET, POST', 'Public'),
    'health': ('GET', 'Public'), 'sign_in': ('GET, POST', 'Public; optional route-specific role'),
    'register': ('GET, POST', 'Public; creates students only'),
    'dashboard': ('GET', 'Authenticated'), 'resources': ('GET', 'Authenticated'),
    'profile_edit': ('GET, POST', 'Authenticated; own account only'),
    'resource_create': ('GET, POST', 'Faculty or director'), 'resource_download': ('POST', 'Authenticated'),
    'notifications': ('GET', 'Own inbox'), 'notification_read': ('POST', 'Own notification'),
    'notifications_read_all': ('POST', 'Own inbox'), 'notification_create': ('GET, POST', 'Faculty or director'),
    'announcements': ('GET', 'Authenticated; audience filtered'), 'announcement_create': ('GET, POST', 'Faculty or director'),
    'quizzes': ('GET', 'Authenticated; role filtered'), 'quiz_create': ('GET, POST', 'Faculty or director'),
    'quiz_toggle': ('POST', 'Creator faculty or director'), 'quiz_attempt': ('GET, POST', 'Student; open published valid quiz'),
    'quiz_result': ('GET', 'Own student attempt; creator faculty; director'),
    'leaderboard': ('GET', 'Authenticated; publication/ownership checks'),
    'complaints': ('GET', 'Own student; assigned faculty; director'),
    'complaint_create': ('GET, POST', 'Student'), 'complaint_detail': ('GET, POST', 'Own student; assigned faculty; director'),
    'doubts': ('GET', 'Own student; assigned faculty; director'), 'doubt_create': ('GET, POST', 'Student'),
    'doubt_answer': ('GET, POST', 'Assigned faculty only'), 'feedback': ('GET, POST', 'Authenticated; only students can POST'),
    'accounts': ('GET', 'Director'), 'account_create': ('GET, POST', 'Director'), 'account_toggle': ('POST', 'Director'),
    'reports': ('GET', 'Director'), 'report_export': ('GET', 'Director'),
    'question_image': ('GET', 'Authenticated; quiz access checks'),
    'attachment_download': ('POST', 'Authenticated; object/audience checks'),
    'submission_detail_list': ('GET', 'Own student; creator faculty; director'),
    'legacy_score': ('GET', 'Own student; creator faculty; director'),
    'student_dashboard': ('GET', 'Student'), 'faculty_dashboard': ('GET', 'Faculty'),
    'Director_dashboard': ('GET', 'Director'),
}


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows])


def write(name, contents):
    (DOCS / name).write_text(contents.rstrip() + '\n', encoding='utf-8')


def default_label(field):
    value = field.default
    if value is NOT_PROVIDED:
        return 'Automatic' if getattr(field, 'auto_now_add', False) else '—'
    if callable(value):
        return getattr(value, '__name__', type(value).__name__) + '()'
    return repr(value)


def database_reference():
    out = ['# Database reference', '', f'Extracted from Django model metadata on {REVIEW_DATE}.', '',
           'This is the current declared schema. The installed database must also have migrations 0001–0009 applied. '
           'Nullable legacy relationships are intentional and do not authorize an arbitrary user to view a historical record.', '',
           '## Reading the dictionary', '',
           'FK means foreign key; O2O means one-to-one; M2M means many-to-many. `blank` is form/model-validation behavior, '
           '`null` permits SQL NULL, and `PROTECT` prevents deletion while referenced. `CASCADE` removes dependent rows; '
           '`SET_NULL` retains the row and clears the link. M2M fields use separate join tables.', '',
           'Django authentication, groups, permissions, sessions, content types and admin-log tables are provided by installed Django applications. '
           'This reference lists every project model and its declared fields, including automatically generated IDs.', '',
           '![Database relationships](assets/database.svg)', '']
    for model in apps.get_app_config('ClassApp').get_models():
        meta = model._meta
        out += [f'## {model.__name__}', '', MODEL_PURPOSES[model.__name__], '',
                f'Table: `{meta.db_table}`. Default ordering: `{list(meta.ordering) or "database default"}`.', '']
        rows = []
        for field in [*meta.local_fields, *meta.local_many_to_many]:
            kind = field.get_internal_type()
            if getattr(field, 'max_length', None):
                kind += f'({field.max_length})'
            rules = []
            if field.primary_key: rules.append('primary key')
            if field.unique and not field.primary_key: rules.append('unique')
            if field.db_index and not field.primary_key: rules.append('indexed')
            rules += ['null=' + str(field.null), 'blank=' + str(field.blank)]
            if field.choices: rules.append('choices: ' + ', '.join(str(k) for k, _ in field.choices))
            relation = '—'
            if field.is_relation:
                relation = field.related_model._meta.label
                if field.many_to_many:
                    relation += '; M2M via ' + field.remote_field.through._meta.db_table
                else:
                    relation += '; ' + field.remote_field.on_delete.__name__
            description = FIELD_NOTES.get(field.name, 'Link to the related record.' if field.is_relation else str(field.verbose_name).capitalize() + '.')
            if hasattr(field, 'upload_to'):
                upload = field.upload_to
                description += ' Upload path: ' + (upload.__name__ + '()' if callable(upload) else str(upload)) + '.'
            rows.append([f'`{field.name}`', kind, default_label(field), '; '.join(rules), relation, description])
        out += [table(['Field', 'Type / length', 'Default', 'Rules', 'Relation / deletion', 'Meaning'], rows), '']
        if meta.constraints:
            out += ['Declared constraints:', '']
            for constraint in meta.constraints:
                detail = ', '.join(getattr(constraint, 'fields', [])) or str(getattr(constraint, 'condition', ''))
                out += [f'- `{constraint.name}`: {type(constraint).__name__} — {detail}.']
            out += ['']
        if meta.indexes:
            out += ['Explicit indexes: ' + '; '.join(f'`{i.name}` on `{i.fields}`' for i in meta.indexes) + '.', '']
    write('DATABASE_REFERENCE.md', '\n'.join(out))


def route_reference():
    out = ['# Route reference', '', 'Paths are relative to the application host. Local example: `http://127.0.0.1:8000/`.', '',
           'The Methods column describes verbs used by the interface. Explicit method decorators enforce POST for mutations '
           'such as downloads, mark-read, publication toggles and account deactivation; the quiz-attempt view explicitly permits GET/POST. '
           'Other read views do not all reject alternative verbs. This is a server-rendered HTML application; these URLs are not a JSON REST API.', '',
           '`pk` and `submission_id` are integer identifiers. `kind` selects an allowed attachment or report type. '
           'An authenticated user with an incorrect role receives a permission error; missing/foreign private objects may return 404.', '',
           '## Current and compatibility routes', '']
    rows = []
    seen = defaultdict(list)
    for pattern in app_urls:
        path = '/' + str(pattern.pattern)
        name = pattern.name or '—'
        view = pattern.callback.__name__
        methods, access = ACCESS[view]
        options = ', '.join(f'{k}={v}' for k, v in pattern.default_args.items()) or '—'
        rows.append([f'`{path}`', f'`{name}`', view, methods, access, options])
        seen[path].append(name)
    out += [table(['Path', 'URL name', 'View', 'Methods', 'Access', 'Fixed arguments'], rows), '',
            '## Authentication and administration', '']
    rows = [['`/admin/`', 'Django admin URL namespace', 'GET / POST', 'Django staff/superuser authorization; application director role alone does not grant admin access.']]
    for pattern in root_urls:
        if isinstance(pattern, URLResolver): continue
        name = pattern.name or ''
        path = '/' + str(pattern.pattern)
        if name.startswith('password_change') or name == 'logout':
            access = 'Authenticated'
        elif name == 'register': access = 'Public student registration'
        else: access = 'Public login'
        method = 'POST' if name == 'logout' else 'GET' if name.endswith('done') or name.endswith('complete') else 'GET, POST'
        rows.append([f'`{path}`', f'`{name}`', method, access])
    out += [table(['Path', 'URL name', 'Methods', 'Access'], rows), '', '## Duplicate paths and aliases', '',
            'Django resolves the first matching URL pattern. Several retained names reverse to the same path and use the same upgraded view:', '']
    out += [f'- `{path}`: ' + ', '.join(f'`{n}`' for n in names) + '.' for path, names in seen.items() if len(names) > 1]
    out += ['', 'The legacy `/score/<submission_id>/` path looks up a Submission ID; the modern quiz result route uses a Quiz ID. '
            'Path case matters: `/Director_dashboard/` retains its original capitalization.', '',
            '## Query parameters', '', table(['Page', 'Parameter', 'Behavior'], [
                ['Resources', 'q', 'Case-insensitive title, description and subject search; stripped to 150 characters.'],
                ['Resources', 'category', 'Built-in value (notes, pyq, assignment) or a saved custom category name; matches the stored category.'],
                ['Resources', 'subject', 'Case-insensitive exact subject; stripped to 100 characters.'],
                ['Resources', 'sort=title', 'Alphabetical title, then ID; otherwise model ordering is newest first.'],
                ['Quizzes', 'code', 'Uppercase exact quiz code, stripped to six characters.'],
                ['Complaints', 'status', 'Stored status code; pending, in_progress or resolved.'],
                ['Account creation', 'role', 'GET selects faculty, student or director; faculty is the default. Legacy staff routes fix the role.'],
                ['Paginated lists', 'page', 'Page number; 15 records per page.'],
            ])]
    write('ROUTE_REFERENCE.md', '\n'.join(out))


def form_reference():
    out = ['# Forms and validation reference', '',
           'Extracted from active form classes. Required marks below apply to an unbound form; '
           'quiz-attempt identity fields become required according to that quiz’s four requirement flags.', '',
           'Public student registration ignores injected role or superuser fields. Director-only account routes determine the '
           'selected role on the server and remove student-only academic fields for staff. Phone inputs limit character length; '
           'they do not implement a numeric-only or international telephone-number validator.', '']
    names = ['StudentRegistrationForm', 'ResourceForm', 'QuizForm', 'QuestionEntryForm', 'StudentInfoForm',
             'AnnouncementForm', 'ComplaintForm', 'DoubtForm', 'FeedbackForm', 'ReplyForm', 'AnswerForm', 'NotificationForm', 'ContactForm']
    instances = [(n, getattr(project_forms, n)()) for n in names]
    instances[1:1] = [(f'AccountForm — {role}', project_forms.AccountForm(role=role)) for role in ['student', 'faculty', 'director']]
    from ClassApp.models import Profile, Student, Faculty, Director
    for role, model, relation in [('student', Student, 'legacy_student'),
                                  ('faculty', Faculty, 'legacy_faculty'),
                                  ('director', Director, 'legacy_director')]:
        account = get_user_model()()
        account.profile = Profile(user=account, role=role)
        setattr(account, relation, model(user=account))
        instances.append((f'ProfileForm — {role}', project_forms.ProfileForm(instance=account)))
    user = get_user_model()()
    instances += [('Django AuthenticationForm', AuthenticationForm()),
                  ('Django PasswordChangeForm', PasswordChangeForm(user))]
    for name, form in instances:
        out += [f'## {name}', '']
        rows = []
        for key, field in form.fields.items():
            rules = []
            for attr in ['max_length', 'min_length', 'min_value', 'max_value']:
                value = getattr(field, attr, None)
                if value is not None: rules.append(f'{attr}={value}')
            if isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                rules.append('choices: ' + ', '.join(str(v) for v, _ in field.choices))
            if isinstance(field, forms.ModelChoiceField): rules.append('Authorized model choices; see workflow rules')
            if field.widget.is_hidden: rules.append('hidden input')
            rows.append([f'`{key}`', str(field.label or key.replace('_', ' ').capitalize()), type(field).__name__,
                         'Yes' if field.required else 'No', type(field.widget).__name__, '; '.join(rules) or 'Default Django field validation'])
        out += [table(['Field', 'Label', 'Field type', 'Required', 'Widget', 'Validation / choices'], rows), '']
    out += ['## Additional server rules', '',
            '- Email uniqueness is checked case-insensitively in the account form; the email is stored lowercase. Django User.email itself is not made globally unique by a database constraint.',
            '- Passwords use Django’s configured similarity, minimum-length (10), common-password and numeric-only rejection validators.',
            '- The quiz closing time must be later than the opening time.',
            '- QuestionFormSet requires 1–50 question forms and uses the `questions` prefix. The builder starts with four options and supports 2–26 options (A–Z) per question, controlled by option_count. Every displayed option needs text. Older payloads without option_count retain the four-option compatibility behavior.',
            '- A single-selection question needs exactly one marked correct option. Every marked correct option needs text.',
            '- Multiple-selection questions are also checked by valid_quiz before students can attempt them; a valid quiz needs at least one correct option per question.',
            '- Correct answers outside the current option count are rejected. Selecting multiple correct checkboxes enables the multiple-answer setting in the browser; the server still validates the single/multiple-choice rule.',
            '- Resource categories include Notes, PYQs, Assignments and saved custom names. Add custom category requires a nonblank name up to 100 characters, normalizes whitespace and reuses matching existing labels without case differences. Saved categories appear in later upload choices and library filters.',
            '- Resource files accept PDF, UTF-8 TXT, DOCX, PPTX, JPG, JPEG and PNG, up to 30 MB each. Images are verified with Pillow. The declared total request-body limit is 32 MB, including multipart overhead; the per-file limit is separate.',
            '- Complaint, doubt and feedback faculty choices include only active faculty users with the faculty role, ordered by name then ID.',
            '- Faculty announcement and notification forms permit the Students audience only; directors may choose all configured audiences.',
            '- A complaint reply requires a message up to 5,000 characters. Only directors receive the status input. A complaint body accepts up to 10,000 characters.',
            '- Private Vercel Blob mode uploads bytes directly with scoped signed PUT URLs and validates them server-side using user/form/field-bound receipts. Authorized downloads redirect to private GET URLs valid for 5 minutes. See the Vercel deployment guide.',
            '- Resource, announcement and doubt file validation and image safety checks are detailed in the handbook Security and uploads chapter.',
            '- New quiz forms automatically publish and require name, enrollment, email and course; these flags are not displayed.',
            '- StudentInfoForm autofills identity and separate course/year/semester/section/batch fields from the account.',
            '- ProfileForm edits only the authenticated account and synchronizes linked role records; roles and permissions cannot be edited here.',
            '- Login and signed-in password change use Django forms. Public password reset, phone OTP and SMTP are disabled.', '']
    write('FORM_REFERENCE.md', '\n'.join(out))


def palette_reference():
    sources = ['ClassApp/static/ClassApp/app.css', 'ClassApp/static/ClassApp/theme.css']
    css = '\n'.join((ROOT / name).read_text(encoding='utf-8') for name in sources)
    tokens = []
    usages = defaultdict(set)
    for rule in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        selector = rule.group(1).strip()
        for declaration in rule.group(2).split(';'):
            if ':' not in declaration: continue
            prop, value = declaration.split(':', 1)
            if prop.strip().startswith('--'):
                tokens.append((selector + ' / ' + prop.strip(), value.strip()))
            for color in re.findall(r'#[0-9a-fA-F]{3,8}\b|(?<![-\w])(?:white|transparent)\b', value):
                usages[color.lower()].add(selector + ' → ' + prop.strip())
    palette = []
    for color, selectors in sorted(usages.items()):
        raw = color.lstrip('#')
        if color == 'white': raw = 'ffffff'
        if color == 'transparent': raw = '00000000'
        if len(raw) in (3, 4): raw = ''.join(c * 2 for c in raw)
        rgb = tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4))
        alpha = int(raw[6:8], 16) / 255 if len(raw) == 8 else 1
        palette.append({'literal': color, 'hex': '#' + raw, 'rgb': rgb, 'alpha': alpha, 'usages': sorted(selectors)})
    rows = [[f'`{p["literal"]}`', f'{p["rgb"][0]}, {p["rgb"][1]}, {p["rgb"][2]}', f'{p["alpha"] * 100:.2f}%',
             '; '.join(f'`{s}`' for s in p['usages'])] for p in palette]
    out = ['# Complete colour index', '',
           f'Generated from `app.css` and `theme.css` on {REVIEW_DATE}: '
           f'{len([p for p in palette if p["literal"].startswith("#")])} distinct hex literals plus named CSS colours. '
           'This is an inventory of the active application stylesheet, not of photographic pixels, browser defaults or the retained legacy theme.', '',
           '## Theme variables', '', table(['Token', 'Declared value'], [[f'`{k}`', f'`{v}`'] for k, v in tokens]), '',
           '## Every explicit colour and its source usage', '',
           'Three-digit hex expands each digit twice. Eight-digit hex is RRGGBBAA, with the last byte specifying alpha. '
           'RGB below is the uncomposited colour; its visible appearance also depends on opacity and the underlying surface. '
           'Named white aliases #ffffff, while transparent has zero opacity. `currentColor` in SVG arrows inherits its surrounding text colour.', '',
           table(['CSS literal', 'RGB', 'Opacity', 'Selectors and properties'], rows), '']
    write('COLOUR_INDEX.md', '\n'.join(out))
    (DOCS / 'colour-index.json').write_text(json.dumps({'sources': sources, 'tokens': dict(tokens), 'colours': palette}, indent=2) + '\n', encoding='utf-8')
    return palette


def test_catalogue():
    rows = []
    for source in sorted((ROOT / 'ClassApp').glob('test*.py')):
        tree = ast.parse(source.read_text(encoding='utf-8'))
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                for method in cls.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                        rows.append([source.name, cls.name, f'`{method.name}`', method.name.removeprefix('test_').replace('_', ' ')])
    write('TEST_CATALOGUE.md', '# Test catalogue\n\n' + f'{len(rows)} test methods are defined in `ClassApp/test*.py`. '
          'This catalogue describes source coverage; a successful test execution must be recorded separately.\n\n' +
          table(['Source', 'Test class', 'Method', 'Scenario'], rows))


def diagram(name, title, boxes, edges, width, height):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
             '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#126c64"/></marker></defs>',
             f'<rect width="{width}" height="{height}" rx="16" fill="#f7f9f7"/>',
             f'<text x="25" y="34" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#172d35">{html.escape(title)}</text>']
    lookup = {b[0]: b for b in boxes}
    for start, end in edges:
        _, x1, y1, w1, h1, _ = lookup[start]
        _, x2, y2, w2, h2, _ = lookup[end]
        if abs(x2 - x1) > abs(y2 - y1):
            a, b = (x1 + w1, y1 + h1 / 2), (x2, y2 + h2 / 2)
            if x2 < x1: a, b = (x1, y1 + h1 / 2), (x2 + w2, y2 + h2 / 2)
        else:
            a, b = (x1 + w1 / 2, y1 + h1), (x2 + w2 / 2, y2)
            if y2 < y1: a, b = (x1 + w1 / 2, y1), (x2 + w2 / 2, y2 + h2)
        parts.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#126c64" fill="none" stroke-width="2" marker-end="url(#arrow)"/>')
    for _, x, y, w, h, lines in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="white" stroke="#cbded2"/>')
        for i, line in enumerate(lines):
            parts.append(f'<text x="{x+w/2}" y="{y+24+i*19}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#172d35">{html.escape(line)}</text>')
    parts.append('</svg>')
    (DOCS / 'assets' / name).write_text('\n'.join(parts), encoding='utf-8')


def build_diagrams():
    (DOCS / 'assets').mkdir(exist_ok=True)
    diagram('architecture.svg', 'TeachTrack application architecture', [
        ('browser', 25, 75, 160, 70, ['Browser', 'HTML forms + CSS + JS']),
        ('django', 240, 75, 210, 90, ['Django / Classroom', 'Middleware → URLs → views', 'Forms + role / object checks']),
        ('templates', 510, 75, 205, 70, ['Templates + static assets', 'Server-rendered response']),
        ('db', 240, 225, 210, 70, ['Relational database', 'SQLite / MySQL / PostgreSQL']),
        ('media', 510, 225, 205, 70, ['Private uploaded files', 'Local / private Blob / GCS']),
        ('theme', 25, 225, 160, 70, ['Light / dark mode', 'Browser preference']),
    ], [('browser','django'),('django','templates'),('django','db'),('django','media'),('browser','theme')], 740, 325)
    diagram('database.svg', 'Core relationships — full field dictionary follows', [
        ('user', 275, 65, 185, 65, ['Django User + Profile', 'Role / account identity']),
        ('legacy', 25, 180, 205, 65, ['Student / Faculty / Director', 'Legacy contact / academic data']),
        ('quiz', 275, 180, 185, 65, ['Quiz → Question → Option', 'Creator and answer structure']),
        ('resources', 515, 180, 205, 65, ['Resource / File / Download', 'Uploader and reader']),
        ('submissions', 275, 305, 185, 65, ['Submission', 'Answer / Detail + M2M options']),
        ('complaints', 25, 305, 205, 65, ['Complaint → ComplaintEvent', 'Student / Teacher wrappers']),
        ('messages', 515, 305, 205, 65, ['Doubt / Rating / Notification', 'Assignment and ownership']),
    ], [('user','legacy'),('user','quiz'),('user','resources'),('quiz','submissions'),('legacy','complaints'),('user','messages')], 745, 405)
    diagram('complaint-workflow.svg', 'Complaint lifecycle', [
        ('pending', 25, 80, 195, 90, ['Pending', 'Student submits a concern', 'Initial timeline event']),
        ('progress', 275, 80, 195, 90, ['In progress', 'First assigned faculty reply', 'Timeline + notifications']),
        ('resolved', 525, 80, 195, 90, ['Resolved', 'Director selects status', 'Timeline + notifications']),
    ], [('pending','progress'),('progress','resolved')], 745, 205)


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


CHAPTERS = [
    ('PROJECT_DOCUMENTATION.md', 'Project handbook'), ('DESIGN_SYSTEM.md', 'Design system'),
    ('DATABASE_REFERENCE.md', 'Database reference'), ('FORM_REFERENCE.md', 'Forms and validation'),
    ('ROUTE_REFERENCE.md', 'Route reference'), ('CONFIGURATION_REFERENCE.md', 'Configuration reference'),
    ('COLOUR_INDEX.md', 'Complete colour index'), ('TEST_CATALOGUE.md', 'Test catalogue'),
    ('VERCEL_DEPLOYMENT.md', 'Vercel deployment'), ('RECENT_CHANGES.md', 'Current features and changes'),
    ('TESTING.md', 'Testing and acceptance'), ('WEBSITE_REVIEW.md', 'Website quality review'),
    ('DATABASE_SETUP.md', 'Local MySQL and Aiven'),
]


def inline(text):
    fragments = []
    def hold(match):
        fragments.append('<code>' + html.escape(match.group(1)) + '</code>')
        return f'ZZCODE{len(fragments)-1}ZZ'
    text = re.sub(r'`([^`]+)`', hold, text)
    text = html.escape(text)
    def image_link(match):
        label, target = html.unescape(match.group(1)), html.unescape(match.group(2))
        asset = DOCS / target
        if asset.exists() and asset.suffix == '.svg':
            target = 'data:image/svg+xml;base64,' + base64.b64encode(asset.read_bytes()).decode()
        return f'<img class="doc-diagram" src="{html.escape(target, quote=True)}" alt="{html.escape(label)}">'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', image_link, text)
    def link(match):
        label, target = match.group(1), html.unescape(match.group(2))
        filename, _, anchor = target.partition('#')
        if filename in {name for name, _ in CHAPTERS}:
            target = '#' + slug(Path(filename).stem.replace('_', '-')) + ('--' + anchor if anchor else '')
        return f'<a href="{html.escape(target, quote=True)}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    for i, fragment in enumerate(fragments): text = text.replace(f'ZZCODE{i}ZZ', fragment)
    return text


def render_markdown(source, prefix):
    """Render the deliberately limited Markdown constructs used by this handbook."""
    lines, result, headings = source.splitlines(), [], []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip(): index += 1; continue
        if line.startswith('```'):
            language, code = line[3:], []
            index += 1
            while index < len(lines) and not lines[index].startswith('```'):
                code.append(lines[index]); index += 1
            result.append('<pre data-language="' + html.escape(language) + '"><code>' + html.escape('\n'.join(code)) + '</code></pre>')
            index += 1; continue
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading:
            level, title = len(heading[1]), heading[2]
            anchor = prefix if level == 1 else prefix + '--' + slug(title)
            headings.append((level, title, anchor))
            result.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            index += 1; continue
        if line.startswith('|') and index + 1 < len(lines) and re.match(r'^\|[\s:|\-]+\|$', lines[index + 1]):
            rows = []
            while index < len(lines) and lines[index].startswith('|'):
                rows.append(re.split(r'(?<!\\)\|', lines[index].strip().strip('|'))); index += 1
            result.append('<div class="table-scroll"><table><thead><tr>' + ''.join('<th>' + inline(c.strip().replace('\\|', '|')) + '</th>' for c in rows[0]) + '</tr></thead><tbody>')
            for row in rows[2:]:
                result.append('<tr>' + ''.join('<td>' + inline(c.strip().replace('\\|', '|')) + '</td>' for c in row) + '</tr>')
            result.append('</tbody></table></div>'); continue
        if re.match(r'^(?:- |\d+\. )', line):
            ordered = bool(re.match(r'^\d+\.', line)); tag = 'ol' if ordered else 'ul'
            result.append(f'<{tag}>')
            while index < len(lines) and re.match(r'^(?:\d+\. )' if ordered else r'^- ', lines[index]):
                result.append('<li>' + inline(re.sub(r'^(?:- |\d+\. )', '', lines[index])) + '</li>'); index += 1
            result.append(f'</{tag}>'); continue
        paragraph = [line]; index += 1
        while index < len(lines) and lines[index].strip() and not re.match(r'^(?:#|```|\||- |\d+\. )', lines[index]):
            paragraph.append(lines[index]); index += 1
        result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(result), headings


def build_html(palette):
    sections, navigation = [], []
    for filename, label in CHAPTERS:
        prefix = slug(Path(filename).stem.replace('_', '-'))
        body, headings = render_markdown((DOCS / filename).read_text(encoding='utf-8'), prefix)
        sections.append(f'<section class="chapter" aria-label="{label}">{body}</section>')
        navigation.append(f'<a class="chapter-link" href="#{prefix}">{label}</a>')
        navigation.extend(f'<a class="sub-link" href="#{anchor}">{html.escape(title)}</a>' for level, title, anchor in headings if level == 2)
    swatches = []
    for color in palette:
        query = color['literal'] + ' ' + ' '.join(color['usages'])
        usage = html.escape('; '.join(color['usages']))
        swatches.append(f'<article class="swatch-card" data-colour="{html.escape(query, quote=True)}"><div class="swatch-preview"><span style="background:{color["literal"]}"></span></div><code>{color["literal"]}</code><small>RGB {color["rgb"]} · {color["alpha"]*100:.2f}% opacity</small><p>{usage}</p></article>')
    colour_section = '<section class="chapter" id="visual-colour-catalogue"><h1>Visual colour catalogue</h1><p>Every explicit colour in the active application and light/dark theme stylesheets. Transparent colours are shown over a checkerboard. Search by value, selector or property.</p><label class="colour-search">Filter colours <input type="search" id="colour-search" placeholder="Try #126c64, .pending, or footer"></label><div class="swatch-grid">' + ''.join(swatches) + '</div></section>'
    css = '''
:root{--ink:#172d35;--teal:#126c64;--line:#dfe8e2}*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:var(--ink);font:15px/1.75 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--teal)}aside{position:fixed;inset:0 auto 0 0;width:290px;padding:30px 22px;background:#143c35;color:#fff;overflow:auto}aside strong{display:block;font-size:24px;letter-spacing:-1px}aside p{font-size:12px;color:#c2d5c9}aside nav a{display:block;color:#d5e4da;text-decoration:none;font-size:11px;padding:5px 9px;border-radius:5px}aside nav a:hover{background:#ffffff20}aside .chapter-link{font-size:13px;font-weight:700;margin-top:16px;color:#fff}aside .sub-link{border-left:1px solid #ffffff20;margin-left:9px}.document{max-width:1240px;padding:55px 55px 80px;margin-left:290px}.cover{padding:40px;background:linear-gradient(120deg,#e8f4ef,#fff);border:1px solid var(--line);border-radius:16px;margin-bottom:40px}.cover h1{font-size:46px;line-height:1.1;margin:14px 0 20px;letter-spacing:-1.8px}.cover small{letter-spacing:2px;color:var(--teal);font-weight:700}.cover p{max-width:680px}.toolbar{display:flex;gap:20px;align-items:center;margin-top:22px}button{background:var(--teal);border:0;border-radius:6px;color:white;padding:10px 18px;font:inherit;cursor:pointer}.chapter{margin-bottom:65px;scroll-margin-top:20px}h1{font-size:34px;line-height:1.2;letter-spacing:-.9px;margin:55px 0 25px}h2{font-size:23px;line-height:1.35;border-bottom:1px solid var(--line);padding-bottom:10px;margin:38px 0 18px}h3{font-size:18px;margin:28px 0 12px}h4{font-size:15px}p{margin:0 0 16px}li{margin-bottom:8px}ul,ol{padding-left:24px}code{font-family:Consolas,monospace;font-size:.9em;background:#eaf0ec;padding:2px 5px;border-radius:3px;overflow-wrap:anywhere}pre{background:#102b24;color:#e3eee7;padding:20px;border-radius:8px;overflow:auto;line-height:1.6;font-size:12px}pre code{background:none;padding:0;color:inherit;white-space:pre-wrap;overflow-wrap:anywhere}.table-scroll{overflow:auto;margin:20px 0 28px}table{width:100%;border-collapse:collapse;background:#fff;font-size:12px}th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#e8f4ef;font-size:11px}tbody tr:nth-child(even){background:#f7faf8}.doc-diagram{display:block;width:100%;max-height:460px;object-fit:contain;margin:20px auto}.colour-search{display:block;margin:24px 0}.colour-search input{display:block;width:100%;max-width:580px;margin-top:7px;padding:12px;border:1px solid #b7cbbd;border-radius:6px;font:inherit}.swatch-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.swatch-card{background:white;border:1px solid var(--line);border-radius:9px;overflow:hidden;min-width:0}.swatch-preview{height:86px;background:repeating-conic-gradient(#d6dcd8 0% 25%,#fff 0% 50%) 50%/16px 16px}.swatch-preview span{display:block;width:100%;height:100%}.swatch-card>code{display:block;margin:15px 15px 5px;background:none;font-weight:700}.swatch-card small{display:block;font-size:10px;margin:0 15px 10px;color:#63766f}.swatch-card p{font-size:9px;margin:0 15px 15px;max-height:105px;overflow:auto;overflow-wrap:anywhere}.swatch-card[hidden]{display:none}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #e7af49;outline-offset:3px}@media(max-width:1000px){aside{width:235px}.document{margin-left:235px;padding:30px}.swatch-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:720px){aside{position:static;width:auto;max-height:330px}.document{margin:0;padding:22px}.cover{padding:25px}.cover h1{font-size:34px}h1{font-size:28px}.swatch-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@page{size:A4;margin:16mm 13mm}@media print{body{background:#fff;font:11px/1.6 Arial,sans-serif}aside,.toolbar,.colour-search{display:none}.document{margin:0;padding:0;max-width:none}.cover{margin:0;padding:22px;background:#e8f4ef;break-after:page;border-radius:0}.cover h1{font-size:40px}.chapter{break-before:page;margin:0}h1{font-size:27px;margin:0 0 20px}h2{font-size:19px;margin:25px 0 12px;break-after:avoid}h3{font-size:15px;break-after:avoid}h4{break-after:avoid}p,li{orphans:3;widows:3}table{font-size:9px;table-layout:fixed}th{font-size:9px}td,th{padding:6px;word-break:normal;overflow-wrap:anywhere}thead{display:table-header-group}tr{break-inside:avoid}.table-scroll{overflow:visible}pre{white-space:pre-wrap;font-size:9px;background:#f1f5f2;color:#172d35;border:1px solid #dfe8e2}pre code{white-space:pre-wrap}.doc-diagram{max-height:320px;break-inside:avoid}.swatch-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.swatch-card{break-inside:avoid}.swatch-preview{height:48px;print-color-adjust:exact;-webkit-print-color-adjust:exact}.swatch-card p{max-height:none;font-size:6.5px;line-height:1.4}.swatch-card>code{margin:8px 8px 4px;font-size:10px}.swatch-card small{font-size:7px;margin:0 8px 8px}.swatch-card p{margin:0 8px 8px}.swatch-card[hidden]{display:block}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}a{color:#126c64;text-decoration:none}}
'''
    document = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TeachTrack — Complete Project Documentation</title><style>' + css + '</style></head><body><aside><strong>TeachTrack.</strong><p>PROJECT DOCUMENTATION<br>' + REVIEW_DATE + '</p><nav aria-label="Documentation chapters">' + ''.join(navigation) + '<a class="chapter-link" href="#visual-colour-catalogue">Visual colour catalogue</a></nav></aside><main class="document"><div class="cover"><small>PROJECT HANDBOOK · DESIGN & TECHNICAL REFERENCE</small><h1>TeachTrack<br>Complete documentation.</h1><p>A detailed guide to setup, architecture, roles, workflows, data, forms, routes, configuration, security, operations and the complete colour system.</p><p><strong>Prepared for Zaman & Saloni</strong><br>Source review: ' + REVIEW_DATE + '<br>Documentation describes the code in this workspace; it does not certify a live cloud deployment.</p><div class="toolbar"><button type="button" onclick="window.print()">Print / save as PDF</button><a href="#project-documentation">Start reading →</a></div></div>' + ''.join(sections) + colour_section + '</main><script>document.querySelector("#colour-search").addEventListener("input",event=>{const value=event.target.value.trim().toLowerCase();document.querySelectorAll("[data-colour]").forEach(card=>{card.hidden=!card.dataset.colour.toLowerCase().includes(value);});});</script></body></html>'
    write('TEACHTRACK_DOCUMENTATION.html', document)


def main():
    build_diagrams()
    database_reference()
    route_reference()
    form_reference()
    palette = palette_reference()
    test_catalogue()
    build_html(palette)
    print(f'Built handbook, references and {len(palette)} colour swatches in {DOCS}. No database rows accessed.')


if __name__ == '__main__':
    main()
