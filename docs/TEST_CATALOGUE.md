# Test catalogue

71 test methods are defined in `ClassApp/test*.py`. This catalogue describes source coverage; a successful test execution must be recorded separately.

| Source | Test class | Method | Scenario |
| --- | --- | --- | --- |
| test_database_config.py | DatabaseConfigurationTests | `test_default_preserves_aiven_certificate_and_hostname_verification` | default preserves aiven certificate and hostname verification |
| test_database_config.py | DatabaseConfigurationTests | `test_local_mysql_disables_ssl_without_loading_any_certificate` | local mysql disables ssl without loading any certificate |
| test_database_config.py | DatabaseConfigurationTests | `test_connector_url_uses_the_same_environment_configuration` | connector url uses the same environment configuration |
| test_database_config.py | DatabaseConfigurationTests | `test_custom_ca_relative_and_absolute_paths` | custom ca relative and absolute paths |
| test_database_config.py | DatabaseConfigurationTests | `test_client_certificate_and_key_are_paired` | client certificate and key are paired |
| test_database_config.py | DatabaseConfigurationTests | `test_invalid_ssl_modes_and_missing_ca_fail_clearly` | invalid ssl modes and missing ca fail clearly |
| test_database_config.py | DatabaseConfigurationTests | `test_connection_lifetime_timeout_and_driver_are_configurable` | connection lifetime timeout and driver are configurable |
| test_database_config.py | DatabaseConfigurationTests | `test_invalid_numeric_and_boolean_options_fail_clearly` | invalid numeric and boolean options fail clearly |
| test_database_config.py | DatabaseConfigurationTests | `test_environment_ssl_replaces_uri_ssl_options` | environment ssl replaces uri ssl options |
| test_database_config.py | DatabaseConfigurationTests | `test_sqlite_and_postgresql_ignore_mysql_settings` | sqlite and postgresql ignore mysql settings |
| test_database_config.py | DatabaseConfigurationTests | `test_blank_url_keeps_sqlite_fallback` | blank url keeps sqlite fallback |
| test_database_config.py | DatabaseConfigurationTests | `test_invalid_url_error_does_not_echo_credentials` | invalid url error does not echo credentials |
| test_database_config.py | DatabaseConfigurationTests | `test_selected_private_environment_file_is_used_by_settings` | selected private environment file is used by settings |
| test_database_config.py | DatabaseConfigurationTests | `test_runserver_loads_the_selected_file_over_inherited_values` | runserver loads the selected file over inherited values |
| tests.py | WorkspaceTests | `test_all_role_pages_render` | all role pages render |
| tests.py | WorkspaceTests | `test_guests_require_login` | guests require login |
| tests.py | WorkspaceTests | `test_student_cannot_access_staff_actions` | student cannot access staff actions |
| tests.py | WorkspaceTests | `test_registration_hashes_password_and_ignores_role_injection` | registration hashes password and ignores role injection |
| tests.py | WorkspaceTests | `test_login_throttle` | login throttle |
| tests.py | WorkspaceTests | `test_role_login_pages_and_matching_accounts` | role login pages and matching accounts |
| tests.py | WorkspaceTests | `test_role_login_mismatch_explains_where_to_sign_in` | role login mismatch explains where to sign in |
| tests.py | WorkspaceTests | `test_csrf_and_logout_method` | csrf and logout method |
| tests.py | WorkspaceTests | `test_email_password_reset_is_removed` | email password reset is removed |
| tests.py | WorkspaceTests | `test_resource_upload_search_and_notification` | resource upload search and notification |
| tests.py | WorkspaceTests | `test_reject_fake_pdf_and_html` | reject fake pdf and html |
| tests.py | WorkspaceTests | `test_oversized_and_binary_txt_rejected` | oversized and binary txt rejected |
| tests.py | WorkspaceTests | `test_download_authenticated_and_counted` | download authenticated and counted |
| tests.py | WorkspaceTests | `test_missing_resource_does_not_increment` | missing resource does not increment |
| tests.py | WorkspaceTests | `test_notifications_are_private_and_mutations_post_only` | notifications are private and mutations post only |
| tests.py | WorkspaceTests | `test_notification_open_redirect_blocked` | notification open redirect blocked |
| tests.py | WorkspaceTests | `test_announcement_audience` | announcement audience |
| tests.py | WorkspaceTests | `test_create_quiz_formset` | create quiz formset |
| tests.py | WorkspaceTests | `test_quiz_rejects_empty_questions` | quiz rejects empty questions |
| tests.py | WorkspaceTests | `test_quiz_scoring_and_duplicate_submission` | quiz scoring and duplicate submission |
| tests.py | WorkspaceTests | `test_answers_withheld_until_close` | answers withheld until close |
| tests.py | WorkspaceTests | `test_incomplete_quiz_is_not_submitted` | incomplete quiz is not submitted |
| tests.py | WorkspaceTests | `test_closed_upcoming_and_unpublished_quizzes` | closed upcoming and unpublished quizzes |
| tests.py | WorkspaceTests | `test_other_faculty_cannot_manage_quiz` | other faculty cannot manage quiz |
| tests.py | WorkspaceTests | `test_students_only_see_their_submission_details` | students only see their submission details |
| tests.py | WorkspaceTests | `test_complaint_creation_and_status_history` | complaint creation and status history |
| tests.py | WorkspaceTests | `test_complaint_object_access` | complaint object access |
| tests.py | WorkspaceTests | `test_feedback_upsert_and_range` | feedback upsert and range |
| tests.py | WorkspaceTests | `test_feedback_db_constraint` | feedback db constraint |
| tests.py | WorkspaceTests | `test_doubt_answer_permission_and_notification` | doubt answer permission and notification |
| tests.py | WorkspaceTests | `test_account_creation_and_deactivation` | account creation and deactivation |
| tests.py | WorkspaceTests | `test_profile_edit_for_all_roles` | profile edit for all roles |
| tests.py | WorkspaceTests | `test_profile_edit_rejects_duplicate_email_and_username` | profile edit rejects duplicate email and username |
| tests.py | WorkspaceTests | `test_profile_edit_requires_login_and_csrf` | profile edit requires login and csrf |
| tests.py | WorkspaceTests | `test_staff_creation_forms_exclude_student_details` | staff creation forms exclude student details |
| tests.py | WorkspaceTests | `test_staff_registration_fixes_role_and_saves_contact_details` | staff registration fixes role and saves contact details |
| tests.py | WorkspaceTests | `test_director_created_student_requires_and_saves_academic_details` | director created student requires and saves academic details |
| tests.py | WorkspaceTests | `test_director_cannot_deactivate_self` | director cannot deactivate self |
| tests.py | WorkspaceTests | `test_report_export_alphabetical_and_csv_safe` | report export alphabetical and csv safe |
| tests.py | WorkspaceTests | `test_dashboard_no_removed_performance_sections` | dashboard no removed performance sections |
| tests.py | WorkspaceTests | `test_legacy_import_dry_run_and_hashing` | legacy import dry run and hashing |
| tests.py | WorkspaceTests | `test_director_bootstrap_command` | director bootstrap command |
| tests.py | WorkspaceTests | `test_password_change_invalidates_old_password` | password change invalidates old password |
| tests.py | WorkspaceTests | `test_deactivation_revokes_existing_session` | deactivation revokes existing session |
| tests.py | WorkspaceTests | `test_original_role_urls_enforce_correct_role` | original role urls enforce correct role |
| tests.py | WorkspaceTests | `test_original_quiz_answer_and_detail_tables_are_written` | original quiz answer and detail tables are written |
| tests.py | WorkspaceTests | `test_multi_select_requires_exact_correct_set` | multi select requires exact correct set |
| tests.py | WorkspaceTests | `test_forged_options_from_other_question_rejected` | forged options from other question rejected |
| tests.py | WorkspaceTests | `test_required_original_quiz_details_are_validated` | required original quiz details are validated |
| tests.py | WorkspaceTests | `test_quiz_attempt_autofills_separate_academic_details_and_dates` | quiz attempt autofills separate academic details and dates |
| tests.py | WorkspaceTests | `test_invalid_legacy_quiz_cannot_be_attempted_or_published` | invalid legacy quiz cannot be attempted or published |
| tests.py | WorkspaceTests | `test_private_original_doubt_attachment` | private original doubt attachment |
| tests.py | WorkspaceTests | `test_original_announcement_upload_and_audience_download` | original announcement upload and audience download |
| tests.py | WorkspaceTests | `test_score_url_checks_original_submission_id` | score url checks original submission id |
| tests.py | WorkspaceTests | `test_student_academic_fields_are_preserved` | student academic fields are preserved |
| tests.py | WorkspaceTests | `test_plaintext_fields_no_longer_exist` | plaintext fields no longer exist |
| tests.py | LegacyMigrationTests | `test_populated_original_0006_database_upgrades_without_losing_records` | populated original 0006 database upgrades without losing records |
