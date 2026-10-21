# Test catalogue

53 test methods are defined in `ClassApp/tests.py`. This catalogue describes source coverage; a successful test execution must be recorded separately.

| Test class | Method | Scenario |
| --- | --- | --- |
| WorkspaceTests | `test_all_role_pages_render` | all role pages render |
| WorkspaceTests | `test_guests_require_login` | guests require login |
| WorkspaceTests | `test_student_cannot_access_staff_actions` | student cannot access staff actions |
| WorkspaceTests | `test_registration_hashes_password_and_ignores_role_injection` | registration hashes password and ignores role injection |
| WorkspaceTests | `test_login_throttle` | login throttle |
| WorkspaceTests | `test_role_login_pages_and_matching_accounts` | role login pages and matching accounts |
| WorkspaceTests | `test_role_login_mismatch_explains_where_to_sign_in` | role login mismatch explains where to sign in |
| WorkspaceTests | `test_csrf_and_logout_method` | csrf and logout method |
| WorkspaceTests | `test_password_reset_email` | password reset email |
| WorkspaceTests | `test_resource_upload_search_and_notification` | resource upload search and notification |
| WorkspaceTests | `test_reject_fake_pdf_and_html` | reject fake pdf and html |
| WorkspaceTests | `test_oversized_and_binary_txt_rejected` | oversized and binary txt rejected |
| WorkspaceTests | `test_download_authenticated_and_counted` | download authenticated and counted |
| WorkspaceTests | `test_missing_resource_does_not_increment` | missing resource does not increment |
| WorkspaceTests | `test_notifications_are_private_and_mutations_post_only` | notifications are private and mutations post only |
| WorkspaceTests | `test_notification_open_redirect_blocked` | notification open redirect blocked |
| WorkspaceTests | `test_announcement_audience` | announcement audience |
| WorkspaceTests | `test_create_quiz_formset` | create quiz formset |
| WorkspaceTests | `test_quiz_rejects_empty_questions` | quiz rejects empty questions |
| WorkspaceTests | `test_quiz_scoring_and_duplicate_submission` | quiz scoring and duplicate submission |
| WorkspaceTests | `test_answers_withheld_until_close` | answers withheld until close |
| WorkspaceTests | `test_incomplete_quiz_is_not_submitted` | incomplete quiz is not submitted |
| WorkspaceTests | `test_closed_upcoming_and_unpublished_quizzes` | closed upcoming and unpublished quizzes |
| WorkspaceTests | `test_other_faculty_cannot_manage_quiz` | other faculty cannot manage quiz |
| WorkspaceTests | `test_students_only_see_their_submission_details` | students only see their submission details |
| WorkspaceTests | `test_complaint_creation_and_status_history` | complaint creation and status history |
| WorkspaceTests | `test_complaint_object_access` | complaint object access |
| WorkspaceTests | `test_feedback_upsert_and_range` | feedback upsert and range |
| WorkspaceTests | `test_feedback_db_constraint` | feedback db constraint |
| WorkspaceTests | `test_doubt_answer_permission_and_notification` | doubt answer permission and notification |
| WorkspaceTests | `test_account_creation_and_deactivation` | account creation and deactivation |
| WorkspaceTests | `test_staff_creation_forms_exclude_student_details` | staff creation forms exclude student details |
| WorkspaceTests | `test_staff_registration_fixes_role_and_saves_contact_details` | staff registration fixes role and saves contact details |
| WorkspaceTests | `test_director_created_student_requires_and_saves_academic_details` | director created student requires and saves academic details |
| WorkspaceTests | `test_director_cannot_deactivate_self` | director cannot deactivate self |
| WorkspaceTests | `test_report_export_alphabetical_and_csv_safe` | report export alphabetical and csv safe |
| WorkspaceTests | `test_dashboard_no_removed_performance_sections` | dashboard no removed performance sections |
| WorkspaceTests | `test_legacy_import_dry_run_and_hashing` | legacy import dry run and hashing |
| WorkspaceTests | `test_director_bootstrap_command` | director bootstrap command |
| WorkspaceTests | `test_password_change_invalidates_old_password` | password change invalidates old password |
| WorkspaceTests | `test_deactivation_revokes_existing_session` | deactivation revokes existing session |
| WorkspaceTests | `test_original_role_urls_enforce_correct_role` | original role urls enforce correct role |
| WorkspaceTests | `test_original_quiz_answer_and_detail_tables_are_written` | original quiz answer and detail tables are written |
| WorkspaceTests | `test_multi_select_requires_exact_correct_set` | multi select requires exact correct set |
| WorkspaceTests | `test_forged_options_from_other_question_rejected` | forged options from other question rejected |
| WorkspaceTests | `test_required_original_quiz_details_are_validated` | required original quiz details are validated |
| WorkspaceTests | `test_invalid_legacy_quiz_cannot_be_attempted_or_published` | invalid legacy quiz cannot be attempted or published |
| WorkspaceTests | `test_private_original_doubt_attachment` | private original doubt attachment |
| WorkspaceTests | `test_original_announcement_upload_and_audience_download` | original announcement upload and audience download |
| WorkspaceTests | `test_score_url_checks_original_submission_id` | score url checks original submission id |
| WorkspaceTests | `test_student_academic_fields_are_preserved` | student academic fields are preserved |
| WorkspaceTests | `test_plaintext_fields_no_longer_exist` | plaintext fields no longer exist |
| LegacyMigrationTests | `test_populated_original_0006_database_upgrades_without_losing_records` | populated original 0006 database upgrades without losing records |
