# Upgrade an existing original TeachTrack database

## First distinguish the database you have

The uploaded source's settings used MySQL. The separate uploaded SQLite file is not a complete database for that source: it contains zero legacy student accounts and lacks the Faculty, Director, Quiz and other model tables expected by the original six migrations. Its initial migration record does not describe the shipped initial migration. Do not use `--fake` to force that file through the new migration chain.

For that specific empty bundled file, use a fresh database. Nothing in its academic/account tables needs to be transferred. The separate read-only student importer can preview its supported table if needed.

The process below is for a **consistent populated database matching the original source through migration 0006**. The automated suite tests this path with an isolated populated SQLite fixture. A real MySQL database upgrade must first be rehearsed on a backup copy of that database.

## Back up before upgrading

1. Stop writes to the original application.
2. Make a full database backup and copy the original `media/` directory.
3. Keep the old application version and its environment configuration privately, outside this new source tree.
4. Restore the database backup into a staging database. Never use production as the first migration test.

## Configure the staging copy

- SQLite: point DATABASE_URL at a copy of a consistent database, using `sqlite:///ABSOLUTE_PATH` with the appropriate extra slash for an absolute Linux path.
- Original MySQL: install `requirements-mysql.txt`, which includes the main requirements and MySQL Connector. Set DATABASE_URL to your staging MySQL URL. Do not paste its credentials into settings.py.
- PostgreSQL: use the normal requirements and a PostgreSQL URL. Django schema migrations do not copy data automatically from MySQL to PostgreSQL; first perform and validate a separate database-engine migration if that is your chosen path.

Use `DEBUG=True` for the local staging rehearsal. Production requires DEBUG=False, a strong secret, a supported production database and the private bucket settings described in DEPLOYMENT.md.

## Run the upgrade

```bash
python manage.py showmigrations ClassApp
python manage.py migrate --plan
python manage.py migrate
python manage.py account_migration_report
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test ClassApp
```

Before upgrade, the first six ClassApp migrations should accurately match your existing schema. If migration history and tables disagree, stop and repair the staging schema from a reviewed backup rather than marking migrations fake.

## What the new migrations do

| Migration | Result |
| --- | --- |
| 0007_secure_academic_modules | Adds secure user links, profiles, quiz metadata, resource/notification tables, complaint events and other module fields. Existing IDs and relationships remain. |
| 0008_migrate_secure_accounts | Converts legacy role accounts, hashes plaintext passwords, preserves recognized Django hashes, assigns roles, links unambiguous historical records, fills quiz codes/reviews, converts complaint statuses/history and clears old sessions/OTPs. |
| 0009_remove_plaintext_passwords | Drops the legacy pw columns and adds uniqueness/rating constraints. |

New quiz submissions still create the original SubmissionAnswer and SubmissionDetail records, including their selected Option relations. Question images, doubt attachments and announcement document paths are retained.

## Account names and conflicts

Legacy usernames are used when available and valid. Existing Django users are never silently merged with a different legacy record merely because a username matches. A conflicting or invalid name receives a unique name based on role/record ID. `account_migration_report` lists the mapping without passwords. Sign in using that resulting Django username and the previous password.

Existing AuthenticatedStudent/Teacher Django users keep their accounts and complaint relationships. Existing superusers receive director access, teachers receive faculty access and other existing Django users default to student. Missing passwords become unusable; set a new one through a trusted administrator.

The legacy role tables retain descriptive data and user links, but login reads Django User password hashes exclusively. Old Django/custom sessions are cleared, so everyone must sign in again. Public registration can only create students.

## Historical ambiguity and duplicates

Submissions are linked using an unambiguous enrollment number or student email. Doubts and ratings use an unambiguous legacy student email. Ambiguous or unmatched rows remain in the database for authorized staff review and are not assigned to an arbitrary student.

When repeated historical attempts or ratings map to the same student/quiz or student/faculty pair, only the newest record receives the authenticated user link. Earlier rows remain as unlinked historical records with their original names, email and answer relations. They are not deleted. New authenticated attempts/ratings obey uniqueness constraints. Historical rows can therefore still affect staff aggregate totals until reviewed.

Out-of-range historical numeric ratings are normalized to the nearest valid 1–5 endpoint before the new database constraint is applied. Review unusual old ratings in your staging backup before approving the upgrade.

Complaint Pending becomes pending; Replied becomes in_progress, since a reply alone does not establish resolution. Existing student/teacher links, complaint text, reply and timestamps are retained. A timeline event is created for the original concern and reply.

## Media and rollback

Local development uses the copied media directory with original relative paths. Production requires these files in the configured private Google Cloud Storage bucket under the same keys. There is no public `/media/` route; attachments are served by authenticated views.

The credential-conversion migration is intentionally irreversible. Once plaintext fields are removed, rolling back by unapplying migrations is not supported. To revert a failed rehearsal, restore the database backup and old code together. Keep backups private because pre-upgrade backups can contain plaintext passwords.

Rehearse all three role logins, old quiz scores, images, documents, doubts, feedback and complaints against the staging copy. Only after that review should the equivalent backed-up production database be upgraded.

## Current follow-up migration and storage modes

Migration 0010 adds Student.batch and Submission.academic_details. Apply it after
the original account/schema upgrade. Existing attempts keep their saved combined
summary; no separate historical values are inferred. New submissions retain all
separate academic fields in JSON. Profile edits synchronize linked current role
records while preserving already-recorded submission snapshots.

A private bucket is optional for production startup, but existing files must be
preserved separately. Production without persistent storage deliberately disables
uploads and cannot restore missing historical media. See VERCEL_DEPLOYMENT.md for
the current Aiven/TLS setup. Public password reset and SMTP are removed.
