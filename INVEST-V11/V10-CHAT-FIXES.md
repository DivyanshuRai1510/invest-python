# V10 targeted chat fixes

This version addresses the exact failure visible in the supplied screenshot.

- Existing message bodies are parsed and rendered server-side, not only by client-side JavaScript.
- Repeated identical location/contact lines in legacy messages are collapsed for display.
- Google Maps shares render as clickable location cards; contact shares render as contact cards.
- Initial and polled image attachments use the inline image URL for previews; the download link remains a download.
- The chat script URL has a version query (`v=10`) to reduce stale browser-cache issues.

## Checks run in the build environment
- Python source compilation: passed (18 files).
- Jinja template parsing: passed (21 HTML templates, with the app's `crore` and `inr` filters stubbed for parsing).
- JavaScript syntax (`node --check`): passed for chat.js, swipe.js, and swipe-enhanced.js.
- ZIP integrity: checked after packaging.

## Not claimed as verified
Flask isn't installed in the build environment, so live application startup, database migration behavior, and browser end-to-end behavior were not tested here. Run the app locally before treating the feature as production-ready.
