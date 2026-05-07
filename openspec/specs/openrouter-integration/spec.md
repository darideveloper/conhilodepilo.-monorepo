# openrouter-integration Specification

## Purpose
Define the integration requirements for using OpenRouter as an LLM provider within Stagehand, including support for custom models, analytics headers, and a patch for agent functionality.
## Requirements
### Requirement: LLM Provider Configuration
The system MUST allow configuring OpenRouter as the primary LLM provider. This configuration MUST support optional `OPENROUTER_REFERER`, `OPENROUTER_TITLE`, and `OPENROUTER_MODEL` environment variables.

#### Scenario: Using OpenRouter with DeepSeek V3
Given an `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` (e.g., `deepseek/deepseek-chat`) are set in the environment
When the Stagehand instance is initialized with an OpenRouter client
Then Stagehand should successfully execute browser actions using that model and include analytics headers if provided.

### Requirement: Agent Functionality Compatibility
The OpenRouter integration MUST support Stagehand's `agent()` functionality. This requires implementing a patch for the standard `AISdkClient` to expose the necessary `getLanguageModel` method.

#### Scenario: Running a Stagehand Agent
Given Stagehand is configured with OpenRouter using `PatchAISdkClient`
When `stagehand.agent()` is called and executed
Then the agent should successfully process the request using the configured OpenRouter model.

