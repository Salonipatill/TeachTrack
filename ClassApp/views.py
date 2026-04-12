from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
from .models import Student, Faculty, Director, Contact, Doubt, ImageUploader, Announcement,Rating
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import PasswordResetOTP
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
import random
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
import json
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
import pytz
from .models import Quiz, Question, Option, Submission, SubmissionAnswer, Faculty, Student, Director, SubmissionDetail
from .forms import QuizCreateForm, QuestionForm, StudentInfoForm
from django.db import transaction

# Create your views here.

# Main Page
def index(request):
    return render(request, 'index.html')

# Student Registration
def student_registration(request):
    if request.method == "POST":
        sname = request.POST['sname']
        sen = request.POST['sen']
        sphone = request.POST['sphone']
        semail = request.POST['semail']
        unm = request.POST['unm']
        pw = request.POST['pw']
        course = request.POST['course']
        year = request.POST['year']
        sem = request.POST['sem']
        section = request.POST['section']

        student = Student(
            sname=sname, sen=sen, sphone=sphone, semail=semail,
            unm=unm, pw=pw, course=course, year=year, sem=sem, section=section
        )
        student.save()
        messages.success(request, "Student registered successfully!")
        return redirect('student_login')

    return render(request, 'student_registration.html')

# Faculty Registration
def faculty_registration(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        fphone = request.POST.get("fphone")
        femail = request.POST.get("femail")
        unm = request.POST.get("unm")
        pw = request.POST.get("pw")

        Faculty.objects.create(
            fname=fname, fphone=fphone, femail=femail,
            unm=unm, pw=pw
        )
        messages.success(request, "Faculty registered successfully!")
        return redirect('faculty_login')

    return render(request, 'faculty_registration.html')

# Director Registration
def director_registration(request):
    if request.method == "POST":
        dname = request.POST.get("dname")
        dphone = request.POST.get("dphone")
        demail = request.POST.get("demail")
        unm = request.POST.get("unm")
        pw = request.POST.get("pw")

        Director.objects.create(
            dname=dname, dphone=dphone, demail=demail,
            unm=unm, pw=pw
        )
        messages.success(request, "Director registered successfully!")
        return redirect('director_login')

    return render(request, 'director_registration.html')

def student_login(request):
    if request.method == "POST":
        # Get email & password from all possible field names
        email = request.POST.get("semail")
        password = request.POST.get("pw")

        if not email or not password:
            messages.error(request, "Please enter email and password")
            return redirect("student_login")

        user = None
        user_type = None

        # Check Student
        try:
            student = Student.objects.get(semail=email, pw=password)
            user = student
            user_type = "student"
        except Student.DoesNotExist:
            pass

        if user:
            # Set session
            if user:
                request.session['user_id'] = user.id
                request.session['user_type'] = user_type
                request.session['student_name'] = user.sname   # SAVE NAME HERE
                return redirect('student_dashboard')

        # Failed login
        messages.error(request, "Incorrect email or password")
        return redirect("student_login")
    return render(request, "student_login.html")

def faculty_login(request):
    if request.method == "POST":
        # Accept email & password from any field name you use
        email = (
            request.POST.get("femail")
        )
        password = request.POST.get("pw")

        if not email or not password:
            messages.error(request, "Please enter email and password")
            return redirect("faculty_login")

        user = None

        # Check Faculty
        try:
            faculty = Faculty.objects.get(femail=email, pw=password)
            user = faculty
        except Faculty.DoesNotExist:
            pass

        if user:
            request.session["user_id"] = user.id
            request.session["user_type"] = "faculty"
            request.session["faculty_name"] = faculty.fname    
            return redirect("faculty_dashboard")

        messages.error(request, "Incorrect email or password")
        return redirect("faculty_login")

    return render(request, "faculty_login.html")

def director_login(request):
    if request.method == "POST":
        # Accept email & password from any field name used in form
        email = (
            request.POST.get("email")
            or request.POST.get("demail")
            or request.POST.get("username")
        )
        password = request.POST.get("password") or request.POST.get("pw")

        if not email or not password:
            messages.error(request, "Please enter email and password")
            return redirect("director_login")

        user = None

        # Check Director
        try:
            director = Director.objects.get(demail=email, pw=password)
            user = director
        except Director.DoesNotExist:
            pass

        if user:
            request.session["user_id"] = user.id
            request.session["user_type"] = "director"
            request.session["director_name"] = director.dname
            return redirect("Director_dashboard")

        messages.error(request, "Incorrect email or password")
        return redirect("director_login")

    return render(request, "director_login.html")
    
def student_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("semail")
        # You can add email checking or mail sending logic here
        return render(request, "student_forgot_password.html", {"msg": "Reset link sent if email exists"})
    return render(request, "student_forgot_password.html")

def faculty_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("femail")
        # You can add email checking or mail sending logic here
        return render(request, "faculty_forgot_password.html", {"msg": "Reset link sent if email exists"})
    return render(request, "faculty_forgot_password.html")

def director_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("demail")
        # You can add email checking or mail sending logic here
        return render(request, "director_forgot_password.html", {"msg": "Reset link sent if email exists"})
    return render(request, "director_forgot_password.html")

# Conatact
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        title = request.POST.get("title")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            title=title,
            message=message
        )
        messages.success(request, "Message sent successfully")
        return redirect("/")  # redirect wherever you want
    return render(request, "index.html")

def student_dashboard(request):
    quiz = Quiz.objects.filter(is_active=True).last()  # latest active quiz
    name = request.session.get("student_name", "Student")
    announcements = Announcement.objects.all().order_by('-created_at')  # fetch all announcements
    return render(request, 'student_dashboard.html', {
    'quiz': quiz,
    'name': name,
    'announcements': announcements,
})
     
def Director_dashboard(request):
    name = request.session.get("director_name", "Director")
    return render(request, 'Director_dashboard.html', { 'name': name, })

def faculty_dashboard(request):
    name = request.session.get('faculty_name', 'Faculty')
    return render(request, 'faculty_dashboard.html', {'name': name})

def deactivate_expired_quizzes():
    now_utc = timezone.now()
    expired = Quiz.objects.filter(is_active=True, expiry_time__lte=now_utc)
    if expired.exists():
        expired.update(is_active=False)

# @transaction.atomic
# def create_quiz(request):
#     faculty_obj, created = Faculty.objects.get_or_create(unm=request.user)

#     deactivate_expired_quizzes()

#     if request.method == "POST":
#         form = QuizCreateForm(request.POST)
#         if form.is_valid():
#             quiz = form.save(commit=False)
#             quiz.save()

#             q_json = request.POST.get('questions_data')
#             if q_json:
#                 try:
#                     questions_data = json.loads(q_json)
#                 except json.JSONDecodeError:
#                     transaction.set_rollback(True)
#                     return HttpResponseBadRequest("Invalid questions JSON.")

#                 for idx, qd in enumerate(questions_data):
#                     q = Question.objects.create(
#                         quiz=quiz,
#                         text=qd.get('text', ''),
#                         is_multiple=qd.get('is_multiple', False)
#                     )

#                     img_field_name = qd.get('image_field_name')
#                     if img_field_name and img_field_name in request.FILES:
#                         q.image = request.FILES[img_field_name]
#                         q.save()

#                     for opt in qd.get('options', []):
#                         Option.objects.create(
#                             question=q,
#                             text=opt.get('text', ''),
#                             is_correct=bool(opt.get('is_correct', False))
#                         )

#                 messages.success(request, "Quiz created successfully.")
#                 return redirect(reverse('teacher_quiz_list'))

#             else:
#                 # Fallback legacy parser
#                 questions = request.POST.getlist('question[]')
#                 optionA = request.POST.getlist('optionA[]')
#                 optionB = request.POST.getlist('optionB[]')
#                 optionC = request.POST.getlist('optionC[]')
#                 optionD = request.POST.getlist('optionD[]')
#                 correct = request.POST.getlist('correct[]')

#                 for i, q_text in enumerate(questions):
#                     q = Question.objects.create(
#                         quiz=quiz,
#                         text=q_text,
#                         is_multiple=False
#                     )

#                     if i < len(optionA) and optionA[i].strip():
#                         Option.objects.create(
#                             question=q,
#                             text=optionA[i].strip(),
#                             is_correct=(correct[i].upper() == 'A' if i < len(correct) else False)
#                         )
#                     if i < len(optionB) and optionB[i].strip():
#                         Option.objects.create(
#                             question=q,
#                             text=optionB[i].strip(),
#                             is_correct=(correct[i].upper() == 'B' if i < len(correct) else False)
#                         )
#                     if i < len(optionC) and optionC[i].strip():
#                         Option.objects.create(
#                             question=q,
#                             text=optionC[i].strip(),
#                             is_correct=(correct[i].upper() == 'C' if i < len(correct) else False)
#                         )
#                     if i < len(optionD) and optionD[i].strip():
#                         Option.objects.create(
#                             question=q,
#                             text=optionD[i].strip(),
#                             is_correct=(correct[i].upper() == 'D' if i < len(correct) else False)
#                         )

#                 messages.success(request, "Quiz created (legacy parser).")
#                 return redirect(reverse('teacher_quiz_list'))

#         else:
#             messages.error(request, "Please fix errors in the form.")

#     else:
#         form = QuizCreateForm()

#     return render(request, 'quiz/create_quiz.html', {'form': form})

def create_quiz(request):
    faculty_id = request.session.get('user_id')  # or request.user.id if using Django auth
    faculty = Faculty.objects.get(id=faculty_id)

    if request.method == "POST":
        title = request.POST.get("title")
        require_name = bool(request.POST.get("require_name"))
        require_roll = bool(request.POST.get("require_roll"))
        require_email = bool(request.POST.get("require_email"))
        require_class = bool(request.POST.get("require_class"))

        quiz = Quiz.objects.create(
            title=title,
            faculty=faculty,
            require_name=require_name,
            require_roll=require_roll,
            require_email=require_email,
            require_class=require_class
        )

        questions_data = json.loads(request.POST.get("questions_data", "[]"))
        for q in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=q.get("text"),
                is_multiple=q.get("is_multiple", False)
            )

            image_field_name = q.get("image_field_name")
            if image_field_name and image_field_name in request.FILES:
                question.image = request.FILES[image_field_name]
                question.save()

            for opt in q.get("options", []):
                Option.objects.create(
                    question=question,
                    text=opt.get("text"),
                    is_correct=opt.get("is_correct", False)
                )

        return redirect("faculty_dashboard")  # adjust as needed

    return render(request, "quiz/create_quiz.html")

# def teacher_quiz_list(request):
#     # Deactivate any expired quizzes
#     deactivate_expired_quizzes()

#     # Fetch all quizzes ordered by most recent
#     quizzes = Quiz.objects.all().order_by('-created_at')

#     # Render the teacher quiz list template
#     return render(request, 'quiz/teacher_list.html', {'quizzes': quizzes})

def teacher_quiz_list(request):
    faculty_id = request.session.get('user_id')
    if not faculty_id:
        messages.error(request, "Please log in first.")
        return redirect('faculty_login')

    # Only fetch quizzes created by this faculty
    quizzes = Quiz.objects.filter(faculty_id=faculty_id).order_by('-created_at')

    return render(request, 'quiz/teacher_list.html', {'quizzes': quizzes})

def student_quiz_list(request):
    deactivate_expired_quizzes()
    now = timezone.now()
    quizzes = Quiz.objects.filter(is_active=True, expiry_time__gt=now).order_by('-created_at')
    return render(request, 'quiz/student_list.html', {'quizzes': quizzes})

def attempt_quiz(request, quiz_id):
    deactivate_expired_quizzes()
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # block if inactive or expired
    if not quiz.is_active or timezone.now() >= quiz.expiry_time:
        messages.error(request, "Quiz Expired.")
        return render(request, 'quiz/expired.html', {'quiz': quiz})

    # build question/option context
    questions = quiz.questions.prefetch_related('options').all()

    # Dynamically build student info form and require selected fields
    if request.method == "POST":
        # Validate expiry again at submission time
        if timezone.now() >= quiz.expiry_time:
            messages.error(request, "Quiz Expired at submission.")
            return render(request, 'quiz/expired.html', {'quiz': quiz})

        # Validate student details according to quiz flags
        student_form = StudentInfoForm(request.POST)
        # enforce required flags
        if quiz.require_name:
            student_form.fields['student_name'].required = True
        if quiz.require_roll:
            student_form.fields['roll_no'].required = True
        if quiz.require_email:
            student_form.fields['email'].required = True
        if quiz.require_class:
            student_form.fields['class_div'].required = True

        if not student_form.is_valid():
            messages.error(request, "Please fill required student details.")
            return render(request, 'quiz/attempt.html', {'quiz': quiz, 'questions': questions, 'student_form': student_form})
        
        submission = student_form.save(commit=False)
        submission.quiz = quiz
        submission.save()

        total_score = 0
        for q in questions:
            # For each question, get selected option ids from POST.
            # Frontend should name inputs like "q_<id>" (single) or "q_<id>_multi" (multiple)
            if q.is_multiple:
                key = f"q_{q.id}"
                selected_ids = request.POST.getlist(key)  # list of option ids as strings
            else:
                key = f"q_{q.id}"
                sel = request.POST.get(key)
                selected_ids = [sel] if sel else []

            # create SubmissionAnswer
            if selected_ids:
                sa = SubmissionAnswer.objects.create(submission=submission, question=q)
                # convert to ints and add ManyToMany
                opts = Option.objects.filter(question=q, id__in=[int(x) for x in selected_ids if x])
                sa.selected_options.set(opts)
                sa.save()

            # Evaluate correctness
            correct_opts = q.options.filter(is_correct=True)
            selected_opts = Option.objects.filter(question=q, id__in=[int(x) for x in selected_ids if x])
            # For scoring: require exact match of correct option set
            correct_set = set(correct_opts.values_list('id', flat=True))
            selected_set = set(selected_opts.values_list('id', flat=True))
            if correct_set and selected_set == correct_set:
                total_score += 1

        submission.score = total_score
        submission.save()

        messages.success(request, f"Submitted successfully. Score: {total_score}/{questions.count()}")
        return redirect(reverse('student_quiz_list'))

    else:
        # GET - show quiz; student form fields are empty but required rules applied in template or on POST
        student_form = StudentInfoForm()
        # make fields required in template by passing flags
        required_flags = {
            'require_name': quiz.require_name,
            'require_roll': quiz.require_roll,
            'require_email': quiz.require_email,
            'require_class': quiz.require_class
        }
        return render(request, 'quiz/attempt.html', {
            'quiz': quiz,
            'questions': questions,
            'student_form': student_form,
            'required_flags': required_flags
        })

def quiz_submissions(request, quiz_id):
    # Fetch the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Fetch all submissions for this quiz, newest first
    submissions = Submission.objects.filter(quiz=quiz).order_by('-submitted_at').prefetch_related('answers__selected_options')

    # Render submissions template
    return render(request, 'quiz/submissions.html', {'quiz': quiz, 'submissions': submissions})

# def view_score(request, submission_id):
#     submission = get_object_or_404(Submission, id=submission_id)
#     quiz = submission.quiz

#     answers = []

#     for ans in submission.answers.all():
#         selected = ans.selected_options.all()
#         correct_options = ans.question.options.filter(is_correct=True)

#         # Compare selected vs correct option IDs
#         is_correct = set(o.id for o in selected) == set(o.id for o in correct_options)

#         answers.append({
#             "question": ans.question,
#             "your_answer": selected,
#             "correct_answer": correct_options,
#             "is_correct": is_correct
#         })

#     context = {
#         "quiz": quiz,
#         "submission": submission,
#         "answers": answers
#     }
#     return render(request, "quiz/view_score.html", context)

def view_score(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    quiz = submission.quiz
    answers = []
    for ans in submission.answers.all():
        selected = ans.selected_options.all()
        correct_options = ans.question.options.filter(is_correct=True)
        is_correct = set(o.id for o in selected) == set(o.id for o in correct_options)

        answers.append({
            "question": ans.question,
            "your_answer": selected,
            "correct_answer": correct_options,
            "is_correct": is_correct
        })

    context = {
        "quiz": quiz,
        "submission": submission,
        "answers": answers
    }
    return render(request, 'quiz/submitted.html', context)

def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == "POST":
        submission = Submission.objects.create(
            quiz=quiz,
            student_name=request.POST.get("student_name"),
            roll_no=request.POST.get("roll_no"),
            email=request.POST.get("email"),
            class_div=request.POST.get("class_div"),
        )
        score = 0

        for question in quiz.questions.all():
            selected_ids = request.POST.getlist(f'question_{question.id}')
            if selected_ids:
                # Save SubmissionAnswer (optional, if you want both)
                ans = SubmissionAnswer.objects.create(submission=submission, question=question)
                ans.selected_options.set([int(x) for x in selected_ids])

                # Calculate correctness
                correct_ids = list(question.options.filter(is_correct=True).values_list('id', flat=True))
                if set(map(int, selected_ids)) == set(correct_ids):
                    score += 1
                 
                submission.score = score
                submission.save()
                 
                detail = SubmissionDetail.objects.create(
                    student_name=submission.student_name,
                    roll_no=submission.roll_no,
                    email=submission.email,
                    class_div=submission.class_div,
                    score=score,   # overall score (or use 1/0 for per-question)
                    question=question,
                    quiz=quiz,
                    submission=submission
                )
                detail.selected_options.set([int(x) for x in selected_ids])  # ✅ options saved here
               
        messages.success(request, "Quiz submitted successfully!")
        return redirect('view_score', submission_id=submission.id)

    return render(request, 'quiz/attempt_quiz.html', {'quiz': quiz})

def doubt(request):
    faculties = Faculty.objects.all()  # Fetch all registered faculties

    if request.method == 'POST':
        # Use the same names as in your form
        student_name = request.POST.get('name')        # form input name="name"
        student_email = request.POST.get('email')      # form input name="email"
        doubt_text = request.POST.get('doubt')         # form textarea name="doubt"
        faculty_id = request.POST.get('faculty')       # form select name="faculty"
        attachment = request.FILES.get('attachment')   # form file input

        if not faculty_id:
            messages.error(request, "Please select a faculty.")
            return redirect('doubt')

        selected_faculty = Faculty.objects.get(id=faculty_id)

        # Save the doubt using the correct field names
        Doubt.objects.create(
            student_name=student_name,
            student_email=student_email,
            doubt=doubt_text,
            faculty=selected_faculty,
            attachment=attachment
        )

        messages.success(request, "Your doubt has been submitted successfully!")
        return redirect('doubt')

    return render(request, 'doubt.html', {'faculties': faculties})

def doubt_viewer(request):
    faculty_id = request.session.get('user_id')
    if not faculty_id:
        messages.error(request, "Please log in first.")
        return redirect('faculty_login')

    # Fetch doubts for this faculty
    doubts = Doubt.objects.filter(faculty_id=faculty_id).order_by('-submitted_at')

    # Convert each timestamp to local time
    for doubt in doubts:
        doubt.submitted_at = timezone.localtime(doubt.submitted_at)

    return render(request, 'doubt_viewer.html', {'doubts': doubts})


def rating(request):
    faculties = Faculty.objects.all()

    if request.method == 'POST' :

        student_name = request.POST.get('name')
        student_email = request.POST.get('email')
        rating = request.POST.get('rating')
        faculty_id = request.POST.get('faculty')


        if not faculty_id:
            messages.error(request, "Please select a faculty.")
            return redirect('rating')
        
        selected_faculty = Faculty.objects.get(id=faculty_id)

        Rating.objects.create(
            student_name = student_name,
            student_email = student_email,
            rating = rating,
            faculty = selected_faculty,
        )


        messages.success(request, "Your Feedback has been submitted successfully!")
        return redirect('rating')
    
    return render(request, 'Rating.html', {'faculties' : faculties})




def submission_detail_list(request):
    details = SubmissionDetail.objects.all()
    for d in details:
     print(d.student_name, d.quiz.title, d.question.text, d.score)

    return render(request, "submission_detail_list.html", {"details": details})

from .models import Announcement, Faculty
from .forms import AnnouncementForm
from django.contrib import messages

def announcement(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    user_type = request.session.get("user_type")
    return render(request, 'announcement.html', {
        'announcements': announcements,
        'user_type': user_type
    })

def add_announcement(request):
    if request.session.get("user_type") != "faculty":
        return HttpResponseForbidden("You are not allowed")

    faculty_id = request.session.get("user_id")
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = faculty
            announcement.save()
            messages.success(request, "Announcement posted successfully!")
            return redirect('announcement')
    else:
        form = AnnouncementForm()

    return render(request, 'add_announcement.html', {'form': form})