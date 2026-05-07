# Tasks: Fix Company Profile Admin

- [x] Add `terms_and_conditions_url` to `CompanyProfileAdmin` fieldsets <!-- id: 0 -->
    - **Files**: `dashboard/booking/admin.py`
    - **Step**: Add `"terms_and_conditions_url"` to the `"fields"` list under the `"General"` section in `CompanyProfileAdmin`.
    - **Validation**: Open the Django Admin, navigate to Company Profile, and verify the field is visible and editable.

- [x] Update `dashboard-models` specification <!-- id: 1 -->
    - **Files**: `openspec/specs/dashboard-models/spec.md`
    - **Step**: Add a "Terms and Conditions Configuration" requirement and a "Fetching company profile" scenario.
    - **Validation**: Verify that `openspec validate` (if applicable) or manual review confirms the new requirement is consistent with existing ones.
