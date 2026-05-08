# Proposal: Refactor Stagehand Architecture

## Why
Currently, the Stagehand setup within the `stagehand/` directory has duplicated configuration across files (`index.ts`, `tests/landing-integration.test.ts`). There is no unified execution model; automations are run individually via separate npm scripts. Additionally, there is no standardized location for reusable UI interactions, DOM helpers, or authentication routines, making it difficult to author new automations efficiently. To scale our E2E and data extraction capabilities, the Stagehand setup needs a robust, centralized architecture.

## What Changes
This proposal introduces a structured architecture for the `stagehand` module:
- **Centralized Configuration**: Extract OpenRouter and Stagehand initialization into a shared module.
- **Unified Runner**: Adopt Node.js native test runner to execute all automations with a single command.
- **Shared Utilities**: Establish a dedicated directory for general and reusable functions.
- **Lifecycle Management**: Implement strict setup and teardown routines following Stagehand best practices to prevent zombie browser processes.

This refactor sets the foundation for all future automated interactions with the Dashboard and Landing Page.
