# Proposal: Add Stagehand Landing Data Validation

## Problem
Currently, the integration between the Django Dashboard (source of truth) and the Astro Landing Page is validated manually. There is no automated process to ensure that:
1. Services created in the dashboard appear correctly on the landing page.
2. Courses are correctly filtered by their Group ID.
3. Images from the dashboard's media storage are correctly resolved and rendered.
4. Company profile changes (phone, email) propagate to the landing page.

## Proposed Solution
Implement a Stagehand-based E2E test suite in the `stagehand/` directory. This suite will:
- Navigate to the Landing Page.
- Extract structured data from "Servicios" and "Cursos" sections.
- Verify that the data matches the expected state from a running local Dashboard instance.
- Check image reachability and protocol consistency.

## Impact
- **Landing:** Improved reliability of dynamic content rendering.
- **Dashboard:** Regression testing for API contract changes affecting the landing page.
- **Developer Experience:** Automated verification of the full "Dashboard-to-Landing" data pipeline.

## Dependencies
- Running Dashboard instance (API).
- Running Landing instance (Astro dev or build).
- Stagehand environment configured (OpenRouter/OpenAI API keys).
