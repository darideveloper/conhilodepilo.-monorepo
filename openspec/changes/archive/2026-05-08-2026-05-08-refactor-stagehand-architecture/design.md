# Design: Stagehand Architecture Refactor

## Directory Structure
The `stagehand/` directory will be restructured to separate configuration, utilities, and executable automations:

```text
stagehand/
├── src/
│   ├── config/
│   │   ├── env.ts          # Zod schema for environment variable validation
│   │   └── stagehand.ts    # Shared createStagehand() factory
│   ├── utils/              # General/reusable functions (e.g., auth, DOM helpers)
│   └── automations/        # The actual scripts/tests (formerly tests/)
```

## Centralized Configuration
`PatchAISdkClient` and OpenRouter LLM setup will be centralized in `src/config/stagehand.ts`. The exported function `createStagehand()` will read from environment variables explicitly validated to fail-fast if critical tokens (`OPENROUTER_API_KEY`) are missing.

## Single Command Execution
To run all automations seamlessly, we will adopt the **Node.js Native Test Runner** (`node --test` via `tsx --test`). 
Automations will be structured using `test()` and `describe()` blocks instead of raw `main()` functions. This provides out-of-the-box concurrency, structured reporting, and robust error handling without introducing heavy dependencies like Jest or Vitest.

## Stagehand Best Practices
1. **Clean Teardown**: Node's `after()` or `afterAll()` hooks will be mandated to execute `await stagehand.close()` ensuring no browser processes are left hanging if a test fails mid-execution.
2. **Predictable Targeting**: While LLM extraction is powerful, standard Playwright locators will be preferred for static elements (available via `stagehand.context.pages()[0]`).
3. **Zod Schemas**: Extraction schemas will be strongly typed, with complex or repeated schemas moved into `src/utils/schemas/`.
