import csv
import io
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import (Profile, Resource, Notification, Download, Quiz, Question, Submission,
                     Complaint, ComplaintEvent, Rating as Feedback, Doubt, Announcement, LoginThrottle, Faculty, Student, Option, AuthenticatedStudent, Teacher, SubmissionAnswer, SubmissionDetail)
from .forms import ResourceForm
from .services import ensure_legacy

TEST_STORAGES = {'default':{'BACKEND':'django.core.files.storage.InMemoryStorage'},
                 'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}

@override_settings(STORAGES=TEST_STORAGES)
class WorkspaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users={}
        for role in ['student','faculty','director','other_student','other_faculty']:
            user=get_user_model().objects.create_user(role,password='TestingPassword#57',first_name=role.replace('_',' ').title(),email=f'{role}@example.test')
            Profile.objects.filter(user=user).update(role=role.replace('other_',''))
            ensure_legacy(user,role.replace('other_',''))
            cls.users[role]=user
        cls.student=cls.users['student'];cls.faculty=cls.users['faculty'];cls.director=cls.users['director']
    def login_as(self,role):
        self.client.force_login(self.users[role])
    def make_quiz(self, **kwargs):
        args={'title':'Python quiz','subject':'Python','creator':self.faculty,'is_active':True,
              'starts_at':timezone.now()-timedelta(hours=1),'expiry_time':timezone.now()+timedelta(hours=1)}
        args.update(kwargs)
        q=Quiz.objects.create(**args)
        question=Question.objects.create(quiz=q,text='A unique question with answer options')
        for text,correct in [('Wrong A',False),('Secret correct option B',True),('Wrong C',False),('Wrong D',False)]:
            Option.objects.create(question=question,text=text,is_correct=correct)
        return q,question
    def resource(self):
        return Resource.objects.create(title='DB notes',subject='DBMS',category='notes',uploaded_by=self.faculty,
            original_name='notes.txt',file=SimpleUploadedFile('notes.txt',b'Knowledge'))
    def complaint(self):
        return Complaint.objects.create(student=AuthenticatedStudent.objects.get(user=self.student),teacher=Teacher.objects.get(user=self.faculty),title='Lab concern',text='Please repair the lab.')

    def test_all_role_pages_render(self):
        for role in ['student','faculty','director']:
            self.login_as(role)
            for name in ['dashboard','resources','notifications','announcements','quizzes','complaints','doubts','feedback','password_change']:
                with self.subTest(role=role,page=name):
                    self.assertEqual(self.client.get(reverse(name)).status_code,200)
        for name in ['accounts','account_create','reports','resource_create','quiz_create','announcement_create','notification_create']:
            self.assertEqual(self.client.get(reverse(name)).status_code,200)
    def test_guests_require_login(self):
        for name in ['dashboard','resources','quizzes','complaints','feedback','reports','notifications']:
            self.assertEqual(self.client.get(reverse(name)).status_code,302)
    def test_student_cannot_access_staff_actions(self):
        self.login_as('student')
        for name in ['resource_create','quiz_create','announcement_create','notification_create','accounts','account_create','reports']:
            for method in ['get','post']:
                self.assertEqual(getattr(self.client,method)(reverse(name)).status_code,403)
        self.assertEqual(self.client.get(reverse('report_export',args=['resources'])).status_code,403)
    def test_registration_hashes_password_and_ignores_role_injection(self):
        response=self.client.post(reverse('register'),{'username':'newstudent','first_name':'New Student','email':'new@example.test','enrollment':'CS001','department':'CSE','password1':'UniqueStrongPassword#529','password2':'UniqueStrongPassword#529','role':'director','is_superuser':'1'})
        self.assertEqual(response.status_code,302)
        u=get_user_model().objects.get(username='newstudent')
        self.assertTrue(u.check_password('UniqueStrongPassword#529'))
        self.assertNotEqual(u.password,'UniqueStrongPassword#529')
        self.assertFalse(u.is_superuser)
        self.assertEqual(u.profile.role,'student')
        self.assertEqual(u.profile.enrollment,'CS001')
    def test_login_throttle(self):
        for _ in range(10):
            self.client.post(reverse('login'),{'username':'student','password':'wrong'})
        response=self.client.post(reverse('login'),{'username':'student','password':'TestingPassword#57'})
        self.assertEqual(response.status_code,429)
        LoginThrottle.objects.update(window_start=timezone.now()-timedelta(minutes=16))
        response=self.client.post(reverse('login'),{'username':'student','password':'TestingPassword#57'})
        self.assertRedirects(response,reverse('dashboard'))
    def test_role_login_pages_and_matching_accounts(self):
        for role in ['student','faculty','director']:
            with self.subTest(role=role):
                self.client.logout()
                url=reverse(role+'_login')
                response=self.client.get(url)
                self.assertContains(response,f'<h2>{role.title()} sign in</h2>',html=True)
                if role!='student':
                    self.assertNotContains(response,f'href="{reverse("register")}"')
                response=self.client.post(url,{'username':role,'password':'TestingPassword#57'})
                self.assertRedirects(response,reverse('dashboard'))
                self.assertEqual(int(self.client.session['_auth_user_id']),self.users[role].pk)
    def test_role_login_mismatch_explains_where_to_sign_in(self):
        response=self.client.post(reverse('faculty_login'),{'username':'student','password':'TestingPassword#57'})
        self.assertContains(response,'Use the student login for this account.')
        self.assertContains(response,'Faculty sign in')
        self.assertNotIn('_auth_user_id',self.client.session)
        self.assertFalse(LoginThrottle.objects.filter(failures__gt=0).exists())
        response=self.client.post(reverse('login'),{'username':'student','password':'TestingPassword#57'})
        self.assertRedirects(response,reverse('dashboard'))
    def test_csrf_and_logout_method(self):
        self.login_as('student')
        self.assertEqual(self.client.get(reverse('logout')).status_code,405)
        csrf=Client(enforce_csrf_checks=True)
        csrf.force_login(self.student)
        self.assertEqual(csrf.post(reverse('notifications_read_all')).status_code,403)
        self.assertEqual(csrf.post(reverse('login'),{'username':'x','password':'y'}).status_code,403)
    def test_password_reset_email(self):
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response=self.client.post(reverse('password_reset'),{'email':self.student.email})
            self.assertEqual(response.status_code,302)
            self.assertEqual(len(mail.outbox),1)
            self.assertIn('/accounts/password/reset/',mail.outbox[0].body)
    def test_resource_upload_search_and_notification(self):
        self.login_as('faculty')
        response=self.client.post(reverse('resource_create'),{'title':'Normalization','subject':'DBMS','category':'notes','description':'Normal forms','file':SimpleUploadedFile('notes.txt',b'Database notes')})
        self.assertRedirects(response,reverse('resources'))
        self.assertEqual(Resource.objects.count(),1)
        self.assertTrue(Notification.objects.filter(recipient=self.student,title='New resource: Normalization').exists())
        self.login_as('student')
        self.assertContains(self.client.get(reverse('resources'),{'q':'Normalization','category':'notes','subject':'DBMS','sort':'title'}),'Normalization')
        self.assertNotContains(self.client.get(reverse('resources'),{'q':'unmatched'}),'Normal forms')
    def test_reject_fake_pdf_and_html(self):
        self.login_as('faculty')
        for filename in ['fake.pdf','attack.html']:
            response=self.client.post(reverse('resource_create'),{'title':'Bad file','subject':'CS','category':'notes','file':SimpleUploadedFile(filename,b'<script>alert(1)</script>')})
            self.assertEqual(response.status_code,200)
            self.assertEqual(Resource.objects.count(),0)
    def test_oversized_and_binary_txt_rejected(self):
        for f in [SimpleUploadedFile('big.txt',b'x'*(10*1024*1024+1)),SimpleUploadedFile('binary.txt',b'\xff\x00')]:
            form=ResourceForm(data={'title':'x','subject':'x','category':'notes'},files={'file':f})
            self.assertFalse(form.is_valid())
        self.assertEqual(self.client.post(reverse('login'),{},CONTENT_LENGTH=str(13*1024*1024)).status_code,413)
    def test_download_authenticated_and_counted(self):
        r=self.resource()
        self.assertEqual(self.client.post(reverse('resource_download',args=[r.pk])).status_code,302)
        self.login_as('student')
        self.assertEqual(self.client.get(reverse('resource_download',args=[r.pk])).status_code,405)
        response=self.client.post(reverse('resource_download',args=[r.pk]))
        self.assertEqual(response.status_code,200)
        self.assertEqual(b''.join(response.streaming_content),b'Knowledge')
        self.assertIn('attachment;',response['Content-Disposition'])
        r.refresh_from_db()
        self.assertEqual(r.download_count,1)
        self.assertEqual(Download.objects.filter(resource=r,user=self.student).count(),1)
        self.assertEqual(self.client.get('/media/'+r.file.name).status_code,404)
    def test_missing_resource_does_not_increment(self):
        r=self.resource();r.file.delete(save=False)
        self.login_as('student')
        self.assertEqual(self.client.post(reverse('resource_download',args=[r.pk])).status_code,404)
        r.refresh_from_db();self.assertEqual(r.download_count,0)
    def test_notifications_are_private_and_mutations_post_only(self):
        n=Notification.objects.create(recipient=self.student,title='Private notice')
        self.login_as('other_student')
        self.assertNotContains(self.client.get(reverse('notifications')),'Private notice')
        self.assertEqual(self.client.post(reverse('notification_read',args=[n.pk])).status_code,404)
        self.login_as('student')
        self.assertContains(self.client.get(reverse('notifications')),'Private notice')
        self.assertEqual(self.client.get(reverse('notification_read',args=[n.pk])).status_code,405)
        self.client.post(reverse('notification_read',args=[n.pk]))
        n.refresh_from_db();self.assertIsNotNone(n.read_at)
    def test_notification_open_redirect_blocked(self):
        self.login_as('student')
        for link in ['https://example.org','//example.org','/\\example.org']:
            n=Notification.objects.create(recipient=self.student,title='Notice',link=link)
            self.assertRedirects(self.client.post(reverse('notification_read',args=[n.pk])),reverse('notifications'))
    def test_announcement_audience(self):
        Announcement.objects.create(author=self.director,title='Directors only private',content='private',audience='director')
        self.login_as('student')
        self.assertNotContains(self.client.get(reverse('announcements')),'Directors only private')
        self.assertNotContains(self.client.get(reverse('dashboard')),'Directors only private')
        self.login_as('faculty')
        response=self.client.post(reverse('announcement_create'),{'title':'Oops','content':'test','audience':'director'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(Announcement.objects.count(),1)
    def test_create_quiz_formset(self):
        self.login_as('faculty')
        page = self.client.get(reverse('quiz_create'))
        for field in ['is_active', 'require_name', 'require_roll', 'require_email', 'require_class']:
            self.assertNotContains(page, f'name="{field}"')
        data={'title':'New quiz','subject':'Python','starts_at':(timezone.localtime()-timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
         'expiry_time':(timezone.localtime()+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
         'questions-TOTAL_FORMS':'1','questions-INITIAL_FORMS':'0','questions-MIN_NUM_FORMS':'1','questions-MAX_NUM_FORMS':'50',
         'questions-0-text':'Which?','questions-0-option_a':'a','questions-0-option_b':'b','questions-0-option_c':'c','questions-0-option_d':'d','questions-0-correct':['A']}
        response=self.client.post(reverse('quiz_create'),data)
        self.assertRedirects(response,reverse('quizzes'))
        quiz=Quiz.objects.get(title='New quiz')
        self.assertTrue(all([quiz.is_active, quiz.require_name, quiz.require_roll, quiz.require_email, quiz.require_class]))
        self.assertEqual(len(quiz.code),6);self.assertEqual(quiz.questions.count(),1)
        self.assertTrue(Notification.objects.filter(recipient=self.student,title='New quiz: New quiz').exists())
    def test_quiz_rejects_empty_questions(self):
        self.login_as('faculty')
        data={'title':'No questions','subject':'CS','starts_at':timezone.now().isoformat(),'expiry_time':(timezone.now()+timedelta(days=1)).isoformat(),
              'questions-TOTAL_FORMS':'0','questions-INITIAL_FORMS':'0'}
        self.client.post(reverse('quiz_create'),data)
        self.assertFalse(Quiz.objects.exists())
    def test_quiz_scoring_and_duplicate_submission(self):
        quiz,q=self.make_quiz();self.login_as('student')
        response=self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':str(q.options.get(is_correct=True).pk),'score':'999','student':self.users['other_student'].pk})
        self.assertRedirects(response,reverse('quiz_result',args=[quiz.pk]))
        s=Submission.objects.get();self.assertEqual(s.score,1);self.assertEqual(s.total,1);self.assertEqual(s.student,self.student)
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':str(q.options.filter(is_correct=False).first().pk)})
        self.assertEqual(Submission.objects.count(),1)
        self.assertEqual(Submission.objects.get().score,1)
    def test_answers_withheld_until_close(self):
        quiz,q=self.make_quiz();self.login_as('student')
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':str(q.options.get(is_correct=True).pk)})
        self.assertNotContains(self.client.get(reverse('quiz_result',args=[quiz.pk])),'Secret correct option B')
        Quiz.objects.filter(pk=quiz.pk).update(expiry_time=timezone.now()-timedelta(minutes=1))
        self.assertContains(self.client.get(reverse('quiz_result',args=[quiz.pk])),'Secret correct option B')
    def test_incomplete_quiz_is_not_submitted(self):
        quiz,q=self.make_quiz();self.login_as('student')
        response=self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{})
        self.assertContains(response,'answer every question')
        self.assertFalse(Submission.objects.exists())
    def test_closed_upcoming_and_unpublished_quizzes(self):
        self.login_as('student')
        for start,end,published in [(-2,-1,True),(1,2,True),(-1,1,False)]:
            quiz,q=self.make_quiz(starts_at=timezone.now()+timedelta(hours=start),expiry_time=timezone.now()+timedelta(hours=end),is_active=published)
            response=self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':str(q.options.get(is_correct=True).pk)})
            self.assertIn(response.status_code,[302,404]);self.assertFalse(Submission.objects.exists())
    def test_other_faculty_cannot_manage_quiz(self):
        quiz,q=self.make_quiz();self.login_as('other_faculty')
        self.assertEqual(self.client.post(reverse('quiz_toggle',args=[quiz.pk])).status_code,403)
        self.assertEqual(self.client.get(reverse('quiz_result',args=[quiz.pk])).status_code,403)
        self.assertEqual(self.client.get(reverse('leaderboard',args=[quiz.pk])).status_code,403)
    def test_students_only_see_their_submission_details(self):
        quiz,q=self.make_quiz();self.login_as('student')
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':str(q.options.get(is_correct=True).pk)})
        self.login_as('other_student')
        response=self.client.get(reverse('quiz_result',args=[quiz.pk]))
        self.assertEqual(list(response.context['submissions']),[])
    def test_complaint_creation_and_status_history(self):
        self.login_as('student')
        response=self.client.post(reverse('complaint_create'),{'faculty':Faculty.objects.get(user=self.faculty).pk,'title':'Lab','body':'Concern','student':self.users['other_student'].pk,'status':'resolved'})
        c=Complaint.objects.get();self.assertEqual(c.student.user,self.student);self.assertEqual(c.status,'pending')
        self.assertEqual(c.events.count(),1)
        self.login_as('faculty')
        self.client.post(reverse('complaint_detail',args=[c.pk]),{'message':'Investigating','status':'resolved'})
        c.refresh_from_db();self.assertEqual(c.status,'in_progress')
        self.login_as('director')
        self.client.post(reverse('complaint_detail',args=[c.pk]),{'message':'Fixed','status':'resolved'})
        c.refresh_from_db();self.assertEqual(c.status,'resolved');self.assertEqual(c.events.count(),3)
    def test_complaint_object_access(self):
        c=self.complaint()
        for role in ['other_student','other_faculty']:
            self.login_as(role)
            self.assertEqual(self.client.get(reverse('complaint_detail',args=[c.pk])).status_code,404)
            self.assertEqual(self.client.post(reverse('complaint_detail',args=[c.pk]),{'message':'unauthorized'}).status_code,404)
        self.assertEqual(c.events.count(),0)
    def test_feedback_upsert_and_range(self):
        self.login_as('student')
        for score in [2,5]:
            self.client.post(reverse('feedback'),{'faculty':Faculty.objects.get(user=self.faculty).pk,'rating':score,'comment':'Thanks'})
        self.assertEqual(Feedback.objects.count(),1);self.assertEqual(Feedback.objects.get().rating,5)
        response=self.client.post(reverse('feedback'),{'faculty':Faculty.objects.get(user=self.faculty).pk,'rating':6})
        self.assertEqual(response.status_code,200);self.assertEqual(Feedback.objects.get().rating,5)
    def test_feedback_db_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Feedback.objects.create(student=self.student,faculty=Faculty.objects.get(user=self.faculty),rating=0,student_name='Student',student_email=self.student.email)
    def test_doubt_answer_permission_and_notification(self):
        self.login_as('student')
        self.client.post(reverse('doubt_create'),{'faculty':Faculty.objects.get(user=self.faculty).pk,'subject':'Python','doubt':'Why use functions?'})
        d=Doubt.objects.get()
        self.login_as('other_faculty')
        self.assertEqual(self.client.post(reverse('doubt_answer',args=[d.pk]),{'answer':'bad'}).status_code,404)
        self.login_as('faculty')
        self.client.post(reverse('doubt_answer',args=[d.pk]),{'answer':'Functions help reuse code.'})
        d.refresh_from_db();self.assertEqual(d.answer,'Functions help reuse code.');self.assertIsNotNone(d.answered_at)
        self.assertTrue(Notification.objects.filter(recipient=self.student,title='Your doubt has been answered').exists())
        self.login_as('other_student')
        self.assertNotContains(self.client.get(reverse('doubts')),'Why use functions?')
    def test_account_creation_and_deactivation(self):
        self.login_as('director')
        response=self.client.post(reverse('account_create'),{'username':'newfaculty','first_name':'Teacher','email':'teacher@example.test','department':'CSE','role':'faculty','password1':'UniqueStrongPassword#529','password2':'UniqueStrongPassword#529'})
        self.assertRedirects(response,reverse('accounts'))
        u=get_user_model().objects.get(username='newfaculty');self.assertEqual(u.profile.role,'faculty')
        self.client.post(reverse('account_toggle',args=[u.pk]));u.refresh_from_db();self.assertFalse(u.is_active)
        self.client.logout();self.assertFalse(self.client.login(username='newfaculty',password='UniqueStrongPassword#529'))

    def test_profile_edit_for_all_roles(self):
        for role in ['student', 'faculty', 'director']:
            with self.subTest(role=role):
                self.login_as(role)
                page = self.client.get(reverse('profile_edit'))
                self.assertEqual(page.status_code, 200)
                self.assertContains(page, 'Save changes')
                payload = {'username': role + '_corrected', 'first_name': 'Corrected Name',
                           'email': role + '-corrected@example.test', 'department': 'Physics',
                           'phone': '9876543210', 'enrollment': 'ST123', 'year': '2',
                           'semester': '4', 'section': 'B', 'role': 'director',
                           'is_superuser': 'True', 'user_id': self.faculty.pk}
                response = self.client.post(reverse('profile_edit'), payload)
                self.assertRedirects(response, reverse('profile_edit'))
                user = get_user_model().objects.get(pk=self.users[role].pk)
                self.assertEqual(user.first_name, 'Corrected Name')
                self.assertEqual(user.profile.role, role)
                self.assertFalse(user.is_superuser)
                self.assertEqual(user.profile.department, 'Physics')
                self.assertTrue(user.check_password('TestingPassword#57'))
                if role == 'student':
                    item = Student.objects.get(user=user)
                    self.assertEqual((item.sname, item.sen, item.sem), ('Corrected Name', 'ST123', '4'))
                    self.assertEqual(AuthenticatedStudent.objects.get(user=user).name, 'Corrected Name')
                elif role == 'faculty':
                    self.assertEqual(Faculty.objects.get(user=user).fname, 'Corrected Name')
                    self.assertEqual(Teacher.objects.get(user=user).name, 'Corrected Name')
                else:
                    self.assertEqual(user.legacy_director.dname, 'Corrected Name')
                self.assertContains(self.client.get(reverse('dashboard')), 'Corrected Name')

    def test_profile_edit_rejects_duplicate_email_and_username(self):
        self.login_as('student')
        response = self.client.post(reverse('profile_edit'), {
            'username': self.faculty.username, 'first_name': 'Changed',
            'email': self.faculty.email, 'department': 'Physics', 'phone': '1234567890123'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors.get('username'))
        self.assertTrue(response.context['form'].errors.get('email'))
        self.assertTrue(response.context['form'].errors.get('phone'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Student')

    def test_profile_edit_requires_login_and_csrf(self):
        self.assertEqual(self.client.get(reverse('profile_edit')).status_code, 302)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.director)
        self.assertEqual(client.post(reverse('profile_edit'), {}).status_code, 403)
    def test_staff_creation_forms_exclude_student_details(self):
        self.login_as('director')
        for role in ['faculty','director']:
            for url in [reverse(role+'_registration')+'?role=student',reverse('account_create')+'?role='+role]:
                with self.subTest(role=role,url=url):
                    response=self.client.get(url)
                    self.assertContains(response,f'<h1>Create {role} account</h1>',html=True)
                    self.assertContains(response,f'<input type="hidden" name="role" value="{role}" id="id_role">',html=True)
                    for name in ['enrollment','year','semester','section']:
                        self.assertNotContains(response,f'name="{name}"')
                    for name in ['username','first_name','email','department','phone','password1','password2']:
                        self.assertContains(response,f'name="{name}"')
        self.assertContains(self.client.get(reverse('account_create')),'Create faculty account')
    def test_staff_registration_fixes_role_and_saves_contact_details(self):
        self.login_as('director')
        for role in ['faculty','director']:
            with self.subTest(role=role):
                response=self.client.post(reverse(role+'_registration'),{
                    'username':'new_'+role,'first_name':'Campus Staff','email':role+'-new@example.test',
                    'department':'CSE','phone':'+919876543210','role':'student',
                    'enrollment':'SHOULD-BE-IGNORED','year':'4','semester':'8','section':'A',
                    'password1':'UniqueStrongPassword#529','password2':'UniqueStrongPassword#529'})
                self.assertRedirects(response,reverse('accounts'))
                user=get_user_model().objects.get(username='new_'+role)
                self.assertEqual(user.profile.role,role)
                self.assertEqual(user.profile.enrollment,'')
                self.assertEqual(user.profile.department,'CSE')
                self.assertFalse(Student.objects.filter(user=user).exists())
                legacy=getattr(user,'legacy_'+role)
                self.assertEqual(getattr(legacy,'fphone' if role=='faculty' else 'dphone'),'+919876543210')
    def test_director_created_student_requires_and_saves_academic_details(self):
        self.login_as('director')
        url=reverse('account_create')+'?role=student'
        data={'role':'student','username':'new_student','first_name':'New Student',
              'email':'student-new@example.test','department':'CSE','phone':'9876543210',
              'year':'2','semester':'3','section':'B',
              'password1':'UniqueStrongPassword#529','password2':'UniqueStrongPassword#529'}
        response=self.client.post(url,data)
        self.assertContains(response,'Create student account')
        self.assertIn('enrollment',response.context['form'].errors)
        self.assertFalse(get_user_model().objects.filter(username='new_student').exists())
        data['enrollment']='CS002'
        self.assertRedirects(self.client.post(url,data),reverse('accounts'))
        user=get_user_model().objects.get(username='new_student')
        self.assertEqual(user.profile.role,'student')
        self.assertEqual(user.profile.enrollment,'CS002')
        student=Student.objects.get(user=user)
        self.assertEqual((student.sen,student.course,student.sphone,student.year,student.sem,student.section),
                         ('CS002','CSE','9876543210','2','3','B'))
    def test_director_cannot_deactivate_self(self):
        self.login_as('director');self.client.post(reverse('account_toggle',args=[self.director.pk]))
        self.director.refresh_from_db();self.assertTrue(self.director.is_active)
    def test_report_export_alphabetical_and_csv_safe(self):
        self.login_as('director')
        for title in ['Zebra','=HYPERLINK("bad")','Alpha']:
            Resource.objects.create(title=title,subject='CS',category='notes',file='placeholder.txt',original_name='placeholder.txt',uploaded_by=self.faculty)
        response=self.client.get(reverse('report_export',args=['resources']))
        rows=list(csv.reader(io.StringIO(response.content.decode('utf-8-sig'))))
        self.assertEqual(rows[1][0], '\'=HYPERLINK("bad")')
        self.assertEqual(rows[2][0],'Alpha');self.assertEqual(rows[3][0],'Zebra')
        for kind in ['feedback','complaints','quizzes']:
            self.assertEqual(self.client.get(reverse('report_export',args=[kind])).status_code,200)
    def test_dashboard_no_removed_performance_sections(self):
        self.login_as('director')
        response=self.client.get(reverse('dashboard'))
        self.assertContains(response,'Total resources');self.assertNotContains(response,'Teacher Performance');self.assertNotContains(response,'Student Performance')
    def test_legacy_import_dry_run_and_hashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'legacy.sqlite3'
            with closing(sqlite3.connect(p)) as db:
                db.execute('CREATE TABLE ClassApp_student (id INTEGER, sname TEXT, sen TEXT, semail TEXT, unm TEXT, pw TEXT)')
                db.execute('INSERT INTO ClassApp_student VALUES (1,?,?,?,?,?)',('Legacy Student','EN001','legacy@example.test','legacy','old-password'))
                db.commit()
            before=p.read_bytes()
            call_command('import_legacy_students',str(p),stdout=io.StringIO())
            self.assertFalse(get_user_model().objects.filter(username='legacy').exists())
            call_command('import_legacy_students',str(p),apply=True,stdout=io.StringIO())
            user=get_user_model().objects.get(username='legacy')
            self.assertTrue(user.check_password('old-password'));self.assertNotEqual(user.password,'old-password')
            self.assertEqual(user.profile.enrollment,'EN001');self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(CommandError):
                call_command('import_legacy_students',str(p),apply=True,stdout=io.StringIO())
    def test_director_bootstrap_command(self):
        from unittest.mock import patch
        with patch('ClassApp.management.commands.create_director.getpass.getpass',return_value='UniqueBootstrapPassword#71'):
            call_command('create_director',username='bootstrap',email='bootstrap@example.test',name='Campus Director',stdout=io.StringIO())
        user=get_user_model().objects.get(username='bootstrap')
        self.assertEqual(user.profile.role,'director');self.assertTrue(user.check_password('UniqueBootstrapPassword#71'))
        self.assertFalse(user.is_staff);self.assertFalse(user.is_superuser)
    def test_password_change_invalidates_old_password(self):
        self.login_as('student')
        response=self.client.post(reverse('password_change'),{'old_password':'TestingPassword#57','new_password1':'ChangedStrongPassword#89','new_password2':'ChangedStrongPassword#89'})
        self.assertRedirects(response,reverse('password_change_done'))
        self.student.refresh_from_db();self.assertTrue(self.student.check_password('ChangedStrongPassword#89'))
        self.assertFalse(self.student.check_password('TestingPassword#57'))
    def test_deactivation_revokes_existing_session(self):
        client=Client();client.force_login(self.student)
        self.student.is_active=False;self.student.save(update_fields=['is_active'])
        self.assertEqual(client.get(reverse('dashboard')).status_code,302)
    def test_original_role_urls_enforce_correct_role(self):
        self.login_as('student')
        for name in ['faculty_dashboard','Director_dashboard','faculty_registration','director_registration']:
            self.assertEqual(self.client.get(reverse(name)).status_code,403)
        self.assertEqual(self.client.get(reverse('student_dashboard')).status_code,200)
        self.assertEqual(self.client.get(reverse('teacher_quiz_list')).status_code,200)
        # The shared listing still filters according to the authenticated role.
        self.assertEqual(self.client.get(reverse('index')).status_code,200)
    def test_original_quiz_answer_and_detail_tables_are_written(self):
        quiz,q=self.make_quiz();self.login_as('student')
        correct=q.options.get(is_correct=True)
        self.client.post(reverse('attempt_quiz',args=[quiz.pk]),{f'q_{q.pk}':correct.pk})
        s=Submission.objects.get()
        self.assertEqual(s.answers.get().selected_options.get(),correct)
        self.assertEqual(SubmissionDetail.objects.get(submission=s).selected_options.get(),correct)
        self.assertEqual(SubmissionDetail.objects.get(submission=s).score,1)
    def test_multi_select_requires_exact_correct_set(self):
        quiz,q=self.make_quiz();q.is_multiple=True;q.save(update_fields=['is_multiple'])
        extra=q.options.filter(is_correct=False).first();extra.is_correct=True;extra.save(update_fields=['is_correct'])
        self.login_as('student')
        selected=[o.pk for o in q.options.filter(is_correct=True)]
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':selected})
        self.assertEqual(Submission.objects.get().score,1)
        self.login_as('other_student')
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':[selected[0]]})
        self.assertEqual(Submission.objects.get(student=self.users['other_student']).score,0)
    def test_forged_options_from_other_question_rejected(self):
        quiz,q=self.make_quiz();other,q2=self.make_quiz();self.login_as('student')
        response=self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':q2.options.first().pk})
        self.assertEqual(response.status_code,200);self.assertFalse(Submission.objects.exists())
    def test_required_original_quiz_details_are_validated(self):
        quiz,q=self.make_quiz(require_name=True,require_roll=True,require_email=True,require_class=True)
        self.login_as('student')
        response=self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':q.options.get(is_correct=True).pk})
        self.assertEqual(response.status_code,200);self.assertFalse(Submission.objects.exists())
        data={f'q_{q.pk}':q.options.get(is_correct=True).pk,'student_name':'Student','roll_no':'CS001','email':'student@example.test','course':'CSE','year':'4','semester':'7','section':'B','batch':'2023–2027'}
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),data)
        self.assertEqual(Submission.objects.get().roll_no,'CS001')
        self.assertEqual(Submission.objects.get().academic_details, {'course':'CSE','year':'4','semester':'7','section':'B','batch':'2023–2027'})

    def test_quiz_attempt_autofills_separate_academic_details_and_dates(self):
        Profile.objects.filter(user=self.student).update(enrollment='CS456', department='CSE')
        Student.objects.filter(user=self.student).update(year='4', sem='7', section='B', batch='2023–2027')
        quiz, question = self.make_quiz()
        self.login_as('student')
        response = self.client.get(reverse('quiz_attempt', args=[quiz.pk]))
        self.assertEqual(response.status_code, 200)
        form = response.context['info']
        expected = {'student_name':'Student', 'email':self.student.email, 'roll_no':'CS456',
                    'course':'CSE', 'year':'4', 'semester':'7', 'section':'B', 'batch':'2023–2027'}
        for field, value in expected.items():
            self.assertEqual(form[field].value(), value)
        self.assertNotContains(response, 'name="class_div"')
        self.assertContains(response, 'Quiz launch date and time:')
        self.assertContains(response, 'Submission deadline:')
        data = dict(expected)
        data[f'q_{question.pk}'] = question.options.get(is_correct=True).pk
        self.assertRedirects(self.client.post(reverse('quiz_attempt', args=[quiz.pk]), data), reverse('quiz_result', args=[quiz.pk]))
        submission = Submission.objects.get(student=self.student)
        self.assertEqual(submission.academic_details['section'], 'B')
        self.assertEqual(submission.academic_details['batch'], '2023–2027')
    def test_invalid_legacy_quiz_cannot_be_attempted_or_published(self):
        quiz,q=self.make_quiz();q.options.update(is_correct=False)
        self.login_as('student')
        self.assertRedirects(self.client.get(reverse('quiz_attempt',args=[quiz.pk])),reverse('quizzes'))
        self.assertFalse(Submission.objects.exists())
        quiz.is_active=False;quiz.save(update_fields=['is_active']);self.login_as('faculty')
        self.client.post(reverse('quiz_toggle',args=[quiz.pk]));quiz.refresh_from_db();self.assertFalse(quiz.is_active)
    def test_private_original_doubt_attachment(self):
        d=Doubt.objects.create(student=self.student,student_name='Student',student_email=self.student.email,faculty=Faculty.objects.get(user=self.faculty),doubt='Private question',attachment=SimpleUploadedFile('private.txt',b'private content'))
        url=reverse('attachment_download',args=['doubt',d.pk])
        for role in ['other_student','other_faculty']:
            self.login_as(role);self.assertEqual(self.client.post(url).status_code,404)
        self.login_as('student');response=self.client.post(url)
        self.assertEqual(b''.join(response.streaming_content),b'private content')
    def test_original_announcement_upload_and_audience_download(self):
        self.login_as('faculty')
        response=self.client.post(reverse('announcement_create'),{'title':'Attached notes','content':'Read these notes','audience':'student','document':SimpleUploadedFile('notes.txt',b'original document support')})
        self.assertRedirects(response,reverse('announcements'))
        a=Announcement.objects.get();self.assertEqual(a.posted_by.user,self.faculty)
        self.login_as('student')
        response=self.client.post(reverse('attachment_download',args=['announcement',a.pk]))
        self.assertEqual(b''.join(response.streaming_content),b'original document support')
    def test_score_url_checks_original_submission_id(self):
        quiz,q=self.make_quiz();self.login_as('student')
        self.client.post(reverse('quiz_attempt',args=[quiz.pk]),{f'q_{q.pk}':q.options.get(is_correct=True).pk})
        s=Submission.objects.get();self.login_as('other_student')
        self.assertEqual(self.client.get(reverse('view_score',args=[s.pk])).status_code,403)
        self.login_as('other_faculty')
        self.assertEqual(self.client.get(reverse('view_score',args=[s.pk])).status_code,403)
    def test_student_academic_fields_are_preserved(self):
        self.client.post(reverse('register'),{'username':'academic','first_name':'Academic Student','email':'academic@example.test','enrollment':'EN101','department':'CSE','phone':'9876543210','year':'3','semester':'5','section':'A','password1':'UniqueStrongPassword#529','password2':'UniqueStrongPassword#529'})
        record=Student.objects.get(user__username='academic')
        self.assertEqual((record.sen,record.course,record.year,record.sem,record.section),('EN101','CSE','3','5','A'))
    def test_plaintext_fields_no_longer_exist(self):
        from .models import Director
        for model in [Student,Faculty,Director]:
            self.assertNotIn('pw',[f.name for f in model._meta.fields])

class LegacyMigrationTests(TestCase):
    def test_populated_original_0006_database_upgrades_without_losing_records(self):
        """Use an isolated database because the password-removal migration is intentionally irreversible."""
        import subprocess
        import secrets
        project=Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            env=os.environ.copy()
            env.update(DATABASE_URL='sqlite:///'+str(Path(tmp)/'legacy.sqlite3'),DEBUG='True',SECRET_KEY=secrets.token_urlsafe(64))
            def run(*args):
                result=subprocess.run([sys.executable,*args],cwd=project,env=env,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
                return result
            run('manage.py','migrate','ClassApp','0006','--noinput')
            run('manage.py','migrate','auth','--noinput')
            run('manage.py','migrate','sessions','--noinput')
            fixture=r'''
import os,django
os.environ['DJANGO_SETTINGS_MODULE']='Classroom.settings';django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
apps=MigrationExecutor(connection).loader.project_state([('ClassApp','0006_authenticatedstudent_teacher_complaint'),('auth','0012_alter_user_first_name_max_length'),('sessions','0001_initial')]).apps
def M(name):return apps.get_model('ClassApp',name)
User=apps.get_model('auth','User')
oldteacher=User.objects.create(id=7,username='shared',password=make_password('ExistingPassword#42'),email='oldteacher@example.test')
oldstudent=User.objects.create(id=8,username='existingstudent',password=make_password('ExistingStudent#42'),email='existingstudent@example.test')
student=M('Student').objects.create(id=11,sname='Legacy Student',sen='EN001',sphone='1234567890',semail='legacy@example.test',unm='legacy_student',pw='LegacyStudent#42',course='CSE',year='3',sem='5',section='A')
faculty=M('Faculty').objects.create(id=22,fname='Legacy Faculty',fphone='',femail='faculty@example.test',unm='shared',pw=make_password('LegacyFaculty#42'))
M('Director').objects.create(id=33,dname='Legacy Director',dphone='',demail='director@example.test',unm='legacy_director',pw='LegacyDirector#42')
q=M('Quiz').objects.create(id=44,title='Original multiple choice',expiry_time=timezone.now()+timedelta(days=2),faculty=faculty,is_active=True,require_roll=True)
question=M('Question').objects.create(id=45,quiz=q,text='Choose both correct options',is_multiple=True,image='quiz_images/original.png')
a=M('Option').objects.create(id=46,question=question,text='Correct A',is_correct=True)
b=M('Option').objects.create(id=47,question=question,text='Correct B',is_correct=True)
M('Option').objects.create(id=48,question=question,text='Wrong',is_correct=False)
for pk in [55,56]:
 submission=M('Submission').objects.create(id=pk,quiz=q,student_name='Legacy Student',roll_no='EN001',email='legacy@example.test',score=1)
 answer=M('SubmissionAnswer').objects.create(submission=submission,question=question);answer.selected_options.add(a,b)
 detail=M('SubmissionDetail').objects.create(submission=submission,quiz=q,question=question,student_name='Legacy Student',score=1);detail.selected_options.add(a,b)
for pk in [66,67]:M('Rating').objects.create(id=pk,faculty=faculty,student_name='Legacy Student',student_email='legacy@example.test',rating=4)
M('Doubt').objects.create(id=77,faculty=faculty,student_name='Legacy Student',student_email='legacy@example.test',doubt='Original doubt',attachment='attachments/original.txt')
M('Announcement').objects.create(id=88,title='Original announcement',content='Original body',posted_by=faculty,document='announcements/original.pdf')
s=M('AuthenticatedStudent').objects.create(user=oldstudent,name='Existing Student')
t=M('Teacher').objects.create(user=oldteacher,name='Existing Teacher')
M('Complaint').objects.create(id=99,student=s,teacher=t,text='Original complaint text',teacher_reply='Original teacher reply',status='Replied')
apps.get_model('sessions','Session').objects.create(session_key='legacy-session',session_data='legacy',expire_date=timezone.now()+timedelta(days=1))
M('PasswordResetOTP').objects.create(email='legacy@example.test',otp='123456')
'''
            run('-c',fixture)
            run('manage.py','migrate','--noinput')
            verify=r'''
import os,django
os.environ['DJANGO_SETTINGS_MODULE']='Classroom.settings';django.setup()
from ClassApp.models import *
from django.contrib.auth import get_user_model
from django.test import Client
from django.db import connection
from django.contrib.sessions.models import Session
student=Student.objects.get(pk=11);faculty=Faculty.objects.get(pk=22);director=Director.objects.get(pk=33)
assert student.user.check_password('LegacyStudent#42')
assert faculty.user.check_password('LegacyFaculty#42')
assert director.user.check_password('LegacyDirector#42')
assert faculty.user_id!=7 and faculty.user.username!='shared'
assert get_user_model().objects.get(pk=7).check_password('ExistingPassword#42')
assert student.user.profile.role=='student' and faculty.user.profile.role=='faculty' and director.user.profile.role=='director'
assert student.sem=='5' and student.section=='A'
q=Quiz.objects.get(pk=44);assert q.faculty_id==22 and q.creator_id==faculty.user_id and len(q.code)==6
assert Question.objects.get(pk=45).is_multiple and Question.objects.get(pk=45).image.name=='quiz_images/original.png'
assert Option.objects.filter(question_id=45).count()==3
assert Submission.objects.filter(quiz=q).count()==2
assert Submission.objects.filter(quiz=q,student=student.user).count()==1
assert set(Submission.objects.get(pk=55).review[0]['selected'])=={46,47}
assert SubmissionAnswer.objects.count()==2 and SubmissionDetail.objects.count()==2
assert set(SubmissionDetail.objects.get(submission_id=55).selected_options.values_list('pk',flat=True))=={46,47}
assert Rating.objects.count()==2 and Rating.objects.filter(student=student.user).count()==1
assert Doubt.objects.get(pk=77).student_id==student.user_id and Doubt.objects.get(pk=77).attachment.name=='attachments/original.txt'
assert Announcement.objects.get(pk=88).author_id==faculty.user_id and Announcement.objects.get(pk=88).document.name=='announcements/original.pdf'
c=Complaint.objects.get(pk=99)
assert c.text=='Original complaint text' and c.teacher_reply=='Original teacher reply' and c.status=='in_progress'
assert c.teacher.user_id==7 and c.student.user_id==8 and c.events.count()==2
assert c.events.last().message=='Original teacher reply'
assert not Session.objects.exists() and not PasswordResetOTP.objects.exists()
for model in [Student,Faculty,Director]:
 with connection.cursor() as cursor:columns=connection.introspection.get_table_description(cursor,model._meta.db_table)
 assert 'pw' not in [col.name for col in columns]
client=Client(HTTP_HOST='127.0.0.1')
for user,password in [(student.user,'LegacyStudent#42'),(faculty.user,'LegacyFaculty#42'),(director.user,'LegacyDirector#42')]:
 assert client.login(username=user.username,password=password)
 assert client.get('/dashboard/').status_code==200
 client.logout()
print('Populated legacy upgrade passed')
'''
            run('-c',verify)
