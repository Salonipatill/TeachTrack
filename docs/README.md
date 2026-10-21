# TeachTrack documentation

Start with the [complete project handbook](PROJECT_DOCUMENTATION.md). For a single navigable document with diagrams, tables and searchable colour swatches, open [TEACHTRACK_DOCUMENTATION.html](TEACHTRACK_DOCUMENTATION.html) in a browser. A printable PDF snapshot is supplied alongside it as TEACHTRACK_DOCUMENTATION.pdf.

Reviewed source snapshot: 21 October 2026. Covers the current Student, Faculty and Director application, shared public website, Campus Life page and seven-image homepage carousel.

## Read by purpose

| Need | Document |
| --- | --- |
| Understand the whole project | [Project handbook](PROJECT_DOCUMENTATION.md) |
| Install/run it and manage accounts | Handbook sections 4, 5 and 14 |
| Follow academic workflows | Handbook sections 6 and 7 |
| Understand architecture/files | Handbook sections 2 and 3 |
| Find every database field and relation | [Database reference](DATABASE_REFERENCE.md) |
| Find form fields and validation | [Forms reference](FORM_REFERENCE.md) |
| Find routes, roles, methods and query parameters | [Route reference](ROUTE_REFERENCE.md) |
| Understand environment/settings | [Configuration reference](CONFIGURATION_REFERENCE.md) |
| Find colours, typography, spacing and components | [Design system](DESIGN_SYSTEM.md) |
| Find every explicit active-stylesheet colour | [Complete colour index](COLOUR_INDEX.md) and [machine-readable palette](colour-index.json) |
| Inspect individual test coverage | [Test catalogue](TEST_CATALOGUE.md) |
| Run acceptance/verification | [Testing guide](TESTING.md) |
| Upgrade populated original data | [Upgrade guide](UPGRADE.md) |
| Prepare Google Cloud infrastructure/deployment | [Deployment guide](DEPLOYMENT.md) |
| Trace campus facts/image links | [Campus content sources](CAMPUS_CONTENT.md) |
| Review project history or contribution notes | [Changelog](CHANGELOG.md), [contributions](CONTRIBUTIONS.md), [original README](ORIGINAL_README.md) |

## Documentation formats

The handbook and references are ordinary Markdown files suitable for an IDE, repository viewer or future editing. The generated HTML contains all handbook/reference text, embedded vector diagrams, chapter navigation and a visual catalogue of the active palette. It works offline without a CDN, web font or JavaScript library. Its colour filter and Print / save as PDF button are optional browser conveniences.

The PDF is a fixed snapshot for sharing/printing. Source links and companion operational guides remain available in the project. Photographs are documented by filename, dimensions and purpose; database credentials, .env contents, password hashes and live user records are excluded.

## Rebuild the references

From the project root:

```powershell
.\.venv\Scripts\python.exe tools/build_documentation.py
```

The builder reads Django model metadata and source definitions without querying user data. It regenerates DATABASE_REFERENCE.md, FORM_REFERENCE.md, ROUTE_REFERENCE.md, COLOUR_INDEX.md, colour-index.json, TEST_CATALOGUE.md, three SVG diagrams and the combined HTML handbook. It uses the standard library and the project’s existing Django environment; there is no additional Python document dependency.

PROJECT_DOCUMENTATION.md, DESIGN_SYSTEM.md and CONFIGURATION_REFERENCE.md are authored explanations. Edit them when behavior changes, then rebuild. The generated PDF must be exported again after the HTML changes; it is not silently refreshed by the Python builder.

## Completeness and limits

This documentation covers the code and configured behavior in the workspace: all 24 project models, all active form variants, all declared application/account routes and all explicit colours in the active stylesheet. It describes retained legacy files separately from the templates currently rendered.

It does not claim an independent security/accessibility audit, verified live cloud deployment, exhaustive documentation of Django’s internal framework code or every pixel colour inside photography. Operational guides contain replaceable infrastructure placeholders. The runtime database and files still need the target environment’s normal backups and acceptance checks.
