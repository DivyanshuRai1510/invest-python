# INVEST V6 UI update

This build starts from the supplied V5 project and updates the chat and investor profile templates, plus swipe card styling.

## Included
- Redesigned responsive chat layout with animated message rows and six visual themes (Classic, Ocean, Forest, Sunset, Lavender, Midnight); theme choice is remembered in the browser.
- Chat toolbar controls for selecting files/images, location sharing via browser permission, and inserting a contact label.
- Added a direct Discover / Swipe link from the chat page.
- Replaced the investor profile's generic “Startups in these sectors” block with founder-oriented investment-fit guidance and investor background details.
- Improved swipe card depth, control styling and small-screen layout.
- Requirements include python-dotenv for `config.py`.

## Important current limitations
- File/image selection currently shows local attachment previews only. This V6 does not upload or persist attachment bytes to the server, and previews are not delivered to the recipient. A secure upload endpoint, file-size/type validation, storage and attachment records are required to make that production-ready.
- Location sharing inserts a Google Maps link into the message field after the user grants browser location permission; the user still needs to send the message.
- Contact sharing inserts a contact label only; it does not access the user's address book.
- Existing routes, database schema and authentication behavior are retained. Review/test with sample data before deploying.
