# Design: Fix Company Profile Admin

## Overview
The goal is to ensure the `terms_and_conditions_url` field is manageable via the Django Admin. This field already exists in the `CompanyProfile` model but was omitted from the `ModelAdmin` fieldsets.

## Architectural Decisions

### Admin Configuration
We will modify the `CompanyProfileAdmin` class in `dashboard/booking/admin.py`. The field will be added to the "General" fieldset. This ensures consistency with the `privacy_policy_url` which is already present there.

### Requirement Alignment
The `dashboard-models` specification currently only mentions the Privacy Policy. We will add a corresponding requirement for Terms and Conditions to maintain documentation accuracy and parity between these two legal URLs.

## Alternatives Considered

### Automatic Discovery
Django can automatically discover fields if `fieldsets` are not defined, but `CompanyProfileAdmin` uses an explicit `fieldsets` definition for better organization (using the `Unfold` admin theme). Therefore, manual addition is required.

### Stripe Integration
We considered sending this URL to Stripe's Checkout Session under `consent_collection`. However, to keep this change tightly scoped to the user's request ("render in the admin"), we will focus on the Admin UI first. Future tasks can address Stripe integration if requested.
