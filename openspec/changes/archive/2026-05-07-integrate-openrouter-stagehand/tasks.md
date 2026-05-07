# Tasks: Integrate OpenRouter into Stagehand

- [x] Add `@openrouter/ai-sdk-provider` and `dotenv` to `stagehand/package.json` dependencies. <!-- id: 1 -->
- [x] Update `stagehand/.env.example` to include `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_REFERER` (optional), and `OPENROUTER_TITLE` (optional). <!-- id: 2 -->
- [x] Add `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_REFERER`, and `OPENROUTER_TITLE` to `stagehand/.env`. <!-- id: 3 -->
- [x] Implement `PatchAISdkClient` in `stagehand/index.ts` to expose `getLanguageModel`. <!-- id: 7 -->
- [x] Implement `createOpenRouter` and `PatchAISdkClient` initialization in `stagehand/index.ts`. <!-- id: 4 -->
- [x] Configure `Stagehand` instance to use the `PatchAISdkClient` with an OpenRouter model. <!-- id: 5 -->
- [x] Verify the integration with a basic script run including `agent()` functionality. <!-- id: 6 -->
