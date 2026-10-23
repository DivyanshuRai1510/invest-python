# INVEST Professional UI/UX Update — v3

## What changed
- Demo investor and founder profiles now use real photographic portraits from RandomUser (not generated avatars). Demo records using old Picsum avatar placeholders are refreshed on app startup. Users can upload their own headshots from Profile.
- Founder dashboard includes dedicated Order Management and Payments ledger panels, alongside product enquiries and investor interest.
- Added a Support Centre: users can submit tickets by category and see their ticket ID, date, details and status on the dashboard.
- Improved button focus states, form focus rings, dashboard spacing, table responsiveness and consistent rounded controls.
- Removed emoji controls from the startup swipe screen.

## Important operational note
The project does not currently include checkout, an order-creation workflow, a payment gateway, or an admin support-agent console. Order and Payment records are included as database-backed tracking structures, and the founder dashboard displays records when they are created. The payment panel is explicitly an informational ledger; it does not collect or move money. Support tickets are saved and visible to the submitting account, but a staff workflow to reply/resolve tickets would be a separate feature.

## Existing deployment
The new database tables are created by the app's existing `db.create_all()` startup process. Existing demo profile portraits using Picsum URLs are updated automatically. No manual database reset is required, and user-uploaded/local photos are not overwritten.

## Run locally
1. Extract the ZIP.
2. Open a terminal in `invest-python`.
3. Create/activate a virtual environment.
4. Install dependencies with `pip install -r requirements.txt`.
5. Run `python app.py` and open `http://127.0.0.1:5000`.

The sample demo credentials listed in README are for local/demo testing only; change credentials and configuration before production use.
