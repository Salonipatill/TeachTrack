# TeachTrack documentation

Updated 22 October 2026. The current source and documented behavior include profile
editing, quiz questions with 2–26 options and multiple correct answers, separate
academic autofill/snapshots, light/dark mode, Home/WORKSPACE navigation, Campus life
and its Google Maps location search, 30 MB document/image uploads, custom resource
categories, local storage without Google Cloud and Aiven TLS. Public password
reset and SMTP have been removed.

| Guide | Contents |
| --- | --- |
| [Recent changes](RECENT_CHANGES.md) | Current features, removed behavior, migrations 0010–0011 and verification limits |
| [Project handbook](PROJECT_DOCUMENTATION.md) | Architecture, setup, roles, workflows, security and operations |
| [Database setup](DATABASE_SETUP.md) | Local MySQL/Aiven environment switching, SSL modes and isolated test runner |
| [Vercel deployment](VERCEL_DEPLOYMENT.md) | Aiven configuration, commit identity, static assets and live acceptance |
| [Google Cloud deployment](DEPLOYMENT.md) | Optional container, PostgreSQL and private GCS infrastructure |
| [Configuration reference](CONFIGURATION_REFERENCE.md) | Current variables, defaults, storage modes and disabled email |
| [Database reference](DATABASE_REFERENCE.md) | All project models/fields, custom resource categories, batch and academic_details |
| [Form reference](FORM_REFERENCE.md) | Active forms, per-role profile fields and automatic quiz defaults |
| [Route reference](ROUTE_REFERENCE.md) | Current routes, authorization and own-account profile endpoint |
| [Design system](DESIGN_SYSTEM.md) | Shared components, responsive layouts and light/dark themes |
| [Colour index](COLOUR_INDEX.md) | Both active stylesheets, scoped tokens and exact colour usage |
| [Testing](TESTING.md) | Isolated procedure and verified versus unverified checks |
| [Test catalogue](TEST_CATALOGUE.md) | Current test methods derived from source |
| [Website review](WEBSITE_REVIEW.md) | Quality checklist and remaining operational checks |
| [Upgrade guide](UPGRADE.md) | Original schema/account migration and preservation procedure |
| [Change log](CHANGELOG.md) | Recent features and original upgrade history |
| [Campus content](CAMPUS_CONTENT.md) | Image/content sources and internal navigation/Google Maps behavior |
| [Tool guide](../tools/README.md) | Build, export and validation commands |

## Offline deliverables

[Open the illustrated HTML handbook](TEACHTRACK_DOCUMENTATION.html) or
[download/open its PDF](TEACHTRACK_DOCUMENTATION.pdf). The HTML includes diagrams,
internal navigation and searchable swatches without external libraries. The PDF
is exported from that rebuilt HTML and must be refreshed after later changes.

## Rebuild

From the TeachTrack folder:

```powershell
.\.venv\Scripts\python.exe tools/build_documentation.py
.\.venv\Scripts\python.exe tools/export_documentation_pdf.py
.\.venv\Scripts\python.exe tools/check_documentation.py
```

The builder uses an isolated in-memory database configuration, inspects metadata,
URLs and unsaved form variants, and does not read account rows or serialize secrets.
Generated references/JSON/diagrams and HTML are rebuilt; authored guides are edited
first. PDF export needs the optional local browser dependency in the tool guide.
The checker covers maintained local links and current account-feature references,
not external URL availability or live deployment health.

The original README and older historical upgrade notes are retained as records;
current feature status is in RECENT_CHANGES.md and the regenerated references.
