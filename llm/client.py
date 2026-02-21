from llm.openai_client import chat as _openai_chat
#from llm.gemini_client import chat as _gemini_chat
import os

PROVIDERS = {
    "openai": _openai_chat,
    #"gemini": _gemini_chat,
}

DEFAULT_PROVIDER = "openai"


def chat(messages, model=None, provider=None):
    provider = provider or DEFAULT_PROVIDER
    fn = PROVIDERS.get(provider)
    print(f"Using provider: {provider}, API key is {os.getenv(f'{provider.upper()}_API_KEY')}")
    if fn is None:
        raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS)}")
    return fn(messages, model=model)
