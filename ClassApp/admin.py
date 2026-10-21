from django.contrib import admin
from .models import (Student,Faculty,Director,Profile,Contact,ImageUploader,Quiz,Question,Option,Submission,SubmissionAnswer,SubmissionDetail,Doubt,Announcement,Rating,AuthenticatedStudent,Teacher,Complaint,ComplaintEvent,Resource,Download,Notification)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','role','department','enrollment']
    list_filter=['role','department']
    search_fields=['user__username','user__first_name','enrollment']
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display=['sname','sen','course','year','sem','section','user']
    search_fields=['sname','sen','semail']
    readonly_fields=['user']
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display=['fname','femail','user']
    readonly_fields=['user']
@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display=['dname','demail','user']
    readonly_fields=['user']
for model in [Contact,ImageUploader,Quiz,Question,Option,Submission,SubmissionAnswer,SubmissionDetail,Doubt,Announcement,Rating,AuthenticatedStudent,Teacher,Complaint,ComplaintEvent,Resource,Download,Notification]:admin.site.register(model)
admin.site.site_header='TeachTrack administration'
admin.site.site_title='TeachTrack'
