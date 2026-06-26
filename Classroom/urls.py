from django.contrib import admin
from django.urls import path, include
from ClassApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,name='index'),
    path('index/', views.index,name='index'),
    path('student-registration/', views.student_registration,name='student_registration'),
    path('faculty-registration/', views.faculty_registration, name='faculty_registration'),
    path('director-registration/', views.director_registration, name='director_registration'),
    path('student-login/', views.student_login,name='student_login'),
    path('faculty-login/', views.faculty_login, name='faculty_login'),
    path('director-login/', views.director_login, name='director_login'),
    path('student-forgot_password/', views.student_forgot_password, name='student_forgot_password'),
    path('faculty-forgot_password/', views.faculty_forgot_password, name='faculty_forgot_password'),
    path('director-forgot_password/', views.director_forgot_password, name='director_forgot_password'),
    path('contact/', views.contact, name='contact'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty_dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('Director_dashboard/', views.Director_dashboard, name='Director_dashboard'),
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('teacher/', views.teacher_quiz_list, name='teacher_quiz_list'),
    path('student/', views.student_quiz_list, name='student_quiz_list'),
    path('attempt/<int:quiz_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('submit/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('submissions/<int:quiz_id>/', views.quiz_submissions, name='quiz_submissions'),
    path('score/<int:submission_id>/', views.view_score, name='view_score'),
    path("submission-details/", views.submission_detail_list, name="submission_detail_list"),
    path('doubt/', views.doubt, name='doubt'),
    path('doubt-viewer/', views.doubt_viewer, name='doubt_viewer'),
    path('rating/',views.rating, name='rating'),
    path('announcements/', views.announcement, name='announcement'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    path("complaints/", views.complaints_list, name="complaints_list"),
    path("complaints/add/", views.add_complaint, name="add_complaint"),
    path("complaints/reply/<int:id>/", views.teacher_reply, name="teacher_reply"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)