# Suggested implementation review split

This follows your original work-allocation plan. It is an ownership and presentation guide, not a claim about who authored the generated implementation.

| Saloni review/demo | Zaman review/demo | Joint validation |
| --- | --- | --- |
| Director analytics and CSV exports | Resource model, upload, download and filters | Cross-role workflows |
| Secure authentication and password migration | Notification model, badges and panel | Deployment settings |
| Complaint model, workflow and status history | Role access decorators and object checks | Cloud SQL / private bucket |
| Feedback constraints and aggregation | Responsive CSS, navigation and dashboards | Static files and SMTP |
| Quiz participation and leaderboard | Resource totals and private media delivery | Regression tests and documentation |

Suggested presentation order: director creates faculty → faculty uploads resources and publishes quiz → student downloads, attempts quiz, asks doubt and raises complaint → faculty responds → director resolves complaint and exports analytics.
