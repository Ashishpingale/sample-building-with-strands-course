import os
from pathlib import Path
from strands.models.openai import OpenAIModel

def _load_env() -> None:
    """Load variables from .env file into os.environ if not already present."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip("'\""))

_load_env()

def get_openrouter_model(
    model_id: str | None = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    **extra_params,
) -> OpenAIModel:
    """Returns a Strands OpenAIModel configured for OpenRouter.

    The model is resolved in this order: the ``model_id`` argument, the
    ``OPENROUTER_MODEL`` environment variable, then the default below.

    Common model_ids:
        - "cohere/north-mini-code:free"
        - "nvidia/nemotron-3.5-super-vl:free"
        - "openai/gpt-4o-mini"
        - "anthropic/claude-3.5-sonnet"
        - "google/gemini-2.5-flash"
        - "meta-llama/llama-3.3-70b-instruct"
    """
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model_id = model_id or os.environ.get(
        "OPENROUTER_MODEL", "cohere/north-mini-code:free"
    )

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment or .env file.")

    params = {"max_tokens": max_tokens, "temperature": temperature, **extra_params}

    return OpenAIModel(
        client_args={
            "api_key": api_key,
            "base_url": base_url,
        },
        model_id=model_id,
        params=params,
    )

