# Proposal: Integrate OpenRouter into Stagehand

## Summary
Enable Stagehand to use OpenRouter as an LLM provider. This allows the use of diverse models like DeepSeek V3, Claude, and others through an OpenAI-compatible API, providing more flexibility and cost optimization. This integration includes a temporary patch for `AISdkClient` to support `agent()` functionality.

## Motivation
OpenRouter provides access to multiple high-quality models at competitive prices and often supports advanced features like prompt caching. Integrating it with Stagehand leverages the Vercel AI SDK compatibility to broaden model selection.

## Scope
- Update `stagehand/package.json` to include `@openrouter/ai-sdk-provider` and `dotenv`.
- Update `stagehand/.env.example` and `stagehand/.env` with `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_REFERER`, and `OPENROUTER_TITLE`.
- Modify `stagehand/index.ts` to implement `PatchAISdkClient` to fix missing `getLanguageModel` in Stagehand v3.
- Modify `stagehand/index.ts` to use `createOpenRouter` and `PatchAISdkClient` for initialization.
- Document configuration requirements for OpenRouter models (JSON mode, context window).
