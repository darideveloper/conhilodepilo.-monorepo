# Tasks: Refactor Stagehand Architecture

- [x] Create `stagehand/src/config/stagehand.ts` and move the LLM and Stagehand initialization logic out of existing scripts.
- [x] Create `stagehand/src/utils/` directory to serve as a home for reusable functions.
- [x] Move `stagehand/tests/landing-integration.test.ts` to `stagehand/src/automations/landing-integration.test.ts`.
- [x] Refactor `landing-integration.test.ts` to use Node.js `test` and `describe` blocks.
- [x] Update `landing-integration.test.ts` to import `createStagehand` from `src/config/stagehand.ts`.
- [x] Implement `after()` teardown hook in the automation to guarantee `stagehand.close()` execution.
- [x] Update `stagehand/package.json` to include a single `"automate": "tsx --test src/automations/**/*.test.ts"` script.
- [x] Verify refactor by running the unified command (`npm run automate`).
- [x] Clean up redundant code from `stagehand/index.ts` (convert to an example or remove).
