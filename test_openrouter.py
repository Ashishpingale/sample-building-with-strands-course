from strands import Agent
from openrouter_helper import get_openrouter_model

# Initialize model via OpenRouter
model = get_openrouter_model(model_id="cohere/north-mini-code:free", max_tokens=2048)

# Create and run Strands agent
agent = Agent(model=model)
response = agent("Explain what an AI agent is in two sentences.")

print("\n--- OpenRouter Agent Response ---")
print(response)
