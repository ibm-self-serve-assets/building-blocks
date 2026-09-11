# Verification

- `npm run check`: 37 tests covering ACP/REST contracts, parsing, ownership, persistence/recovery, cancellation/process cleanup, thread lifecycle, Markdown sanitization, workspace downloads and usage statistics.
- Real Bob Shell 2.0.1 smoke checks covered file creation, continued sessions and cancellation.
- OpenShift deployment verified persistent history, authenticated file downloads and real Bob usage in run/message responses.
- UI DOM checks covered Markdown, file links, cancellation states and usage rendering. Browser visual testing was not performed.

Run fixture tests without a Bob API key using `npm ci && npm run check`. `npm run smoke` requires licensed Bob Shell setup and valid credentials, and consumes Bob credit.

ACP discoverability coverage verifies the public guide and contract, capability links, root-level routes, bearer authentication, and omission of unsupported Await/resume.

Python examples were exercised against a temporary service using the Bob fixture: ACP sync/async/stream, session continuation, REST thread continuation, reported usage, event streaming, file download, both cancellation routes and authentication failure passed. Python syntax compilation passed. No third-party Python packages are required.
