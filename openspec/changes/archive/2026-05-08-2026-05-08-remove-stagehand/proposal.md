# Proposal: Remove Stagehand from Project

## Why
Stagehand was introduced for AI-driven E2E testing of the landing page (data validation, media reachability, etc.). However, it has proven to be brittle in local development, suffering from schema extraction failures, LLM provider routing issues (e.g., OpenRouter endpoint 404 errors), and unexpected delays even when caching is disabled. Given these limitations, the overhead of maintaining AI-based interactions outweighs the benefits.

## What Changes
This proposal entirely removes the `stagehand` module and its associated dependencies from the project.
- Deletes the `stagehand/` directory entirely.
- Removes the specific OpenSpec requirements that mandated Stagehand usage (`stagehand-architecture`, `landing-data-validation`, `openrouter-integration`).
