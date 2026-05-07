import "dotenv/config";
import { Stagehand, AISdkClient } from "@browserbasehq/stagehand";
import { createOpenRouter } from "@openrouter/ai-sdk-provider";
import type { LanguageModelV2 } from "@ai-sdk/provider";

/**
 * PatchAISdkClient
 *
 * Stagehand v3's public AISdkClient is missing the getLanguageModel method,
 * which is required for the agent() functionality to work correctly.
 */
class PatchAISdkClient extends AISdkClient {
  private _model: LanguageModelV2;

  constructor({ model }: { model: LanguageModelV2 }) {
    super({ model });
    this._model = model;
  }

  getLanguageModel() {
    return this._model;
  }
}

async function main() {
  const openrouterApiKey = process.env.OPENROUTER_API_KEY;

  if (!openrouterApiKey || openrouterApiKey === "YOUR_OPENROUTER_API_KEY") {
    console.error(
      "Please set OPENROUTER_API_KEY in your .env file to run this example."
    );
    process.exit(1);
  }

  const openrouter = createOpenRouter({
    apiKey: openrouterApiKey,
    headers: {
      "HTTP-Referer": process.env.OPENROUTER_REFERER || "https://stagehand.dev",
      "X-OpenRouter-Title": process.env.OPENROUTER_TITLE || "Stagehand OpenRouter",
    },
  });

  const modelName = process.env.OPENROUTER_MODEL || "anthropic/claude-3.5-sonnet";

  const stagehand = new Stagehand({
    env: "LOCAL",
    model: modelName,
    llmClient: new PatchAISdkClient({
      model: openrouter(modelName),
    }),
  });

  await stagehand.init();

  console.log(`Stagehand Session Started`);
  console.log(
    `Watch live: https://browserbase.com/sessions/${stagehand.browserbaseSessionId}`
  );

  const page = stagehand.context.pages()[0];

  await page.goto("https://stagehand.dev");

  const extractResult = await stagehand.extract(
    "Extract the value proposition from the page."
  );
  console.log(`Extract result:\n`, extractResult);

  const actResult = await stagehand.act("Click the 'Docs' link.");
  console.log(`Act result:\n`, actResult);

  const observeResult = await stagehand.observe("What can I click on this page?");
  console.log(`Observe result:\n`, observeResult);

  const agent = stagehand.agent({
    systemPrompt: "You're a helpful assistant that can control a web browser.",
  });

  const agentResult = await agent.execute(
    "What is the most accurate model to use in Stagehand?"
  );
  console.log(`Agent result:\n`, agentResult);

  await stagehand.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
