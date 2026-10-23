# INVEST v5 redesign notes

## Implemented in this package
- Replaced the homepage template with a new dark editorial hero, animated orbital graphic, floating glass information panels, responsive statistics, category discovery, featured products, and a clear founder/investor CTA.
- Added mobile breakpoints and reduced-motion accessibility.
- Added a working chat theme selector (Classic, Ocean, Forest, Sunset, Midnight).
- Added file selection UI, a location-link helper using browser permission, and contact-card text helper in chat.
- Public startup discovery remains browseable without login; server-side actions continue to require an investor account.

## Important limitations
- File picker currently selects files locally but does not upload/send them; upload storage, validation, download authorization, and database metadata need backend implementation.
- Gallery and actual contact-vCard sharing are not implemented.
- Confirm all pages on your hosting provider after deployment; this archive cannot change an already deployed website until you replace the deployed source and redeploy.
