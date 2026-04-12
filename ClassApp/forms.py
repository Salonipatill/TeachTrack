# forms.py
from django import forms
from .models import Quiz, Question, Option, Submission, Announcement
from django.utils import timezone
import pytz

class QuizCreateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'require_name', 'require_roll', 'require_email', 'require_class']

    # override save to set expiry_time to today's midnight Asia/Kolkata
    def save(self, commit=True):
        quiz = super().save(commit=False)
        if not quiz.expiry_time:
            india = pytz.timezone("Asia/Kolkata")
            now_india = timezone.now().astimezone(india)
            # expiry is the upcoming midnight (00:00 of next day)
            tomorrow = (now_india + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            quiz.expiry_time = tomorrow.astimezone(pytz.UTC)
        if commit:
            quiz.save()
        return quiz


class QuestionForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Question
        fields = ['text', 'image', 'is_multiple']


# Student info form (dynamically enforce required fields in view)
class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['student_name', 'roll_no', 'email', 'class_div']

# forms.py
from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'document']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter announcement title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write announcement details'
            }),
        }