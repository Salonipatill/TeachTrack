# Testing and verification

Run `python manage.py test ClassApp` from the project folder. Tests use a separate temporary database and in-memory media storage. They do not edit the original supplied database.

The current source defines **53 test methods**, listed individually in [TEST_CATALOGUE.md](TEST_CATALOGUE.md). Use the same virtual-environment interpreter for Django and its test subprocesses. For a workspace with an existing MySQL database, prefer the isolated SQLite procedure in [handbook section 15](PROJECT_DOCUMENTATION.md#15-testing-and-acceptance); it preserves the shell's previous configuration after the run.

## Automated coverage

The suite covers:

- All role dashboards and module pages; anonymous redirects; denial of staff actions to students; correct protection on original role URLs.
- Registration password hashing, prevention of role injection, retained student academic fields and director account bootstrap.
- Login throttling/cooldown, CSRF, POST-only logout, password changes and removed reset routes, account deactivation and revocation of existing sessions.
- Resource upload/search/filters, file content/size validation, authenticated downloads, counting, unavailable files and no public media route.
- Notification privacy, mark-read actions, unsafe redirect rejection and audience restrictions.
- Original announcement document upload, author/faculty links and authorized document download.
- Quiz creation/minimum questions, opening/closing/publication controls, required student details, strict option membership and single/multi-select scoring.
- One authenticated attempt, preserved original answer/detail tables, student/faculty ownership, delayed solutions, invalid legacy quiz rejection and original score URL access.
- Complaints, assignment, role-controlled status/history, doubts and assigned replies, private legacy attachments.
- Feedback updates and database rating constraints; alphabetical CSV exports and formula-text protection.
- Legacy student importer dry-run, password hashing, source preservation and conflict handling.
- No plaintext pw fields in current role models.

## Populated original-schema migration test

An isolated database is first migrated to the original 0006 schema and populated with legacy students, faculty, directors, existing Django/complaint accounts, a username conflict, quiz questions/images/options, repeated submissions with answer/detail M2M relations, repeated ratings, a doubt attachment, an announcement document and a replied complaint.

It then applies 0007–0009 and verifies:

- All original record IDs and relationships remain.
- Legacy plaintext passwords are converted; recognized hashes remain usable; old Django users are not silently taken over by a conflicting legacy username.
- Profiles and role login work.
- Question images, answer selections, submission details and attachment paths remain intact.
- Ambiguous/repeated historical records remain stored; one newest record receives each unique authenticated link.
- Complaint text, teacher reply, status and timeline are retained.
- Old sessions and OTPs are cleared; legacy plaintext password columns no longer exist.

This validates the Django migration path on SQLite. It does not claim validation against an inaccessible external MySQL server.

## Browser checks

Chromium checks all three role dashboards at desktop (1440 px) and mobile (390 px), role module navigation, mobile sidebar behavior, resource download, student quiz submission and the dynamic question-builder button. Rendered pages were inspected for overflow and JavaScript errors.

Recent public-page checks used the running local HTTP server in a hidden Chrome preview. The homepage has seven carousel slides/dots; both newly added photos load, arrows wrap between first/last, keyboard and touch controls work, and the removed star/tagline block is absent. The Campus Life header/footer links open a dedicated page, its selected main image is displayed in full, and all 13 current image elements have valid local asset responses. Narrow layouts were checked at 320 and 390 px, with tablet/desktop checks during the public-page changes. These local observations do not replace browser acceptance in a live deployment.

## Fresh package checks to repeat for a release

Extract the release into a new directory, create its environment without overwriting an existing configuration, then check migrations, system/migration drift, demo seeding, static collection and all three demo-role logins against a new isolated database. A production `check --deploy --fail-level WARNING` using synthetic values checks configuration only; it does not establish cloud connectivity. Record the commands, release source, interpreter, database engine and result for each release instead of treating a previous package check as current evidence.

## Documentation checks

Run `.venv\Scripts\python.exe tools/build_documentation.py` to rebuild source-derived model, form, route, colour and test references and the offline HTML handbook. Check local document links, handbook anchors, diagram rendering and the visual colour filter. The generator reads metadata/source without querying live user data. It does not execute the application test suite or automatically refresh the PDF snapshot.

The most recent application-suite execution recorded during the current workspace changes passed all 53 tests. Documentation-only changes should be checked through document generation and reference/link validation; they do not require claiming a fresh application-test execution. Windows compatibility handling includes closing temporary SQLite source handles and launching migration subprocesses with the test environment's Python interpreter.

## Manual acceptance and live production checks

1. Create a director, faculty and student; test original login/dashboard links and the new home page.
2. Upload resource categories, test search/filters and download counts.
3. Publish a quiz with a single-choice question, multi-select question and image. Test required student details, exact-set grading, duplicate prevention and the answer-review closing time.
4. Upload an announcement document and a doubt attachment. Confirm that another student's private doubt cannot be opened.
5. Submit/update feedback, reply to doubts and walk a complaint through all three statuses.
6. Review director charts, resource totals, historical records and all four CSV reports.
7. Review the migrated account-name report and any unlinked historical records against your backup.
8. Rehearse the real MySQL database upgrade separately if using that database. Test media path preservation and backups.
9. In Google Cloud, verify Cloud SQL connectivity, private bucket reads/writes, HTTPS cookies, CSRF origins, static assets and the health endpoint.
10. Set ingress body/file-size enforcement, including streamed requests without Content-Length, and load-test your intended student count. Review login throttling behind the actual proxy because peer-IP limits can group several users.

Expected Forbidden/Not Found log entries occur during access-denial tests and are not test failures.
