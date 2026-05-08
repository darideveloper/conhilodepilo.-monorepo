# Design: Stagehand Landing Data Validation

## Architecture
The test suite will use **Stagehand**, an AI-powered browser automation tool. It will interact with the Landing Page as a real user would, but with the ability to "understand" the page structure through LLMs.

### Test Components
1.  **Stagehand Client:** Configured in `stagehand/index.ts` (or a dedicated test file).
2.  **Validation Logic:**
    *   **Extraction:** Use `page.extract()` with Zod schemas to get clean JSON from the UI.
    *   **Assertions:** Compare the extracted JSON against known Dashboard data.
3.  **Environment Sync:**
    *   The test must share the same `PUBLIC_API_URL` as the landing page.
    *   `PUBLIC_COURSES_GROUP_ID` must be known by the test to verify correct filtering.

## Verification Workflow

### 1. Service Category Validation
*   **Target:** `#servicios` section.
*   **Extraction Schema:** 
    ```typescript
    Array<{ 
      categoryName: string, 
      imageSrc: string, 
      services: Array<{ title: string, price: string, duration: string }> 
    }>
    ```
*   **Success Criteria:** 
    *   List length > 0.
    *   Names and nested services match the Dashboard `EventType` and `Event` data.
    *   `imageSrc` is an absolute URL pointing to the Dashboard.

### 2. Course Section Validation
*   **Target:** `#cursos` section.
*   **Extraction Schema:** `Array<{ title: string, price: string, duration: string, bookingUrl: string }>`
*   **Success Criteria:** 
    *   Only events from the designated course group are present.
    *   `bookingUrl` follows the pattern `/booking/:id`.

### 3. Media Reachability
*   **Target:** All `<img>` tags within the main sections.
*   **Logic:** For each unique `src` starting with the dashboard URL, ensure the image is rendered with non-zero dimensions.

### 4. Interactive Validation
*   **Action:** Click on different service buttons within a `CategoryCard`.
*   **Validation:** Verify that the "Price" and "Duration" display updates to match the selected service.

## Implementation Details
The test will be added to the existing `stagehand/` project. 
It will likely use the `gpt-4o` model (via OpenRouter) for extraction to ensure high accuracy in identifying UI elements.
