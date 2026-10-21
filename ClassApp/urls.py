from django.urls import path
from . import views as v
urlpatterns = [path('accounts/profile/', v.profile_edit, name='profile_edit')]
urlpatterns += [path('dashboard/',v.dashboard,name='dashboard'), path('',v.index,name='index'),path('index/',v.index),path('contact/',v.contact,name='contact'), path('health/',v.health,name='health'),
 path('campus-life/',v.campus_life,name='campus_life'),
 path('question-images/<int:pk>/',v.question_image,name='question_image'),path('attachments/<str:kind>/<int:pk>/',v.attachment_download,name='attachment_download'),path('submission-details/',v.submission_detail_list,name='submission_detail_list'),path('resources/',v.resources,name='resources'),path('resources/upload/',v.resource_create,name='resource_create'),
 path('resources/<int:pk>/download/',v.resource_download,name='resource_download'),
 path('notifications/',v.notifications,name='notifications'),path('notifications/send/',v.notification_create,name='notification_create'),
 path('notifications/read-all/',v.notifications_read_all,name='notifications_read_all'),path('notifications/<int:pk>/read/',v.notification_read,name='notification_read'),
 path('announcements/',v.announcements,name='announcements'),path('announcements/create/',v.announcement_create,name='announcement_create'),
 path('quizzes/',v.quizzes,name='quizzes'),path('quizzes/create/',v.quiz_create,name='quiz_create'),
 path('quizzes/<int:pk>/toggle/',v.quiz_toggle,name='quiz_toggle'),path('quizzes/<int:pk>/attempt/',v.quiz_attempt,name='quiz_attempt'),
 path('quizzes/<int:pk>/result/',v.quiz_result,name='quiz_result'),path('quizzes/<int:pk>/leaderboard/',v.leaderboard,name='leaderboard'),
 path('complaints/',v.complaints,name='complaints'),path('complaints/new/',v.complaint_create,name='complaint_create'),
 path('complaints/<int:pk>/',v.complaint_detail,name='complaint_detail'),path('doubts/',v.doubts,name='doubts'),
 path('doubts/new/',v.doubt_create,name='doubt_create'),path('doubts/<int:pk>/answer/',v.doubt_answer,name='doubt_answer'),
 path('feedback/',v.feedback,name='feedback'),path('accounts/manage/',v.accounts,name='accounts'),
 path('accounts/manage/new/',v.account_create,name='account_create'),path('accounts/manage/<int:pk>/toggle/',v.account_toggle,name='account_toggle'),
 path('reports/',v.reports,name='reports'),path('reports/<str:kind>/export/',v.report_export,name='report_export')]

# Original URLs remain available and use the upgraded authorization checks.
urlpatterns += [
 path('student-registration/',v.register,name='student_registration'),
 path('faculty-registration/',v.account_create,{'role':'faculty'},name='faculty_registration'),
 path('director-registration/',v.account_create,{'role':'director'},name='director_registration'),
 path('student-login/',v.sign_in,{'role':'student'},name='student_login'),path('faculty-login/',v.sign_in,{'role':'faculty'},name='faculty_login'),path('director-login/',v.sign_in,{'role':'director'},name='director_login'),
 path('student_dashboard/',v.student_dashboard,name='student_dashboard'),path('faculty_dashboard/',v.faculty_dashboard,name='faculty_dashboard'),path('Director_dashboard/',v.Director_dashboard,name='Director_dashboard'),
 path('create-quiz/',v.quiz_create,name='create_quiz'),path('teacher/',v.quizzes,name='teacher_quiz_list'),path('student/',v.quizzes,name='student_quiz_list'),
 path('attempt/<int:pk>/',v.quiz_attempt,name='attempt_quiz'),path('submit/<int:pk>/',v.quiz_attempt,name='submit_quiz'),path('submissions/<int:pk>/',v.quiz_result,name='quiz_submissions'),path('score/<int:submission_id>/',v.legacy_score,name='view_score'),
 path('doubt/',v.doubt_create,name='doubt'),path('doubt-viewer/',v.doubts,name='doubt_viewer'),path('rating/',v.feedback,name='rating'),
 path('announcements/add/',v.announcement_create,name='add_announcement'),path('announcements/',v.announcements,name='announcement'),
 path('complaints/add/',v.complaint_create,name='add_complaint'),path('complaints/',v.complaints,name='complaints_list'),path('complaints/reply/<int:pk>/',v.complaint_detail,name='teacher_reply')]
