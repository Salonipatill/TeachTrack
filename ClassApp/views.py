import csv
from .forms import ProfileForm
import hashlib
from datetime import timedelta
from pathlib import Path
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Avg, Count, F, Q
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from .models import (Profile, Resource, Download, Notification, Announcement, Quiz, Question, Submission,
                     Complaint, ComplaintEvent, Rating as Feedback, Doubt, LoginThrottle, Student, Faculty, Teacher, AuthenticatedStudent, Option, SubmissionAnswer, SubmissionDetail)
from .forms import (StudentRegistrationForm, AccountForm, ResourceForm, QuizForm, QuestionFormSet,
                    AnnouncementForm, ComplaintForm, FeedbackForm, DoubtForm, ReplyForm, AnswerForm, NotificationForm, StudentInfoForm, ContactForm)
from .permissions import roles
from .services import notify, audience_users, ensure_legacy

def paginated(request, queryset):
    return Paginator(queryset, 15).get_page(request.GET.get('page'))
def form_page(request, form, title):
    return render(request, 'form.html', {'form':form, 'title':title})
def display_name(user):
    return user.get_full_name() or user.username

def sign_in(request, role=None):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    context = {'form':form, 'login_role':role, 'login_role_label':Profile.Role(role).label if role else ''}
    if request.method == 'POST':
        # Use the trusted peer address, never a client-controlled forwarded header.
        ip = request.META.get('REMOTE_ADDR', '')
        username = request.POST.get('username', '').casefold()[:150]
        keys = [hashlib.sha256(v.encode()).hexdigest() for v in [f'ip:{ip}', f'user:{username}']]
        blocked = False
        with transaction.atomic():
            counters = []
            for key in sorted(keys):
                obj, _ = LoginThrottle.objects.get_or_create(key=key, defaults={'window_start':timezone.now()})
                obj = LoginThrottle.objects.select_for_update().get(pk=obj.pk)
                if obj.window_start < timezone.now() - timedelta(minutes=15):
                    obj.failures = 0
                    obj.window_start = timezone.now()
                    obj.save()
                counters.append(obj)
            blocked = any(c.failures >= 10 for c in counters)
            if not blocked:
                if form.is_valid():
                    user = form.get_user()
                    if role and user.profile.role != role:
                        form.add_error(None, f'Use the {user.profile.get_role_display().lower()} login for this account.')
                    else:
                        LoginThrottle.objects.filter(key=keys[1]).delete()
                        login(request, user)
                        return redirect('dashboard')
                else:
                    for counter in counters:
                        counter.failures = F('failures') + 1
                        counter.save(update_fields=['failures'])
        if blocked:
            form.add_error(None, 'Too many login attempts. Please try again in 15 minutes.')
            return render(request, 'registration/login.html', context, status=429)
    return render(request, 'registration/login.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            notify([user], 'Welcome to TeachTrack', 'Your student account is ready.', reverse('dashboard'))
        login(request, user)
        return redirect('dashboard')
    return form_page(request, form, 'Create your student account')

@login_required
def dashboard(request):
    role=request.user.profile.role;now=timezone.now()
    quizzes=Quiz.objects.all();submissions=Submission.objects.all();complaints=visible_complaints(request.user)
    if role=='student':
        submissions=submissions.filter(student=request.user)
        quizzes=quizzes.filter(is_active=True,starts_at__lte=now,expiry_time__gt=now).exclude(submissions__student=request.user)
        cards=[('Available quizzes',quizzes.count()),('My submissions',submissions.count()),('Total resources',Resource.objects.count()),('Open complaints',complaints.exclude(status='resolved').count())]
    elif role=='faculty':
        quizzes=quizzes.filter(creator=request.user);submissions=submissions.filter(quiz__creator=request.user)
        cards=[('My quizzes',quizzes.count()),('Quiz submissions',submissions.count()),('My resources',Resource.objects.filter(uploaded_by=request.user).count()),('Open complaints',complaints.exclude(status='resolved').count())]
    else:
        cards=[('Students',Profile.objects.filter(role='student',user__is_active=True).count()),('Faculty',Profile.objects.filter(role='faculty',user__is_active=True).count()),('Total resources',Resource.objects.count()),('Open complaints',complaints.exclude(status='resolved').count())]
    students=Profile.objects.filter(role='student',user__is_active=True).count()
    participation=[{'title':q.title,'count':q.attempts,'percentage':min(100,round(q.attempts*100/students)) if students else 0} for q in quizzes.annotate(attempts=Count('submissions')).order_by('-created_at')[:6]]
    ratings=Feedback.objects.all()
    if role=='faculty':ratings=ratings.filter(faculty__user=request.user)
    stats=[{'label':str(i),'count':ratings.filter(rating=i).count()} for i in range(1,6)]
    return render(request,'dashboard.html',{'cards':cards,'participation':participation,
      'status_stats':[{'label':label,'key':key,'count':complaints.filter(status=key).count()} for key,label in Complaint.STATUSES],
      'feedback_stats':stats,'feedback_max':max([x['count'] for x in stats]+[1]),'average_feedback':ratings.aggregate(avg=Avg('rating'))['avg'],
      'announcements':Announcement.objects.filter(Q(audience='all')|Q(audience=role))[:4],
      'recent_resources':Resource.objects.select_related('uploaded_by')[:4],'recent_submissions':submissions.select_related('quiz')[:5]})

@login_required
def resources(request):
    qs = Resource.objects.select_related('uploaded_by')
    q = request.GET.get('q', '').strip()[:150]
    category = request.GET.get('category', '')
    subject = request.GET.get('subject', '').strip()[:100]
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(subject__icontains=q))
    if category:
        qs = qs.filter(category=category)
    if subject:
        qs = qs.filter(subject__iexact=subject)
    if request.GET.get('sort') == 'title':
        qs = qs.order_by('title', 'id')
    return render(request, 'resources.html', {'page_obj':paginated(request, qs), 'q':q, 'category':category, 'subject':subject,
        'categories':Resource.CATEGORIES, 'subjects':Resource.objects.order_by('subject').values_list('subject',flat=True).distinct()})

@roles('faculty', 'director')
def resource_create(request):
    form = ResourceForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            item.original_name = Path(form.cleaned_data['file'].name).name
            item.save()
            notify(audience_users('student'), f'New resource: {item.title}', item.subject, reverse('resources'))
        messages.success(request, 'Resource uploaded successfully.')
        return redirect('resources')
    return form_page(request, form, 'Upload a resource')

@login_required
@require_POST
def resource_download(request, pk):
    item = get_object_or_404(Resource, pk=pk)
    try:
        file = item.file.open('rb')
    except FileNotFoundError:
        raise Http404('This file is unavailable. Contact the uploader.')
    with transaction.atomic():
        Resource.objects.filter(pk=pk).update(download_count=F('download_count')+1)
        Download.objects.create(resource=item, user=request.user)
    response = FileResponse(file, as_attachment=True, filename=item.original_name, content_type='application/octet-stream')
    response['Cache-Control'] = 'private, no-store'
    return response

@login_required
def notifications(request):
    return render(request, 'notifications.html', {'page_obj':paginated(request, request.user.notifications.all())})

@login_required
@require_POST
def notification_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if note.read_at is None:
        note.read_at = timezone.now()
        note.save(update_fields=['read_at'])
    return redirect(note.link if note.link.startswith('/') and not note.link.startswith('//') and '\\' not in note.link else reverse('notifications'))

@login_required
@require_POST
def notifications_read_all(request):
    request.user.notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
    return redirect('notifications')

@roles('faculty', 'director')
def notification_create(request):
    form = NotificationForm(request.POST or None)
    if request.user.profile.role == 'faculty':
        form.fields['audience'].choices = [('student', 'Students')]
    if request.method == 'POST' and form.is_valid():
        notify(audience_users(form.cleaned_data['audience']), form.cleaned_data['title'], form.cleaned_data['message'], reverse('notifications'))
        messages.success(request, 'Notification sent.')
        return redirect('notifications')
    return form_page(request, form, 'Send a notification')

@login_required
def announcements(request):
    qs = Announcement.objects.select_related('author').filter(Q(audience='all') | Q(audience=request.user.profile.role) | Q(author=request.user))
    return render(request, 'announcements.html', {'page_obj':paginated(request, qs)})

@roles('faculty', 'director')
def announcement_create(request):
    form = AnnouncementForm(request.POST or None, request.FILES or None)
    if request.user.profile.role == 'faculty':
        form.fields['audience'].choices = [('student','Students')]
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            item.author = request.user
            if request.user.profile.role == 'faculty': item.posted_by = ensure_legacy(request.user)
            item.save()
            notify(audience_users(item.audience), item.title, item.content[:250], reverse('announcements'))
        messages.success(request, 'Announcement published.')
        return redirect('announcements')
    return form_page(request, form, 'Post an announcement')

@login_required
def quizzes(request):
    role=request.user.profile.role
    qs=Quiz.objects.select_related('creator','faculty').annotate(attempts=Count('submissions')).order_by('-created_at','-id')
    if role=='student':qs=qs.filter(is_active=True)
    elif role=='faculty':qs=qs.filter(creator=request.user)
    code=request.GET.get('code','').strip().upper()[:6]
    if code:qs=qs.filter(code=code)
    return render(request,'quizzes.html',{'page_obj':paginated(request,qs),'my_ids':set(Submission.objects.filter(student=request.user).values_list('quiz_id',flat=True)),'now':timezone.now(),'code':code})

@roles('faculty','director')
def quiz_create(request):
    form=QuizForm(request.POST or None)
    formset=QuestionFormSet(request.POST or None,request.FILES or None,prefix='questions')
    if request.method=='POST' and form.is_valid() and formset.is_valid():
        try:
            with transaction.atomic():
                quiz=form.save(commit=False);quiz.creator=request.user
                if request.user.profile.role=='faculty':quiz.faculty=ensure_legacy(request.user)
                quiz.save()
                for f in formset:
                    if not f.cleaned_data or f.cleaned_data.get('DELETE'):continue
                    data=f.cleaned_data
                    question=Question.objects.create(quiz=quiz,text=data['text'],is_multiple=data['is_multiple'],image=data.get('image'))
                    for key in 'ABCD':
                        text=data.get('option_'+key.lower())
                        if text:Option.objects.create(question=question,text=text,is_correct=key in data['correct'])
                if quiz.is_active:notify(audience_users('student'),f'New quiz: {quiz.title}',f'Code: {quiz.code}',reverse('quizzes'))
        except IntegrityError:form.add_error(None,'A code collision occurred. Please submit again.')
        else:
            messages.success(request,f'Quiz created. Code: {quiz.code}');return redirect('quizzes')
    return render(request,'quiz_create.html',{'form':form,'formset':formset})

@roles('faculty','director')
@require_POST
def quiz_toggle(request,pk):
    with transaction.atomic():
        quiz=get_object_or_404(Quiz.objects.select_for_update(),pk=pk)
        if request.user.profile.role=='faculty' and quiz.creator_id!=request.user.pk:raise PermissionDenied
        if not quiz.is_active and not valid_quiz(quiz):
            messages.error(request,'This legacy quiz has incomplete questions or answer keys. Ask an administrator to correct it before publishing.')
        else:
            quiz.is_active=not quiz.is_active;quiz.save(update_fields=['is_active'])
            if quiz.is_active:notify(audience_users('student'),f'Quiz published: {quiz.title}',f'Code: {quiz.code}',reverse('quizzes'))
    return redirect('quizzes')

@roles('student')
@require_http_methods(['GET','POST'])
def quiz_attempt(request,pk):
    with transaction.atomic():
        quiz=get_object_or_404(Quiz.objects.select_for_update(),pk=pk,is_active=True)
        if Submission.objects.filter(quiz=quiz,student=request.user).exists():return redirect('quiz_result',pk=pk)
        if not quiz.starts_at<=timezone.now()<quiz.expiry_time:
            messages.error(request,'This quiz is not open for submissions.');return redirect('quizzes')
        if not valid_quiz(quiz):
            messages.error(request,'This quiz is incomplete. Contact the faculty member.');return redirect('quizzes')
        questions=list(quiz.questions.prefetch_related('options').all())
        student=ensure_legacy(request.user)
        initial={'student_name':display_name(request.user),'email':request.user.email,
                 'roll_no':request.user.profile.enrollment or student.sen,
                 'course':request.user.profile.department or student.course,
                 'year':student.year,'semester':student.sem,'section':student.section,'batch':student.batch}
        info=StudentInfoForm(request.POST if request.method=='POST' else None,initial=initial)
        for field,required in [('student_name',quiz.require_name),('roll_no',quiz.require_roll),('email',quiz.require_email),('course',quiz.require_class)]:info.fields[field].required=required
        error=None;rows=[]
        for q in questions:
            selected=request.POST.getlist(f'q_{q.pk}')
            rows.append({'question':q,'options':list(q.options.all()),'selected':selected})
        if request.method=='POST':
            valid=info.is_valid()
            for row in rows:
                q=row['question'];allowed={str(o.pk) for o in row['options']};selected=row['selected']
                if not selected or not set(selected)<=allowed or len(selected)!=len(set(selected)) or (not q.is_multiple and len(selected)!=1):valid=False
            if not valid:error='Complete the required details and answer every question using valid options.'
            else:
                review=[];score=0
                for row in rows:
                    q=row['question'];selected=sorted(int(v) for v in row['selected']);correct=sorted(o.pk for o in row['options'] if o.is_correct)
                    score+=selected==correct
                    review.append({'question':q.text,'selected':selected,'correct':correct,'options':{str(o.pk):o.text for o in row['options']},'selected_text':[o.text for o in row['options'] if o.pk in selected],'correct_text':[o.text for o in row['options'] if o.is_correct]})
                try:
                    with transaction.atomic():
                        data=info.cleaned_data
                        academic_details={field:data[field] or initial[field] for field in ['course','year','semester','section','batch']}
                        class_div=' '.join(value for value in academic_details.values() if value)[:50]
                        submission=Submission.objects.create(quiz=quiz,student=request.user,student_name=data['student_name'] or initial['student_name'],email=data['email'] or initial['email'],roll_no=data['roll_no'] or initial['roll_no'],class_div=class_div,academic_details=academic_details,score=score,total=len(questions),review=review)
                        for row,record in zip(rows,review):
                            answer=SubmissionAnswer.objects.create(submission=submission,question=row['question']);answer.selected_options.set(record['selected'])
                            detail=SubmissionDetail.objects.create(quiz=quiz,submission=submission,question=row['question'],student_name=submission.student_name,roll_no=submission.roll_no,email=submission.email,class_div=submission.class_div,score=int(record['selected']==record['correct']))
                            detail.selected_options.set(record['selected'])
                        notify([request.user],f'Quiz submitted: {quiz.title}','Your score is ready.',reverse('quiz_result',args=[pk]))
                except IntegrityError:messages.info(request,'Your submission was already recorded.')
                return redirect('quiz_result',pk=pk)
    return render(request,'quiz_attempt.html',{'quiz':quiz,'rows':rows,'info':info,'error':error})

@login_required
def quiz_result(request,pk):
    quiz=get_object_or_404(Quiz,pk=pk);role=request.user.profile.role
    if role=='faculty' and quiz.creator_id!=request.user.pk:raise PermissionDenied
    qs=quiz.submissions.select_related('student').order_by('student_name','id')
    if role=='student':qs=qs.filter(student=request.user)
    return render(request,'quiz_result.html',{'quiz':quiz,'submissions':qs,'show_answers':role!='student' or timezone.now()>=quiz.expiry_time})

@login_required
def leaderboard(request,pk):
    quiz=get_object_or_404(Quiz,pk=pk);role=request.user.profile.role
    if role=='faculty' and quiz.creator_id!=request.user.pk:raise PermissionDenied
    if role=='student' and not quiz.is_active and not Submission.objects.filter(quiz=quiz,student=request.user).exists():raise PermissionDenied
    # Keep ambiguous historical/anonymous records in staff reports, not a student leaderboard.
    qs=quiz.submissions.filter(student__isnull=False).select_related('student')
    return render(request,'leaderboard.html',{'quiz':quiz,'page_obj':paginated(request,qs)})

def visible_complaints(user):
    qs=Complaint.objects.select_related('student__user','teacher__user')
    if user.profile.role=='student':return qs.filter(student__user=user)
    if user.profile.role=='faculty':return qs.filter(teacher__user=user)
    return qs

@login_required
def complaints(request):
    qs = visible_complaints(request.user)
    status = request.GET.get('status','')
    if status:
        qs = qs.filter(status=status)
    return render(request, 'complaints.html', {'page_obj':paginated(request,qs), 'statuses':Complaint.STATUSES, 'status':status})

@roles('student')
def complaint_create(request):
    form=ComplaintForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            ensure_legacy(request.user)
            faculty=form.cleaned_data['faculty'];ensure_legacy(faculty.user)
            item=Complaint.objects.create(student=AuthenticatedStudent.objects.get(user=request.user),teacher=Teacher.objects.get(user=faculty.user),title=form.cleaned_data['title'],text=form.cleaned_data['body'])
            ComplaintEvent.objects.create(complaint=item,author=request.user,message='Complaint submitted.',status='pending')
            notify(list(audience_users('director'))+[faculty.user],f'New complaint: {item.title}',link=reverse('complaint_detail',args=[item.pk]))
        return redirect('complaint_detail',pk=item.pk)
    return form_page(request,form,'Submit a complaint')

@login_required
def complaint_detail(request,pk):
    item=get_object_or_404(visible_complaints(request.user),pk=pk);role=request.user.profile.role
    form=ReplyForm(request.POST or None)
    if role!='director':form.fields.pop('status')
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            item=Complaint.objects.select_for_update().select_related('student__user','teacher__user').get(pk=pk)
            status=form.cleaned_data.get('status') or item.status if role=='director' else 'in_progress' if role=='faculty' and item.status=='pending' else item.status
            item.status=status;item.updated_at=timezone.now()
            if role=='faculty':item.teacher_reply=form.cleaned_data['message'];item.reply_time=timezone.now()
            item.save(update_fields=['status','updated_at','teacher_reply','reply_time'])
            ComplaintEvent.objects.create(complaint=item,author=request.user,message=form.cleaned_data['message'],status=status)
            recipients=[item.student.user,item.teacher.user]+list(audience_users('director'))
            notify([u for u in recipients if u.pk!=request.user.pk],f'Complaint updated: {item.title}',item.get_status_display(),reverse('complaint_detail',args=[pk]))
        return redirect('complaint_detail',pk=pk)
    return render(request,'complaint_detail.html',{'item':item,'form':form,'events':item.events.select_related('author')})

@login_required
def doubts(request):
    qs=Doubt.objects.select_related('student','faculty__user');role=request.user.profile.role
    if role=='student':qs=qs.filter(student=request.user)
    elif role=='faculty':qs=qs.filter(faculty__user=request.user)
    return render(request,'doubts.html',{'page_obj':paginated(request,qs)})

@roles('student')
def doubt_create(request):
    form=DoubtForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            item=form.save(commit=False);item.student=request.user;item.student_name=display_name(request.user);item.student_email=request.user.email;item.save()
            notify([item.faculty.user],'A student has a doubt',item.subject,reverse('doubts'))
        return redirect('doubts')
    return form_page(request,form,'Ask a doubt')

@roles('faculty')
def doubt_answer(request,pk):
    item=get_object_or_404(Doubt,pk=pk,faculty__user=request.user)
    form=AnswerForm(request.POST or None,initial={'answer':item.answer})
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            item.answer=form.cleaned_data['answer'];item.answered_at=timezone.now();item.save(update_fields=['answer','answered_at'])
            if item.student_id:notify([item.student],'Your doubt has been answered',item.subject,reverse('doubts'))
        return redirect('doubts')
    return form_page(request,form,f'Answer: {item.subject}')

@login_required
def feedback(request):
    role=request.user.profile.role;form=FeedbackForm(request.POST or None) if role=='student' else None
    if request.method=='POST':
        if role!='student':raise PermissionDenied
        if form.is_valid():
            Feedback.objects.update_or_create(student=request.user,faculty=form.cleaned_data['faculty'],defaults={'rating':form.cleaned_data['rating'],'comment':form.cleaned_data['comment'],'student_name':display_name(request.user),'student_email':request.user.email,'updated_at':timezone.now()})
            messages.success(request,'Your feedback has been saved. Submitting again updates your rating.');return redirect('feedback')
    stats=Faculty.objects.filter(user__is_active=True,user__profile__role='faculty')
    if role=='faculty':stats=stats.filter(user=request.user)
    stats=stats.annotate(average_rating=Avg('ratings__rating'),responses=Count('ratings')).order_by('fname','id')
    comments=Feedback.objects.select_related('faculty')
    if role=='student':comments=comments.filter(student=request.user)
    elif role=='faculty':comments=comments.filter(faculty__user=request.user)
    return render(request,'feedback.html',{'form':form,'faculty_stats':stats,'page_obj':paginated(request,comments)})

@login_required
def profile_edit(request):
    form = ProfileForm(request.POST if request.method == 'POST' else None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Your profile has been updated.')
        return redirect('profile_edit')
    return render(request, 'profile.html', {'form': form})


@roles('director')
def accounts(request):
    users = get_user_model().objects.select_related('profile').order_by('first_name','username')
    return render(request, 'accounts.html', {'page_obj':paginated(request,users)})

@roles('director')
def account_create(request, role=None):
    selected_role = role or (request.POST.get('role') if request.method == 'POST' else request.GET.get('role', 'faculty'))
    if selected_role not in Profile.Role.values:
        raise Http404('Choose a valid account role.')
    form = AccountForm(request.POST if request.method == 'POST' else None, role=selected_role)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Account created. Share the initial password privately; the user can change it after login.')
        return redirect('accounts')
    return render(request, 'account_form.html', {'form':form, 'account_role':selected_role,
        'role_choices':Profile.Role.choices, 'title':f'Create {Profile.Role(selected_role).label.lower()} account'})

@roles('director')
@require_POST
def account_toggle(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if user.pk == request.user.pk or user.is_superuser or user.profile.role == 'director':
        messages.error(request, 'Director and administrator accounts cannot be deactivated here.')
    else:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, 'Account access updated.')
    return redirect('accounts')

@roles('director')
def reports(request):
    return render(request,'reports.html')

def csv_value(value):
    text = str(value if value is not None else '')
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) or text.startswith(('\t','\r','\n')) else text

@roles('director')
def report_export(request,kind):
    if kind=='feedback':
        header=['Faculty','Average rating','Responses'];qs=Faculty.objects.annotate(average_rating=Avg('ratings__rating'),responses=Count('ratings')).order_by('fname','id')
        rows=[(f.fname,round(f.average_rating,2) if f.average_rating else '',f.responses) for f in qs]
    elif kind=='quizzes':
        header=['Quiz','Code','Faculty','Submissions','Active students','Participation %']
        students=Profile.objects.filter(role='student',user__is_active=True).count()
        rows=[(q.title,q.code,display_name(q.creator) if q.creator else str(q.faculty or 'Unassigned'),q.attempts,students,round(q.attempts*100/students,2) if students else 0) for q in Quiz.objects.select_related('creator','faculty').annotate(attempts=Count('submissions')).order_by('title','id')]
    elif kind=='complaints':
        header=['Title','Student','Faculty','Status','Created at']
        rows=[(c.title,c.student.name,c.teacher.name,c.get_status_display(),c.created_at.isoformat()) for c in Complaint.objects.select_related('student','teacher').order_by('title','id')]
    elif kind=='resources':
        header=['Title','Subject','Category','Downloads','Uploader']
        rows=[(r.title,r.subject,r.get_category_display(),r.download_count,display_name(r.uploaded_by)) for r in Resource.objects.select_related('uploaded_by').order_by('title','id')]
    else:raise Http404
    response=HttpResponse(content_type='text/csv; charset=utf-8');response['Content-Disposition']=f'attachment; filename="teachtrack-{kind}.csv"';response['Cache-Control']='private, no-store';response.write('\ufeff')
    writer=csv.writer(response);writer.writerow(header);writer.writerows([[csv_value(v) for v in row] for row in rows]);return response

def health(request):
    return HttpResponse('ok',content_type='text/plain')

def valid_quiz(quiz):
    questions=list(quiz.questions.prefetch_related('options').all())
    return bool(questions) and all(len(q.options.all())>=2 and sum(o.is_correct for o in q.options.all())>=1 and (q.is_multiple or sum(o.is_correct for o in q.options.all())==1) for q in questions)

def index(request):
    return render(request,'index.html',{'public_page':'home'})

def campus_life(request):
    return render(request,'campus_life.html',{'public_page':'campus'})

def contact(request):
    form=ContactForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save();messages.success(request,'Your message has been received.');return redirect('index')
    return render(request, 'contact.html', {'form': form, 'public_page': 'contact'})

@login_required
def question_image(request,pk):
    question=get_object_or_404(Question.objects.select_related('quiz'),pk=pk)
    quiz=question.quiz;role=request.user.profile.role
    if role=='faculty' and quiz.creator_id!=request.user.pk:raise PermissionDenied
    if role=='student' and not Submission.objects.filter(quiz=quiz,student=request.user).exists() and not (quiz.is_active and quiz.starts_at<=timezone.now()<quiz.expiry_time):raise PermissionDenied
    if not question.image:raise Http404
    try:file=question.image.open('rb')
    except FileNotFoundError:raise Http404
    import mimetypes
    content_type=mimetypes.guess_type(question.image.name)[0]
    if content_type not in ['image/png','image/jpeg','image/gif','image/webp']:raise Http404
    return FileResponse(file,content_type=content_type)

@login_required
@require_POST
def attachment_download(request,kind,pk):
    role=request.user.profile.role
    if kind=='doubt':
        qs=Doubt.objects.all()
        if role=='student':qs=qs.filter(student=request.user)
        elif role=='faculty':qs=qs.filter(faculty__user=request.user)
        item=get_object_or_404(qs,pk=pk);field=item.attachment
    elif kind=='announcement':
        item=get_object_or_404(Announcement.objects.filter(Q(audience='all')|Q(audience=role)|Q(author=request.user)),pk=pk);field=item.document
    else:raise Http404
    if not field:raise Http404
    try:file=field.open('rb')
    except FileNotFoundError:raise Http404
    return FileResponse(file,as_attachment=True,filename=Path(field.name).name,content_type='application/octet-stream')

@login_required
def submission_detail_list(request):
    qs=Submission.objects.select_related('student','quiz')
    role=request.user.profile.role
    if role=='student':qs=qs.filter(student=request.user)
    elif role=='faculty':qs=qs.filter(quiz__creator=request.user)
    return render(request,'submission_history.html',{'page_obj':paginated(request,qs.order_by('-submitted_at','-id'))})

@login_required
def legacy_score(request,submission_id):
    item=get_object_or_404(Submission,pk=submission_id)
    role=request.user.profile.role
    if role=='student' and item.student_id!=request.user.pk:raise PermissionDenied
    if role=='faculty' and item.quiz.creator_id!=request.user.pk:raise PermissionDenied
    return render(request,'quiz_result.html',{'quiz':item.quiz,'submissions':[item],'show_answers':role!='student' or timezone.now()>=item.quiz.expiry_time})

@roles('student')
def student_dashboard(request):return dashboard(request)
@roles('faculty')
def faculty_dashboard(request):return dashboard(request)
@roles('director')
def Director_dashboard(request):return dashboard(request)
