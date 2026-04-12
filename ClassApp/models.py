from django.db import models
from django.utils.timezone import now
import json
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
import pytz

# Create your models here.

# Student Model
class Student(models.Model):
    sname = models.CharField(max_length=100)
    sen = models.CharField(max_length=50)
    sphone = models.CharField(max_length=10)
    semail = models.EmailField()
    unm = models.CharField(max_length=50)
    pw = models.CharField(max_length=50)
    course = models.CharField(max_length=50, default='')
    year = models.CharField(max_length=20, default='')
    sem = models.CharField(max_length=20, default='')
    section = models.CharField(max_length=5, default='')

    def __str__(self):
        return self.sname

# Faculty Model
class Faculty(models.Model):
    fname = models.CharField(max_length=100)
    fphone = models.CharField(max_length=15)
    femail = models.EmailField(unique=True, blank=True, null=True)
    unm = models.CharField(max_length=50, unique=True)
    pw = models.CharField(max_length=128)

    def __str__(self):
        return self.fname

# Director Model
class Director(models.Model):
    dname = models.CharField(max_length=100)
    dphone = models.CharField(max_length=15)
    demail = models.EmailField(unique=True)
    unm = models.CharField(max_length=50, unique=True)
    pw = models.CharField(max_length=128)

    def __str__(self):
        return self.dname
    
from django.db import models

# Contact
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ImageUploader(models.Model):
    photo=models.ImageField(upload_to="ALLImages")
    date=models.DateTimeField(default=now)

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
# QUIZ MODEL
# class Quiz(models.Model):
#     title = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expiry_time = models.DateTimeField()  # auto set to 12 AM
#     is_active = models.BooleanField(default=True)

#     # Student detail requirements
#     require_name = models.BooleanField(default=False)
#     require_roll = models.BooleanField(default=False)
#     require_email = models.BooleanField(default=False)
#     require_class = models.BooleanField(default=False)

#     def save(self, *args, **kwargs):
#         # Set expiry to today's midnight India time
#         if not self.expiry_time:
#             india = timezone.pytz.timezone("Asia/Kolkata")
#             now = timezone.now().astimezone(india)
#             midnight = now.replace(hour=23, minute=59, second=59)
#             self.expiry_time = midnight.astimezone(timezone.utc)

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title

# Quiz Model
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()  # auto set to 12 AM
    is_active = models.BooleanField(default=True)

    # Student detail requirements
    require_name = models.BooleanField(default=False)
    require_roll = models.BooleanField(default=False)
    require_email = models.BooleanField(default=False)
    require_class = models.BooleanField(default=False)

    # **Add faculty reference**
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="quizzes", null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.expiry_time:
            india = pytz.timezone("Asia/Kolkata")  # use pytz directly
            now = timezone.now().astimezone(india)
            midnight = now.replace(hour=23, minute=59, second=59)
            self.expiry_time = midnight.astimezone(pytz.UTC)
    
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# QUESTION MODEL
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    image = models.ImageField(upload_to="quiz_images/", null=True, blank=True)

    is_multiple = models.BooleanField(default=False)  # True = multi-select

    def __str__(self):
        return f"{self.quiz.title} — {self.text[:40]}"

# OPTION MODEL
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} {'(Correct)' if self.is_correct else ''}"
    
# STUDENT SUBMISSION
class Submission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Student details
    student_name = models.CharField(max_length=255, null=True, blank=True)
    roll_no = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    class_div = models.CharField(max_length=50, null=True, blank=True)
   
    # Score
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Submission for {self.quiz.title}"

# SUBMISSION ANSWERS
class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option)

    def __str__(self):
        return f"Answer to: {self.question.text[:40]}"

# Doubt model
class Doubt(models.Model):
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    doubt = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='doubts')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} -> {self.faculty.fname}"  # use fname instead of name
    
class SubmissionDetail(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option)

    # Student details (duplicate from Submission)
    student_name = models.CharField(max_length=255, null=True, blank=True)
    roll_no = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    class_div = models.CharField(max_length=50, null=True, blank=True)

    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student_name} — {self.quiz.title} — {self.question.text[:30]}"
    
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    document = models.FileField(
        upload_to='announcements/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Rating(models.Model):
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    rating = models.PositiveSmallIntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='ratings')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} -> {self.faculty.fname}"
    