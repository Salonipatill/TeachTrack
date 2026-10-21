import os
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from ClassApp.models import Profile, Resource, Announcement, Quiz, Question, Rating, Complaint, ComplaintEvent, Doubt, Submission, Faculty, Teacher, AuthenticatedStudent, Option, SubmissionAnswer, SubmissionDetail
from ClassApp.services import notify, ensure_legacy
class Command(BaseCommand):
    help = 'Create local demo accounts and sample data. Set DEMO_PASSWORD in your terminal first.'
    def handle(self,*args,**opts):
        if not settings.DEBUG:
            raise CommandError('Demo data is only allowed with DEBUG=True.')
        password = os.getenv('DEMO_PASSWORD','')
        try:
            validate_password(password)
        except ValidationError as e:
            raise CommandError('Set a strong DEMO_PASSWORD environment variable: '+'; '.join(e.messages))
        User = get_user_model()
        if User.objects.filter(username__in=['demo_director','demo_faculty','demo_student','demo_student2']).exists():
            raise CommandError('Demo users already exist. No changes made.')
        with transaction.atomic():
            users=[]
            for username,name,role in [('demo_director','Saloni','director'),('demo_faculty','Dr. Meera Sharma','faculty'),('demo_student','Zaman','student'),('demo_student2','Aarav','student')]:
                u=User.objects.create_user(username=username,first_name=name,email=f'{username}@example.test',password=password)
                Profile.objects.filter(user=u).update(role=role,department='Computer Science')
                ensure_legacy(u,role)
                users.append(u)
            director,faculty,student,student2=users
            for title,subject,category in [('Database normalization notes','Database Systems','notes'),('Previous year questions · 2025','Python Programming','pyq'),('Assignment 01 · SQL fundamentals','Database Systems','assignment')]:
                r=Resource(title=title,subject=subject,category=category,description='Sample learning material. Replace with your own college resources.',uploaded_by=faculty,original_name='sample-resource.txt')
                r.file.save('sample-resource.txt',ContentFile(f'{title}\n\nTeachTrack demo learning resource.\n'),save=True)
            Announcement.objects.create(author=director,title='Welcome to your academic workspace',content='Find notes, practise with quizzes and keep track of your academic conversations.',audience='all')
            Announcement.objects.create(author=faculty,title='Database Systems: quiz this week',content='Review normalization and SQL fundamentals before attempting the quiz.',audience='student')
            q=Quiz.objects.create(title='Python fundamentals',subject='Python Programming',creator=faculty,faculty=Faculty.objects.get(user=faculty),is_active=True,starts_at=timezone.now()-timedelta(days=1),expiry_time=timezone.now()+timedelta(days=7))
            question=Question.objects.create(quiz=q,text='Which keyword defines a function in Python?')
            options=[Option.objects.create(question=question,text=text,is_correct=correct) for text,correct in [('func',False),('def',True),('function',False),('define',False)]]
            review=[{'question':question.text,'selected':[options[1].pk],'correct':[options[1].pk],'options':{str(o.pk):o.text for o in options},'selected_text':['def'],'correct_text':['def']}]
            submission=Submission.objects.create(quiz=q,student=student2,student_name=student2.first_name,score=1,total=1,review=review)
            answer=SubmissionAnswer.objects.create(submission=submission,question=question);answer.selected_options.add(options[1])
            detail=SubmissionDetail.objects.create(submission=submission,quiz=q,question=question,student_name=student2.first_name,score=1);detail.selected_options.add(options[1])
            Rating.objects.create(student=student,student_name=student.first_name,student_email=student.email,faculty=Faculty.objects.get(user=faculty),rating=5,comment='The practical examples make concepts easy to understand.')
            Rating.objects.create(student=student2,student_name=student2.first_name,student_email=student2.email,faculty=Faculty.objects.get(user=faculty),rating=4,comment='Helpful notes and clear explanations.')
            c=Complaint.objects.create(student=AuthenticatedStudent.objects.get(user=student),teacher=Teacher.objects.get(user=faculty),title='Projector in lab 2 needs attention',text='The projector display flickers during the afternoon lab.',status='in_progress')
            ComplaintEvent.objects.create(complaint=c,author=student,message='Complaint submitted.',status='pending')
            ComplaintEvent.objects.create(complaint=c,author=faculty,message='The maintenance team has been informed.',status='in_progress')
            Doubt.objects.create(student=student,student_name=student.first_name,student_email=student.email,faculty=Faculty.objects.get(user=faculty),subject='Database Systems',doubt='What is the difference between a primary key and a foreign key?')
            notify(users,'Welcome to TeachTrack','Your demo workspace is ready to explore.',reverse('dashboard'))
        self.stdout.write(self.style.SUCCESS('Demo ready: demo_director, demo_faculty, demo_student, demo_student2. Use your DEMO_PASSWORD to sign in.'))
