# INVEST V9 QA checklist

## Static checks completed in the build workspace
- Python files compile with `compileall`.
- Jinja templates parse with the project's custom `crore` and `inr` filters registered.
- `chat.js`, `swipe.js`, and `swipe-enhanced.js` pass Node.js syntax checks.
- ZIP archive integrity is checked after packaging.
- Chat UI now formats location/contact shares as rich cards and de-duplicates repeated identical lines at render time.
- Location sharing avoids appending an identical location line repeatedly.
- Contact sharing now shares the signed-in user's contact details, not the recipient's.
- Polling response includes attachment metadata, so newly received files/images can render without refreshing.
- Image-preview failures degrade to a designed fallback instead of a giant broken-image icon.
- Company logo slots use initials for missing/stock placeholder logos; editorial industry imagery is used in the company cover, not as a logo.
- Upload total is checked using stream size, with request overhead allowance and an 8 MiB attachment budget.
- Removed duplicate Enter-to-send listeners to avoid accidental double-submit.

## Not yet verified (do not mark 10/10)
- Full Flask app startup and database-backed integration tests could not be run in the build environment because Flask dependencies are not installed and package installation has no network access.
- No live browser/mobile end-to-end test has been performed here.
- Remote Unsplash cover images require network access; gradient/animated cover styling remains as fallback.
- Location/contact sharing is message-based, not a full native map picker or address-book integration.

This is an honest static QA report, not a claim of full production readiness.
