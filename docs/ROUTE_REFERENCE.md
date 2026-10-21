# Route reference

Paths are relative to the application host. Local example: `http://127.0.0.1:8000/`.

The Methods column describes verbs used by the interface. Explicit method decorators enforce POST for mutations such as downloads, mark-read, publication toggles and account deactivation; the quiz-attempt view explicitly permits GET/POST. Other read views do not all reject alternative verbs. This is a server-rendered HTML application; these URLs are not a JSON REST API.

`pk` and `submission_id` are integer identifiers. `kind` selects an allowed attachment or report type. An authenticated user with an incorrect role receives a permission error; missing/foreign private objects may return 404.

## Current and compatibility routes

| Path | URL name | View | Methods | Access | Fixed arguments |
| --- | --- | --- | --- | --- | --- |
| `/accounts/profile/` | `profile_edit` | profile_edit | GET, POST | Authenticated; own account only | — |
| `/dashboard/` | `dashboard` | dashboard | GET | Authenticated | — |
| `/` | `index` | index | GET | Public | — |
| `/index/` | `—` | index | GET | Public | — |
| `/contact/` | `contact` | contact | GET, POST | Public | — |
| `/health/` | `health` | health | GET | Public | — |
| `/campus-life/` | `campus_life` | campus_life | GET | Public | — |
| `/question-images/<int:pk>/` | `question_image` | question_image | GET | Authenticated; quiz access checks | — |
| `/attachments/<str:kind>/<int:pk>/` | `attachment_download` | attachment_download | POST | Authenticated; object/audience checks | — |
| `/submission-details/` | `submission_detail_list` | submission_detail_list | GET | Own student; creator faculty; director | — |
| `/resources/` | `resources` | resources | GET | Authenticated | — |
| `/resources/upload/` | `resource_create` | resource_create | GET, POST | Faculty or director | — |
| `/resources/<int:pk>/download/` | `resource_download` | resource_download | POST | Authenticated | — |
| `/notifications/` | `notifications` | notifications | GET | Own inbox | — |
| `/notifications/send/` | `notification_create` | notification_create | GET, POST | Faculty or director | — |
| `/notifications/read-all/` | `notifications_read_all` | notifications_read_all | POST | Own inbox | — |
| `/notifications/<int:pk>/read/` | `notification_read` | notification_read | POST | Own notification | — |
| `/announcements/` | `announcements` | announcements | GET | Authenticated; audience filtered | — |
| `/announcements/create/` | `announcement_create` | announcement_create | GET, POST | Faculty or director | — |
| `/quizzes/` | `quizzes` | quizzes | GET | Authenticated; role filtered | — |
| `/quizzes/create/` | `quiz_create` | quiz_create | GET, POST | Faculty or director | — |
| `/quizzes/<int:pk>/toggle/` | `quiz_toggle` | quiz_toggle | POST | Creator faculty or director | — |
| `/quizzes/<int:pk>/attempt/` | `quiz_attempt` | quiz_attempt | GET, POST | Student; open published valid quiz | — |
| `/quizzes/<int:pk>/result/` | `quiz_result` | quiz_result | GET | Own student attempt; creator faculty; director | — |
| `/quizzes/<int:pk>/leaderboard/` | `leaderboard` | leaderboard | GET | Authenticated; publication/ownership checks | — |
| `/complaints/` | `complaints` | complaints | GET | Own student; assigned faculty; director | — |
| `/complaints/new/` | `complaint_create` | complaint_create | GET, POST | Student | — |
| `/complaints/<int:pk>/` | `complaint_detail` | complaint_detail | GET, POST | Own student; assigned faculty; director | — |
| `/doubts/` | `doubts` | doubts | GET | Own student; assigned faculty; director | — |
| `/doubts/new/` | `doubt_create` | doubt_create | GET, POST | Student | — |
| `/doubts/<int:pk>/answer/` | `doubt_answer` | doubt_answer | GET, POST | Assigned faculty only | — |
| `/feedback/` | `feedback` | feedback | GET, POST | Authenticated; only students can POST | — |
| `/accounts/manage/` | `accounts` | accounts | GET | Director | — |
| `/accounts/manage/new/` | `account_create` | account_create | GET, POST | Director | — |
| `/accounts/manage/<int:pk>/toggle/` | `account_toggle` | account_toggle | POST | Director | — |
| `/reports/` | `reports` | reports | GET | Director | — |
| `/reports/<str:kind>/export/` | `report_export` | report_export | GET | Director | — |
| `/student-registration/` | `student_registration` | register | GET, POST | Public; creates students only | — |
| `/faculty-registration/` | `faculty_registration` | account_create | GET, POST | Director | role=faculty |
| `/director-registration/` | `director_registration` | account_create | GET, POST | Director | role=director |
| `/student-login/` | `student_login` | sign_in | GET, POST | Public; optional route-specific role | role=student |
| `/faculty-login/` | `faculty_login` | sign_in | GET, POST | Public; optional route-specific role | role=faculty |
| `/director-login/` | `director_login` | sign_in | GET, POST | Public; optional route-specific role | role=director |
| `/student_dashboard/` | `student_dashboard` | student_dashboard | GET | Student | — |
| `/faculty_dashboard/` | `faculty_dashboard` | faculty_dashboard | GET | Faculty | — |
| `/Director_dashboard/` | `Director_dashboard` | Director_dashboard | GET | Director | — |
| `/create-quiz/` | `create_quiz` | quiz_create | GET, POST | Faculty or director | — |
| `/teacher/` | `teacher_quiz_list` | quizzes | GET | Authenticated; role filtered | — |
| `/student/` | `student_quiz_list` | quizzes | GET | Authenticated; role filtered | — |
| `/attempt/<int:pk>/` | `attempt_quiz` | quiz_attempt | GET, POST | Student; open published valid quiz | — |
| `/submit/<int:pk>/` | `submit_quiz` | quiz_attempt | GET, POST | Student; open published valid quiz | — |
| `/submissions/<int:pk>/` | `quiz_submissions` | quiz_result | GET | Own student attempt; creator faculty; director | — |
| `/score/<int:submission_id>/` | `view_score` | legacy_score | GET | Own student; creator faculty; director | — |
| `/doubt/` | `doubt` | doubt_create | GET, POST | Student | — |
| `/doubt-viewer/` | `doubt_viewer` | doubts | GET | Own student; assigned faculty; director | — |
| `/rating/` | `rating` | feedback | GET, POST | Authenticated; only students can POST | — |
| `/announcements/add/` | `add_announcement` | announcement_create | GET, POST | Faculty or director | — |
| `/announcements/` | `announcement` | announcements | GET | Authenticated; audience filtered | — |
| `/complaints/add/` | `add_complaint` | complaint_create | GET, POST | Student | — |
| `/complaints/` | `complaints_list` | complaints | GET | Own student; assigned faculty; director | — |
| `/complaints/reply/<int:pk>/` | `teacher_reply` | complaint_detail | GET, POST | Own student; assigned faculty; director | — |

## Authentication and administration

| Path | URL name | Methods | Access |
| --- | --- | --- | --- |
| `/admin/` | Django admin URL namespace | GET / POST | Django staff/superuser authorization; application director role alone does not grant admin access. |
| `/accounts/login/` | `login` | GET, POST | Public login |
| `/accounts/register/` | `register` | GET, POST | Public student registration |
| `/accounts/logout/` | `logout` | POST | Authenticated |
| `/accounts/password/change/` | `password_change` | GET, POST | Authenticated |
| `/accounts/password/change/done/` | `password_change_done` | GET | Authenticated |

## Duplicate paths and aliases

Django resolves the first matching URL pattern. Several retained names reverse to the same path and use the same upgraded view:

- `/announcements/`: `announcements`, `announcement`.
- `/complaints/`: `complaints`, `complaints_list`.

The legacy `/score/<submission_id>/` path looks up a Submission ID; the modern quiz result route uses a Quiz ID. Path case matters: `/Director_dashboard/` retains its original capitalization.

## Query parameters

| Page | Parameter | Behavior |
| --- | --- | --- |
| Resources | q | Case-insensitive title, description and subject search; stripped to 150 characters. |
| Resources | category | notes, pyq or assignment; matches the stored category. |
| Resources | subject | Case-insensitive exact subject; stripped to 100 characters. |
| Resources | sort=title | Alphabetical title, then ID; otherwise model ordering is newest first. |
| Quizzes | code | Uppercase exact quiz code, stripped to six characters. |
| Complaints | status | Stored status code; pending, in_progress or resolved. |
| Account creation | role | GET selects faculty, student or director; faculty is the default. Legacy staff routes fix the role. |
| Paginated lists | page | Page number; 15 records per page. |
