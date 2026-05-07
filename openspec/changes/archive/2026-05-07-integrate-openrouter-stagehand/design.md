# Design: OpenRouter Integration for Stagehand

## Architecture
Stagehand uses the Vercel AI SDK under the hood. The most robust integration involves using the `@openrouter/ai-sdk-provider` and wrapping the resulting model in Stagehand's `AISdkClient`.

### AISdkClient Patch
Currently, Stagehand v3's public `AISdkClient` is missing the `getLanguageModel` method, which is required for the `agent()` functionality to work correctly. A `PatchAISdkClient` class must be implemented to expose this method.

## Components
- **Provider Initialization:** Use `createOpenRouter` from `@openrouter/ai-sdk-provider`.
- **Client Wrapper:** Use `PatchAISdkClient` (extending `AISdkClient`) to ensure compatibility with Stagehand's internal handlers and `agent()` functionality.
- **Environment Variables:**
  - `OPENROUTER_API_KEY`: Authentication for OpenRouter.
  - `OPENROUTER_MODEL`: The default model to use (e.g., `google/gemini-2.0-flash-lite:free`).
  - `OPENROUTER_REFERER`: (Optional) `HTTP-Referer` for OpenRouter analytics.
  - `OPENROUTER_TITLE`: (Optional) `X-OpenRouter-Title` for OpenRouter analytics.
- **Headers:** Include optional `HTTP-Referer` and `X-OpenRouter-Title` for OpenRouter analytics.
- **Model Selection:** Use the full OpenRouter model string (e.g., `anthropic/claude-3.5-sonnet`).

## Trade-offs
- **Model Compatibility:** Not all OpenRouter models support structured output (JSON mode), which is critical for Stagehand. Users must select compatible models.
- **Context Window:** Many web pages are token-heavy; models with small context windows might fail.
- **Maintenance:** The `PatchAISdkClient` workaround should be monitored and removed once Stagehand officially exposes `getLanguageModel`.
