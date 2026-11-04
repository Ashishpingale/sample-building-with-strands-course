"""OpenRouter Automatic Redirection Bridge for Strands Agents Course.

This module can be installed into any virtualenv to automatically redirect
BedrockModel and default Agent() instantiations to OpenRouter.

To install into current Python environment:
    python openrouter_bridge.py install
"""
import os
import sys
from pathlib import Path

def setup_bridge():
    """Patches BedrockModel in strands to use OpenRouter."""
    # Find .env
    curr = Path.cwd()
    search_paths = [curr] + list(curr.parents)
    try:
        root = Path(__file__).resolve().parent
        if root not in search_paths:
            search_paths.append(root)
    except Exception:
        pass

    for p in search_paths:
        env_file = p / ".env"
        if env_file.is_file():
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
                break
            except Exception:
                pass

    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return False

    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    try:
        from strands.models.bedrock import BedrockModel
        from strands.models.openai import OpenAIModel
        import strands.models

        def bedrock_openrouter_new(cls, *args, **kwargs):
            model_id = kwargs.get("model_id") or (args[0] if args else None)
            model_str = str(model_id or "").lower()

            target_model = os.environ.get("OPENROUTER_MODEL")
            if not target_model:
                if "haiku" in model_str:
                    target_model = "anthropic/claude-haiku-4.5"
                elif "opus" in model_str:
                    target_model = "anthropic/claude-opus-4.5"
                elif "sonnet" in model_str or "claude" in model_str:
                    target_model = "anthropic/claude-sonnet-4.5"
                else:
                    target_model = "openai/gpt-4o-mini"

            params = kwargs.get("params")
            params = dict(params) if params else {}

            if "max_tokens" not in params:
                params["max_tokens"] = int(os.environ.get("OPENROUTER_MAX_TOKENS", 2048))
            if "temperature" not in params:
                params["temperature"] = 0.7

            return OpenAIModel(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url,
                },
                model_id=target_model,
                params=params,
                context_window_limit=kwargs.get("context_window_limit", 200_000),
            )

        BedrockModel.__new__ = staticmethod(bedrock_openrouter_new)
        strands.models.BedrockModel.__new__ = staticmethod(bedrock_openrouter_new)
        return True
    except Exception as e:
        return False

def install():
    import site
    site_packages = site.getsitepackages()
    if not site_packages:
        print("Error: Could not locate site-packages directory.")
        return 1

    target = Path(site_packages[0]) / "sitecustomize.py"
    source = Path(__file__).resolve()

    content = f'''import sys
from pathlib import Path

# Add project root to path if needed and run bridge
bridge_file = Path(r"{source}")
if bridge_file.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("openrouter_bridge", bridge_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.setup_bridge()
'''
    target.write_text(content)
    print(f"Successfully installed OpenRouter bridge to {target}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        sys.exit(install())
    else:
        success = setup_bridge()
        if success:
            print("OpenRouter bridge is active.")
        else:
            print("Could not activate OpenRouter bridge. Check OPENROUTER_API_KEY.")

