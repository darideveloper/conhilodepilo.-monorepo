# Proposal: Fix Company Profile Admin

## Why
The `CompanyProfile` model includes a field for the Terms and Conditions URL (`terms_and_conditions_url`), but this field is not exposed in the Django admin interface. Consequently, administrators cannot configure this URL through the dashboard, even though the frontend application expects and attempts to use it.

## What Changes
1.  **Modify `CompanyProfileAdmin`**: Update the `fieldsets` in `dashboard/booking/admin.py` to include the `terms_and_conditions_url` field within the "General" section, adjacent to the `privacy_policy_url`.
2.  **Update Specification**: Add a new requirement to `openspec/specs/dashboard-models/spec.md` for the Terms and Conditions configuration to match the existing Privacy Policy requirement.

## Impact
- **Admin Dashboard**: A new "Terms and conditions URL" field will appear in the Company Profile admin page.
- **Frontend**: Administrators will be able to provide a URL that the frontend booking form will use for legal links.
- **Stripe Integration**: While not currently sent to Stripe, having this field correctly managed in the admin is the first step toward potential future integration (e.g., via Stripe's `consent_collection`).
