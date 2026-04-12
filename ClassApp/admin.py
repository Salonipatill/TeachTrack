from django.contrib import admin
from ClassApp.models import Student, Faculty, Director, ImageUploader, Contact, Quiz, Doubt, SubmissionDetail, Announcement,Rating

# Register your models here.
class StudentAdmin(admin.ModelAdmin):list_display=['sname','sen','sphone','semail','course','year','sem','section','unm','pw']
class FacultyAdmin(admin.ModelAdmin):list_display=['fname','fphone','femail','unm','pw']
class DirectorAdmin(admin.ModelAdmin):list_display=['dname','dphone','demail','unm','pw']
class ContactAdmin(admin.ModelAdmin):list_display=['name','email','title','message']
class QuizAdmin(admin.ModelAdmin):list_display=['title','created_at','expiry_time','is_active','require_name','require_roll','require_email','require_class']
class ImageUploaderAdmin(admin.ModelAdmin):list_display=['photo','date']
class SubmissionDetailAdmin(admin.ModelAdmin):list_display = ['student_name','roll_no','email','class_div','quiz','question','score']
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'created_at', 'document']
    list_filter = ['created_at', 'posted_by']
    search_fields = ['title', 'content']

admin.site.register(SubmissionDetail, SubmissionDetailAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Quiz,QuizAdmin)
admin.register(ImageUploader)

@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_name', 'faculty', 'submitted_at')
    list_filter = ('faculty', 'submitted_at')
    search_fields = ('student_name', 'student_email', 'doubt')

admin.site.register(Announcement, AnnouncementAdmin)


@admin.register(Rating)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_name', 'faculty', 'submitted_at')
    list_filter = ('faculty', 'submitted_at')
    search_fields = ('student_name', 'student_email', 'rating')