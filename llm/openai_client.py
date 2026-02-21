import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = "gpt-4.1-mini"


def chat(messages, model=None):
    response = _client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content
