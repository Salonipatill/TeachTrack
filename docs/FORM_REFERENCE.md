# Forms and validation reference

Extracted from active form classes. Required marks below apply to an unbound form; quiz-attempt identity fields become required according to that quiz’s four requirement flags.

Public student registration ignores injected role or superuser fields. Director-only account routes determine the selected role on the server and remove student-only academic fields for staff. Phone inputs limit character length; they do not implement a numeric-only or international telephone-number validator.

## StudentRegistrationForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `username` | Username | UsernameField | Yes | TextInput | max_length=150 |
| `first_name` | Full name | CharField | Yes | TextInput | max_length=100 |
| `email` | Email | EmailField | Yes | EmailInput | max_length=320 |
| `enrollment` | Enrollment | CharField | Yes | TextInput | max_length=50 |
| `department` | Course / department | CharField | Yes | TextInput | max_length=50 |
| `phone` | Phone | CharField | No | TextInput | max_length=10 |
| `year` | Year | CharField | No | TextInput | max_length=20 |
| `semester` | Semester | CharField | No | TextInput | max_length=20 |
| `section` | Section | CharField | No | TextInput | max_length=5 |
| `password1` | Password | CharField | Yes | PasswordInput | Default Django field validation |
| `password2` | Password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## AccountForm — student

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `username` | Username | UsernameField | Yes | TextInput | max_length=150 |
| `first_name` | Full name | CharField | Yes | TextInput | max_length=100 |
| `email` | Email | EmailField | Yes | EmailInput | max_length=320 |
| `enrollment` | Enrollment | CharField | Yes | TextInput | max_length=50 |
| `department` | Course / department | CharField | Yes | TextInput | max_length=50 |
| `phone` | Phone number | CharField | No | TextInput | max_length=10 |
| `year` | Year | CharField | No | TextInput | max_length=20 |
| `semester` | Semester | CharField | No | TextInput | max_length=20 |
| `section` | Section | CharField | No | TextInput | max_length=5 |
| `role` | Role | ChoiceField | Yes | HiddenInput | choices: student, faculty, director; hidden input |
| `password1` | Password | CharField | Yes | PasswordInput | Default Django field validation |
| `password2` | Password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## AccountForm — faculty

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `username` | Username | UsernameField | Yes | TextInput | max_length=150 |
| `first_name` | Full name | CharField | Yes | TextInput | max_length=100 |
| `email` | Email | EmailField | Yes | EmailInput | max_length=320 |
| `department` | Department | CharField | Yes | TextInput | max_length=50 |
| `phone` | Phone number | CharField | No | TextInput | max_length=15 |
| `role` | Role | ChoiceField | Yes | HiddenInput | choices: student, faculty, director; hidden input |
| `password1` | Password | CharField | Yes | PasswordInput | Default Django field validation |
| `password2` | Password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## AccountForm — director

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `username` | Username | UsernameField | Yes | TextInput | max_length=150 |
| `first_name` | Full name | CharField | Yes | TextInput | max_length=100 |
| `email` | Email | EmailField | Yes | EmailInput | max_length=320 |
| `department` | Department | CharField | Yes | TextInput | max_length=50 |
| `phone` | Phone number | CharField | No | TextInput | max_length=15 |
| `role` | Role | ChoiceField | Yes | HiddenInput | choices: student, faculty, director; hidden input |
| `password1` | Password | CharField | Yes | PasswordInput | Default Django field validation |
| `password2` | Password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## ResourceForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `title` | Title | CharField | Yes | TextInput | max_length=180 |
| `subject` | Subject | CharField | Yes | TextInput | max_length=100 |
| `category` | Category | TypedChoiceField | Yes | Select | choices: , notes, pyq, assignment |
| `description` | Description | CharField | No | Textarea | Default Django field validation |
| `file` | File | FileField | Yes | ClearableFileInput | max_length=255 |

## QuizForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `title` | Title | CharField | Yes | TextInput | max_length=255 |
| `subject` | Subject | CharField | No | TextInput | max_length=100 |
| `starts_at` | Opens at (IST) | DateTimeField | Yes | DateTimeInput | Default Django field validation |
| `expiry_time` | Closes at (IST) | DateTimeField | Yes | DateTimeInput | Default Django field validation |
| `is_active` | Published | BooleanField | No | CheckboxInput | Default Django field validation |
| `require_name` | Require name | BooleanField | No | CheckboxInput | Default Django field validation |
| `require_roll` | Require roll | BooleanField | No | CheckboxInput | Default Django field validation |
| `require_email` | Require email | BooleanField | No | CheckboxInput | Default Django field validation |
| `require_class` | Require class | BooleanField | No | CheckboxInput | Default Django field validation |

## QuestionEntryForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `text` | Question | CharField | Yes | Textarea | max_length=5000 |
| `image` | Question image (JPG/PNG, optional) | ImageField | No | ClearableFileInput | Default Django field validation |
| `is_multiple` | Allow multiple correct options | BooleanField | No | CheckboxInput | Default Django field validation |
| `option_a` | Option a | CharField | Yes | TextInput | max_length=255 |
| `option_b` | Option b | CharField | Yes | TextInput | max_length=255 |
| `option_c` | Option c | CharField | No | TextInput | max_length=255 |
| `option_d` | Option d | CharField | No | TextInput | max_length=255 |
| `correct` | Correct | MultipleChoiceField | Yes | CheckboxSelectMultiple | choices: A, B, C, D |
| `DELETE` | Remove this question | BooleanField | No | CheckboxInput | Default Django field validation |

## StudentInfoForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `student_name` | Full name | CharField | No | TextInput | max_length=255 |
| `roll_no` | Roll / enrollment number | CharField | No | TextInput | max_length=50 |
| `email` | Email | EmailField | No | EmailInput | max_length=320 |
| `class_div` | Class / division | CharField | No | TextInput | max_length=50 |

## AnnouncementForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `title` | Title | CharField | Yes | TextInput | max_length=200 |
| `content` | Content | CharField | Yes | Textarea | Default Django field validation |
| `document` | Document | FileField | No | ClearableFileInput | max_length=100 |
| `audience` | Audience | TypedChoiceField | Yes | Select | choices: all, student, faculty, director |

## ComplaintForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `faculty` | Faculty | ModelChoiceField | Yes | Select | Authorized model choices; see workflow rules |
| `title` | Title | CharField | Yes | TextInput | max_length=180 |
| `body` | Body | CharField | Yes | Textarea | max_length=10000 |

## DoubtForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `faculty` | Faculty | ModelChoiceField | Yes | Select | Authorized model choices; see workflow rules |
| `subject` | Subject | CharField | No | TextInput | max_length=100 |
| `doubt` | Doubt | CharField | Yes | Textarea | Default Django field validation |
| `attachment` | Attachment | FileField | No | ClearableFileInput | max_length=100 |

## FeedbackForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `faculty` | Faculty | ModelChoiceField | Yes | Select | Authorized model choices; see workflow rules |
| `rating` | Rating | IntegerField | Yes | Select | min_value=0 |
| `comment` | Comment | CharField | No | Textarea | Default Django field validation |

## ReplyForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `message` | Message | CharField | Yes | Textarea | max_length=5000 |
| `status` | Status | ChoiceField | No | Select | choices: pending, in_progress, resolved |

## AnswerForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `answer` | Answer | CharField | Yes | Textarea | max_length=5000 |

## NotificationForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `title` | Title | CharField | Yes | TextInput | max_length=180 |
| `message` | Message | CharField | Yes | Textarea | max_length=5000 |
| `audience` | Audience | ChoiceField | Yes | Select | choices: all, student, faculty, director |

## ContactForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `name` | Name | CharField | Yes | TextInput | max_length=100 |
| `email` | Email | EmailField | Yes | EmailInput | max_length=254 |
| `title` | Title | CharField | Yes | TextInput | max_length=200 |
| `message` | Message | CharField | Yes | Textarea | Default Django field validation |

## Django AuthenticationForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `username` | Username | UsernameField | Yes | TextInput | max_length=150 |
| `password` | Password | CharField | Yes | PasswordInput | Default Django field validation |

## Django PasswordChangeForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `old_password` | Old password | CharField | Yes | PasswordInput | Default Django field validation |
| `new_password1` | New password | CharField | Yes | PasswordInput | Default Django field validation |
| `new_password2` | New password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## Django PasswordResetForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `email` | Email | EmailField | Yes | EmailInput | max_length=254 |

## Django SetPasswordForm

| Field | Label | Field type | Required | Widget | Validation / choices |
| --- | --- | --- | --- | --- | --- |
| `new_password1` | New password | CharField | Yes | PasswordInput | Default Django field validation |
| `new_password2` | New password confirmation | CharField | Yes | PasswordInput | Default Django field validation |

## Additional server rules

- Email uniqueness is checked case-insensitively in the account form; the email is stored lowercase. Django User.email itself is not made globally unique by a database constraint.
- Passwords use Django’s configured similarity, minimum-length (10), common-password and numeric-only rejection validators.
- The quiz closing time must be later than the opening time.
- QuestionFormSet requires 1–50 question forms and uses the `questions` prefix. Options A and B are mandatory; C and D are optional.
- A single-selection question needs exactly one marked correct option. Every marked correct option needs text.
- Multiple-selection questions are also checked by valid_quiz before students can attempt them; a valid quiz needs at least one correct option per question.
- Complaint, doubt and feedback faculty choices include only active faculty users with the faculty role, ordered by name then ID.
- Faculty announcement and notification forms permit the Students audience only; directors may choose all configured audiences.
- A complaint reply requires a message up to 5,000 characters. Only directors receive the status input. A complaint body accepts up to 10,000 characters.
- Resource, announcement and doubt file validation and image safety checks are detailed in the handbook Security and uploads chapter.
- AuthenticationForm, password-change and token-reset forms come from Django. The login field is a username, not an email identifier.
