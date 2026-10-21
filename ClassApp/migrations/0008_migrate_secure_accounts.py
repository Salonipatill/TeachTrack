"""Migrate the ORIGINAL data in place, preserving all legacy record IDs and relations."""
from django.db import migrations
from django.contrib.auth.hashers import make_password, identify_hasher
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import secrets

def forwards(apps,schema_editor):
    alias=schema_editor.connection.alias
    def M(name): return apps.get_model('ClassApp',name).objects.using(alias)
    User=apps.get_model('auth','User')
    users=User.objects.using(alias)
    for user in users.all().iterator():
        role='director' if user.is_superuser else 'faculty' if M('Teacher').filter(user_id=user.pk).exists() else 'student'
        M('Profile').get_or_create(user_id=user.pk,defaults={'role':role})
    def name_for(row,role):
        base=(row.unm or '').strip()
        try:UnicodeUsernameValidator()(base)
        except ValidationError:base=''
        if not base:base=f'legacy_{role}_{row.pk}'
        base=base[:140]
        name=base;i=0
        while users.filter(username=name).exists():
            i+=1;name=f'{base[:115]}_{role}_{row.pk}_{i}'
        return name
    for model,role,name_field,email_field in [('Student','student','sname','semail'),('Faculty','faculty','fname','femail'),('Director','director','dname','demail')]:
        for row in M(model).order_by('pk').iterator():
            if row.user_id:continue
            password=row.pw or ''
            if password:
                try:identify_hasher(password)
                except ValueError:password=make_password(password)
            else:password=make_password(None)
            user=users.create(username=name_for(row,role),first_name=getattr(row,name_field)[:150],email=getattr(row,email_field) or '',password=password)
            M('Profile').create(user_id=user.pk,role=role,enrollment=getattr(row,'sen',''),department=getattr(row,'course',''))
            row.user_id=user.pk;row.save(using=alias,update_fields=['user'])
            if role=='student':M('AuthenticatedStudent').get_or_create(user_id=user.pk,defaults={'name':row.sname})
            if role=='faculty':M('Teacher').get_or_create(user_id=user.pk,defaults={'name':row.fname})
    # Only uniquely identified students are linked. Ambiguous historical rows stay visible to directors.
    def student_for(email,roll=''):
        candidates=M('Student').exclude(user_id=None)
        if roll:
            by_roll=list(candidates.filter(sen=roll).values_list('user_id',flat=True).distinct()[:2])
            if len(by_roll)==1:return by_roll[0]
        if not email:return None
        ids=list(candidates.filter(semail__iexact=email).values_list('user_id',flat=True).distinct()[:2])
        return ids[0] if len(ids)==1 else None
    for q in M('Quiz').all().iterator():
        code=f'{q.pk:06X}' if q.pk<16777216 else secrets.token_hex(3).upper()
        while M('Quiz').exclude(pk=q.pk).filter(code=code).exists():code=secrets.token_hex(3).upper()
        q.code=code
        q.starts_at=q.created_at
        faculty=M('Faculty').filter(pk=q.faculty_id).first()
        q.creator_id=faculty.user_id if faculty else None
        q.save(using=alias,update_fields=['code','starts_at','creator'])
    linked=set()
    for s in M('Submission').order_by('-submitted_at','-pk').iterator():
        uid=student_for(s.email,s.roll_no)
        if uid and (s.quiz_id,uid) not in linked:
            s.student_id=uid;linked.add((s.quiz_id,uid))
        questions=list(M('Question').filter(quiz_id=s.quiz_id).order_by('pk'))
        s.total=len(questions)
        review=[]
        for q in questions:
            options=list(M('Option').filter(question_id=q.pk).order_by('pk'))
            answer=M('SubmissionAnswer').filter(submission_id=s.pk,question_id=q.pk).first()
            if not answer:answer=M('SubmissionDetail').filter(submission_id=s.pk,question_id=q.pk).first()
            selected=list(answer.selected_options.using(alias).values_list('pk',flat=True)) if answer else []
            review.append({'question':q.text,'selected':selected,'correct':[o.pk for o in options if o.is_correct],
                           'options':{str(o.pk):o.text for o in options},'selected_text':[o.text for o in options if o.pk in selected],'correct_text':[o.text for o in options if o.is_correct]})
        s.review=review;s.save(using=alias,update_fields=['student','total','review'])
    linked=set()
    for r in M('Rating').order_by('-submitted_at','-pk').iterator():
        uid=student_for(r.student_email)
        if uid and (r.faculty_id,uid) not in linked:
            r.student_id=uid;linked.add((r.faculty_id,uid))
        # Invalid historical ratings are normalized to the nearest valid endpoint.
        r.rating=max(1,min(5,int(r.rating or 1)))
        r.updated_at=r.submitted_at
        r.save(using=alias,update_fields=['student','rating','updated_at'])
    for d in M('Doubt').all().iterator():
        d.student_id=student_for(d.student_email);d.save(using=alias,update_fields=['student'])
    for a in M('Announcement').exclude(posted_by_id=None).iterator():
        faculty=M('Faculty').filter(pk=a.posted_by_id).first()
        a.author_id=faculty.user_id if faculty else None;a.save(using=alias,update_fields=['author'])
    for c in M('Complaint').all().iterator():
        old_status=c.status
        c.status='resolved' if old_status.lower()=='resolved' else 'in_progress' if old_status.lower() in ['replied','in_progress'] else 'pending'
        c.updated_at=c.reply_time or c.created_at
        c.save(using=alias,update_fields=['status','updated_at'])
        student=M('AuthenticatedStudent').get(pk=c.student_id)
        event=M('ComplaintEvent').create(complaint_id=c.pk,author_id=student.user_id,message=c.text,status='pending')
        M('ComplaintEvent').filter(pk=event.pk).update(created_at=c.created_at)
        if c.teacher_reply:
            teacher=M('Teacher').get(pk=c.teacher_id)
            event=M('ComplaintEvent').create(complaint_id=c.pk,author_id=teacher.user_id,message=c.teacher_reply,status=c.status)
            M('ComplaintEvent').filter(pk=event.pk).update(created_at=c.reply_time or c.created_at)
    # Old custom sessions and OTPs must not survive the authentication change.
    apps.get_model('sessions','Session').objects.using(alias).all().delete()
    M('PasswordResetOTP').all().delete()

class Migration(migrations.Migration):
    dependencies=[('ClassApp','0007_secure_academic_modules'),('sessions','0001_initial'),('auth','0012_alter_user_first_name_max_length')]
    operations=[migrations.RunPython(forwards)]
