import warnings
import zipfile
from pathlib import Path
from PIL import Image
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from .models import Resource,Quiz,Announcement,Doubt,Rating,Faculty,Profile,Complaint,Contact
from .services import ensure_legacy

def validate_attachment(f,images=False):
    if f.size>30*1024*1024:raise forms.ValidationError('Maximum file size is 30 MB.')
    ext=Path(f.name).suffix.lower();header=f.read(8);f.seek(0);valid=False
    try:
        if ext=='.pdf':valid=header.startswith(b'%PDF-')
        elif ext=='.txt':valid='\x00' not in f.read().decode('utf-8')
        elif ext in ('.docx','.pptx'):
            with zipfile.ZipFile(f) as z:
                valid=('word/document.xml' if ext=='.docx' else 'ppt/presentation.xml') in z.namelist() and '[Content_Types].xml' in z.namelist() and sum(i.file_size for i in z.infolist())<50*1024*1024
        elif images and ext in ('.jpg','.jpeg','.png'):
            with warnings.catch_warnings():
                warnings.simplefilter('error',Image.DecompressionBombWarning)
                image=Image.open(f);image.verify();valid=image.format in ('JPEG','PNG')
    except (ValueError,OSError,UnicodeDecodeError,zipfile.BadZipFile,Image.DecompressionBombError,Image.DecompressionBombWarning):valid=False
    finally:f.seek(0)
    if not valid:raise forms.ValidationError('Choose a valid PDF, UTF-8 TXT, DOCX or PPTX'+(', JPG or PNG' if images else '')+' file, up to 30 MB.')
    return f

class StudentRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    first_name=forms.CharField(label='Full name',max_length=100)
    enrollment=forms.CharField(max_length=50)
    department=forms.CharField(label='Course / department',max_length=50)
    phone=forms.CharField(max_length=10,required=False)
    year=forms.CharField(max_length=20,required=False)
    semester=forms.CharField(max_length=20,required=False)
    section=forms.CharField(max_length=5,required=False)
    batch=forms.CharField(max_length=30,required=False)
    class Meta(UserCreationForm.Meta):
        model=get_user_model()
        fields=['username','first_name','email','enrollment','department','phone','year','semester','section','batch']
    def clean_email(self):
        email=self.cleaned_data['email'].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():raise forms.ValidationError('An account with this email already exists.')
        return email
    def save(self,commit=True):
        user=super().save(commit)
        if commit:
            role=self.cleaned_data.get('role','student')
            Profile.objects.filter(user=user).update(role=role,enrollment=self.cleaned_data.get('enrollment',''),department=self.cleaned_data['department'])
            item=ensure_legacy(user,role)
            if role=='student':
                item.sen=self.cleaned_data.get('enrollment','');item.course=self.cleaned_data['department']
                item.sphone=self.cleaned_data.get('phone','');item.year=self.cleaned_data.get('year','')
                item.sem=self.cleaned_data.get('semester','');item.section=self.cleaned_data.get('section','');item.batch=self.cleaned_data.get('batch','');item.save()
            elif role=='faculty':
                item.fphone=self.cleaned_data.get('phone','');item.save(update_fields=['fphone'])
            elif role=='director':
                item.dphone=self.cleaned_data.get('phone','');item.save(update_fields=['dphone'])
        return user
class AccountForm(StudentRegistrationForm):
    role=forms.ChoiceField(choices=Profile.Role.choices)
    phone=forms.CharField(label='Phone number',max_length=15,required=False)
    class Meta(StudentRegistrationForm.Meta):fields=StudentRegistrationForm.Meta.fields+['role']
    def __init__(self,*args,role=Profile.Role.FACULTY,**kwargs):
        super().__init__(*args,**kwargs)
        self.initial['role']=role
        if self.is_bound:
            self.data=self.data.copy()
            self.data['role']=role
        self.fields['role'].widget=forms.HiddenInput()
        if role==Profile.Role.STUDENT:
            self.fields['phone']=forms.CharField(label='Phone number',max_length=10,required=False)
        else:
            self.fields['department'].label='Department'
            for name in ['enrollment','year','semester','section','batch']:
                self.fields.pop(name)
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Full name', max_length=100)
    email = forms.EmailField()
    department = forms.CharField(label='Department', max_length=50)
    phone = forms.CharField(label='Phone number', max_length=15, required=False)
    enrollment = forms.CharField(max_length=50, required=False)
    year = forms.CharField(max_length=20, required=False)
    semester = forms.CharField(max_length=20, required=False)
    section = forms.CharField(max_length=5, required=False)
    batch = forms.CharField(max_length=30, required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = self.instance.profile
        role = profile.role
        self.initial.update(department=profile.department, enrollment=profile.enrollment)
        relation = {'student': 'legacy_student', 'faculty': 'legacy_faculty', 'director': 'legacy_director'}[role]
        item = getattr(self.instance, relation, None)
        if item:
            self.initial['phone'] = getattr(item, {'student': 'sphone', 'faculty': 'fphone', 'director': 'dphone'}[role])
        if role == 'student':
            self.fields['phone'].max_length = 10
            if item:
                self.initial.update(year=item.year, semester=item.sem, section=item.section, batch=item.batch)
        else:
            for name in ['enrollment', 'year', 'semester', 'section', 'batch']:
                self.fields.pop(name)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if self.instance.profile.role == 'student' and len(phone) > 10:
            raise forms.ValidationError('Use at most 10 characters.')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if get_user_model().objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self):
        user = super().save()
        profile = user.profile
        profile.department = self.cleaned_data['department']
        if profile.role == 'student':
            profile.enrollment = self.cleaned_data['enrollment']
        profile.save()
        item = ensure_legacy(user, profile.role)
        data = self.cleaned_data
        if profile.role == 'student':
            item.sname, item.semail, item.unm = user.first_name, user.email, user.username[:50]
            item.sphone, item.sen, item.course = data['phone'], data['enrollment'], data['department']
            item.year, item.sem, item.section = data['year'], data['semester'], data['section']
            item.batch = data['batch']
        elif profile.role == 'faculty':
            item.fname, item.femail, item.fphone = user.first_name, user.email, data['phone']
        else:
            item.dname, item.demail, item.dphone = user.first_name, user.email, data['phone']
        item.save()
        from .models import AuthenticatedStudent, Teacher
        AuthenticatedStudent.objects.filter(user=user).update(name=user.first_name)
        Teacher.objects.filter(user=user).update(name=user.first_name)
        return user


class ResourceForm(forms.ModelForm):
    category=forms.ChoiceField(choices=Resource.CATEGORIES+[('__custom__','+ Add custom category')])
    custom_category=forms.CharField(max_length=100,required=False,label='Custom category',
        help_text='Enter a category name when you choose Add custom category.')
    class Meta:
        model=Resource
        fields=['title','subject','category','custom_category','description','file']
        widgets={
            'description':forms.Textarea(attrs={'rows':3}),
            'file':forms.ClearableFileInput(attrs={'accept':'.pdf,.txt,.docx,.pptx,.jpg,.jpeg,.png'}),
        }
        help_texts={'file':'PDF, TXT, DOCX, PPTX, JPG, JPEG or PNG. Maximum file size: 30 MB.'}
    def __init__(self,*args,category_choices=None,**kwargs):
        super().__init__(*args,**kwargs)
        if category_choices is not None:
            self.fields['category'].choices=list(category_choices)+[('__custom__','+ Add custom category')]
    def clean(self):
        data=super().clean()
        if data.get('category')=='__custom__':
            name=' '.join(data.get('custom_category','').split())
            if not name:
                self.add_error('custom_category','Enter a name for your custom category.')
            elif name=='__custom__':
                self.add_error('custom_category','Choose another category name.')
            else:
                for value,label in self.fields['category'].choices:
                    if value!='__custom__' and name.casefold() in (value.casefold(),label.casefold()):
                        name=value
                        break
                data['category']=name
        return data
    def clean_file(self):return validate_attachment(self.cleaned_data['file'],images=True)
class QuizForm(forms.ModelForm):
    class Meta:
        model=Quiz
        fields=['title','subject','starts_at','expiry_time']
        labels={'expiry_time':'Closes at (IST)','starts_at':'Opens at (IST)','is_active':'Published'}
        widgets={x:forms.DateTimeInput(attrs={'type':'datetime-local'},format='%Y-%m-%dT%H:%M') for x in ['starts_at','expiry_time']}
    def save(self, commit=True):
        quiz = super().save(commit=False)
        quiz.is_active = True
        quiz.require_name = True
        quiz.require_roll = True
        quiz.require_email = True
        quiz.require_class = True
        if commit:
            quiz.save()
            self.save_m2m()
        return quiz
    def clean(self):
        data=super().clean()
        if data.get('starts_at') and data.get('expiry_time') and data['expiry_time']<=data['starts_at']:self.add_error('expiry_time','Closing time must be after opening time.')
        return data
class QuestionEntryForm(forms.Form):
    text=forms.CharField(label='Question',max_length=5000,widget=forms.Textarea(attrs={'rows':2}))
    image=forms.ImageField(required=False,label='Question image (JPG/PNG, optional)')
    is_multiple=forms.BooleanField(required=False,label='Allow multiple correct options')
    option_count=forms.IntegerField(min_value=2,max_value=26,initial=4,required=False,widget=forms.HiddenInput())
    option_a=forms.CharField(max_length=255)
    option_b=forms.CharField(max_length=255)
    option_c=forms.CharField(max_length=255,required=False)
    option_d=forms.CharField(max_length=255,required=False)
    correct=forms.MultipleChoiceField(choices=[(chr(65+i),chr(65+i)) for i in range(26)],widget=forms.CheckboxSelectMultiple)
    DELETE=forms.BooleanField(required=False,label='Remove this question')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for key in 'efghijklmnopqrstuvwxyz':
            self.fields['option_'+key]=forms.CharField(max_length=255,required=False)
        names=['text','image','is_multiple','option_count']+['option_'+chr(97+i) for i in range(26)]+['correct','DELETE']
        self.order_fields(names)

    def clean_image(self):
        f=self.cleaned_data.get('image')
        return validate_attachment(f,images=True) if f else None
    def clean(self):
        data=super().clean()
        if data.get('DELETE'):return data
        count=data.get('option_count') or 4
        keys=[chr(65+i) for i in range(count)]
        if self.add_prefix('option_count') in self.data:
            for key in keys:
                if not data.get('option_'+key.lower()):self.add_error('option_'+key.lower(),'Enter option text.')
        for i in range(count,26):data.pop('option_'+chr(97+i),None)
        correct=data.get('correct',[])
        if any(key not in keys for key in correct):self.add_error('correct','Choose correct answers only from the current options.')
        if not data.get('is_multiple') and len(correct)!=1:self.add_error('correct','Choose exactly one correct option for a single-choice question.')
        for key in correct:
            if not data.get('option_'+key.lower()):self.add_error('correct','Every selected correct option needs option text.')
        return data
QuestionFormSet=formset_factory(QuestionEntryForm,extra=0,min_num=1,validate_min=True,max_num=50,validate_max=True,can_delete=True)
class StudentInfoForm(forms.Form):
    student_name=forms.CharField(max_length=255,required=False,label='Full name')
    roll_no=forms.CharField(max_length=50,required=False,label='Roll / enrollment number')
    email=forms.EmailField(required=False)
    course=forms.CharField(max_length=50,required=False,label='Course / class')
    year=forms.CharField(max_length=20,required=False,label='Year')
    semester=forms.CharField(max_length=20,required=False,label='Semester')
    section=forms.CharField(max_length=5,required=False,label='Section')
    batch=forms.CharField(max_length=30,required=False,label='Batch')
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model=Announcement
        fields=['title','content','document','audience']
    def clean_document(self):
        f=self.cleaned_data.get('document');return validate_attachment(f,images=True) if f else None
class FacultyChoiceMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['faculty'].queryset=Faculty.objects.filter(user__is_active=True,user__profile__role='faculty').select_related('user').order_by('fname','id')
class ComplaintForm(FacultyChoiceMixin,forms.Form):
    faculty=forms.ModelChoiceField(queryset=Faculty.objects.none())
    title=forms.CharField(max_length=180)
    body=forms.CharField(widget=forms.Textarea,max_length=10000)
class DoubtForm(FacultyChoiceMixin,forms.ModelForm):
    class Meta:
        model=Doubt
        fields=['faculty','subject','doubt','attachment']
    def clean_attachment(self):
        f=self.cleaned_data.get('attachment');return validate_attachment(f,images=True) if f else None
class FeedbackForm(FacultyChoiceMixin,forms.ModelForm):
    class Meta:
        model=Rating
        fields=['faculty','rating','comment']
        widgets={'rating':forms.Select(choices=[(i,f'{i} / 5') for i in range(1,6)])}
class ReplyForm(forms.Form):
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':4}),max_length=5000)
    status=forms.ChoiceField(choices=Complaint.STATUSES,required=False)
class AnswerForm(forms.Form):
    answer=forms.CharField(widget=forms.Textarea(attrs={'rows':4}),max_length=5000)
class NotificationForm(forms.Form):
    title=forms.CharField(max_length=180)
    message=forms.CharField(widget=forms.Textarea,max_length=5000)
    audience=forms.ChoiceField(choices=Announcement.AUDIENCES)
class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields=['name','email','title','message']
