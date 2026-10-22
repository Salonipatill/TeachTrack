"""Original TeachTrack models, extended with secure accounts and academic modules."""
import secrets
import uuid
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

def quiz_code():
    return secrets.token_hex(3).upper()
def resource_path(instance, filename):
    return f'resources/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'

class Student(models.Model):
    sname=models.CharField(max_length=100)
    sen=models.CharField(max_length=50)
    sphone=models.CharField(max_length=10)
    semail=models.EmailField()
    unm=models.CharField(max_length=50)
    course=models.CharField(max_length=50,default='')
    year=models.CharField(max_length=20,default='')
    sem=models.CharField(max_length=20,default='')
    section=models.CharField(max_length=5,default='')
    batch=models.CharField(max_length=30,blank=True,default='')
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='legacy_student')
    def __str__(self): return self.sname
class Faculty(models.Model):
    fname=models.CharField(max_length=100)
    fphone=models.CharField(max_length=15)
    femail=models.EmailField(unique=True,blank=True,null=True)
    unm=models.CharField(max_length=50,unique=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='legacy_faculty')
    def __str__(self): return self.fname
class Director(models.Model):
    dname=models.CharField(max_length=100)
    dphone=models.CharField(max_length=15)
    demail=models.EmailField(unique=True)
    unm=models.CharField(max_length=50,unique=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='legacy_director')
    def __str__(self): return self.dname
class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT='student','Student'
        FACULTY='faculty','Faculty'
        DIRECTOR='director','Director'
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile')
    role=models.CharField(max_length=10,choices=Role.choices,default=Role.STUDENT,db_index=True)
    enrollment=models.CharField(max_length=90,blank=True)
    department=models.CharField(max_length=100,blank=True)
    def __str__(self): return f'{self.user.username} ({self.role})'
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    title=models.CharField(max_length=200)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
class ImageUploader(models.Model):
    photo=models.ImageField(upload_to='ALLImages')
    date=models.DateTimeField(default=now)
class PasswordResetOTP(models.Model):
    # Retained for migration history only. Authentication uses Django reset tokens.
    email=models.EmailField()
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.email
class Quiz(models.Model):
    title=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    expiry_time=models.DateTimeField()
    is_active=models.BooleanField(default=True)
    require_name=models.BooleanField(default=False)
    require_roll=models.BooleanField(default=False)
    require_email=models.BooleanField(default=False)
    require_class=models.BooleanField(default=False)
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE,related_name='quizzes',null=True,blank=True)
    code=models.CharField(max_length=6,null=True,blank=True,unique=True,editable=False)
    subject=models.CharField(max_length=100,blank=True)
    starts_at=models.DateTimeField(default=now)
    creator=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='created_quizzes')
    class Meta: ordering=['-created_at','-id']
    def save(self,*args,**kwargs):
        if not self.expiry_time:
            local=timezone.localtime()
            self.expiry_time=(local+timezone.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        if not self.code: self.code=quiz_code()
        super().save(*args,**kwargs)
    def __str__(self): return self.title
    @property
    def published(self): return self.is_active
    @property
    def ends_at(self): return self.expiry_time
class Question(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='questions')
    text=models.TextField()
    image=models.ImageField(upload_to='quiz_images/',null=True,blank=True)
    is_multiple=models.BooleanField(default=False)
    class Meta: ordering=['id']
    def __str__(self): return f'{self.quiz.title}: {self.text[:40]}'
class Option(models.Model):
    question=models.ForeignKey(Question,on_delete=models.CASCADE,related_name='options')
    text=models.CharField(max_length=255)
    is_correct=models.BooleanField(default=False)
    class Meta: ordering=['id']
    def __str__(self): return self.text
class Submission(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='submissions')
    submitted_at=models.DateTimeField(auto_now_add=True)
    student_name=models.CharField(max_length=255,null=True,blank=True)
    roll_no=models.CharField(max_length=50,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    class_div=models.CharField(max_length=50,null=True,blank=True)
    score=models.IntegerField(default=0)
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='quiz_submissions')
    total=models.PositiveIntegerField(default=0)
    review=models.JSONField(default=list)
    academic_details=models.JSONField(default=dict,blank=True)
    class Meta:
        ordering=['-score','submitted_at','id']
        constraints=[models.UniqueConstraint(fields=['quiz','student'],name='one_authenticated_quiz_attempt')]
    @property
    def percentage(self):return round(self.score*100/self.total) if self.total else 0
    def __str__(self):return f'Submission for {self.quiz.title}'
class SubmissionAnswer(models.Model):
    submission=models.ForeignKey(Submission,on_delete=models.CASCADE,related_name='answers')
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_options=models.ManyToManyField(Option)
    def __str__(self): return f'Answer to: {self.question.text[:40]}'
class SubmissionDetail(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    submission=models.ForeignKey(Submission,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_options=models.ManyToManyField(Option)
    student_name=models.CharField(max_length=255,null=True,blank=True)
    roll_no=models.CharField(max_length=50,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    class_div=models.CharField(max_length=50,null=True,blank=True)
    score=models.IntegerField(default=0)
    def __str__(self): return f'{self.student_name}: {self.quiz.title}'
class Doubt(models.Model):
    student_name=models.CharField(max_length=100)
    student_email=models.EmailField()
    doubt=models.TextField()
    attachment=models.FileField(upload_to='attachments/',null=True,blank=True)
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE,related_name='doubts')
    submitted_at=models.DateTimeField(auto_now_add=True)
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='doubts')
    subject=models.CharField(max_length=100,blank=True)
    answer=models.TextField(blank=True)
    answered_at=models.DateTimeField(null=True,blank=True)
    class Meta: ordering=['-submitted_at','-id']
    def __str__(self): return f'{self.student_name} -> {self.faculty.fname}'
class Announcement(models.Model):
    AUDIENCES=[('all','Everyone'),('student','Students'),('faculty','Faculty'),('director','Directors')]
    title=models.CharField(max_length=200)
    content=models.TextField()
    posted_by=models.ForeignKey(Faculty,on_delete=models.SET_NULL,null=True,blank=True)
    document=models.FileField(upload_to='announcements/',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    audience=models.CharField(max_length=10,choices=AUDIENCES,default='all')
    class Meta: ordering=['-created_at','-id']
    def __str__(self): return self.title
class Rating(models.Model):
    student_name=models.CharField(max_length=100)
    student_email=models.EmailField()
    rating=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE,related_name='ratings')
    submitted_at=models.DateTimeField(auto_now_add=True)
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='given_feedback')
    comment=models.TextField(blank=True)
    updated_at=models.DateTimeField(default=now)
    class Meta:
        ordering=['-updated_at','-id']
        constraints=[models.UniqueConstraint(fields=['student','faculty'],name='one_authenticated_faculty_rating'),models.CheckConstraint(condition=Q(rating__gte=1,rating__lte=5),name='rating_between_1_and_5')]
    def __str__(self): return f'{self.student_name} -> {self.faculty.fname}'
class AuthenticatedStudent(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='student')
    name=models.CharField(max_length=100)
    def __str__(self): return self.name
class Teacher(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacher')
    name=models.CharField(max_length=100)
    def __str__(self): return self.name
class Complaint(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('in_progress','In progress'),('resolved','Resolved')]
    STATUSES=STATUS_CHOICES
    student=models.ForeignKey(AuthenticatedStudent,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    text=models.TextField()
    teacher_reply=models.TextField(blank=True,null=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending',db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    reply_time=models.DateTimeField(blank=True,null=True)
    title=models.CharField(max_length=180,default='Student concern')
    updated_at=models.DateTimeField(default=now)
    class Meta: ordering=['-updated_at','-id']
    def __str__(self): return f'{self.student.name} -> {self.teacher.name}'
class ComplaintEvent(models.Model):
    complaint=models.ForeignKey(Complaint,on_delete=models.CASCADE,related_name='events')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    message=models.TextField()
    status=models.CharField(max_length=20,choices=Complaint.STATUSES)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['created_at','id']
class Resource(models.Model):
    CATEGORIES=[('notes','Notes'),('pyq','PYQs'),('assignment','Assignments')]
    title=models.CharField(max_length=180)
    description=models.TextField(blank=True)
    subject=models.CharField(max_length=100,db_index=True)
    category=models.CharField(max_length=100,db_index=True)
    file=models.FileField(upload_to=resource_path,max_length=255)
    original_name=models.CharField(max_length=255)
    uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    download_count=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['-created_at','-id']
    def __str__(self):return self.title
    def get_category_display(self):
        return dict(self.CATEGORIES).get(self.category,self.category)
    @classmethod
    def category_choices(cls):
        custom=cls.objects.exclude(category__in=dict(cls.CATEGORIES)).exclude(category='').order_by('category').values_list('category',flat=True).distinct()
        return cls.CATEGORIES+[(value,value) for value in custom]
class Download(models.Model):
    resource=models.ForeignKey(Resource,on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
class ResourceFile(models.Model):
    resource=models.OneToOneField(Resource,on_delete=models.CASCADE,related_name='stored_file')
    storage_name=models.CharField(max_length=255)
    content=models.BinaryField()
    created_at=models.DateTimeField(auto_now_add=True)
class Notification(models.Model):
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications')
    title=models.CharField(max_length=180)
    message=models.TextField(blank=True)
    link=models.CharField(max_length=255,blank=True)
    read_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at','-id']
        indexes=[models.Index(fields=['recipient','read_at'])]
class LoginThrottle(models.Model):
    key=models.CharField(max_length=64,unique=True)
    failures=models.PositiveIntegerField(default=0)
    window_start=models.DateTimeField()
