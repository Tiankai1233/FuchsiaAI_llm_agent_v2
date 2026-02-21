import os
import base64
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DEFAULT_MODEL = "gemini-2.0-flash"


def _convert_messages(messages):
    """Convert OpenAI-style messages to Gemini contents format.

    Gemini doesn't have a 'system' role in contents — it's passed separately.
    The remaining messages map 'assistant' -> 'model'.
    Supports both text and image content.
    """
    system_parts = []
    contents = []

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            system_parts.append(content)
        else:
            # Handle both string content and array content (with images)
            parts = []
            if isinstance(content, str):
                parts.append({"text": content})
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        parts.append({"text": item["text"]})
                    elif item.get("type") == "image_url":
                        # Extract base64 data from data URI
                        image_url = item["image_url"]["url"]
                        if image_url.startswith("data:"):
                            # Format: data:image/png;base64,{base64_string}
                            header, data = image_url.split(",", 1)
                            mime_type = header.split(":")[1].split(";")[0]
                            parts.append({
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": data
                                }
                            })
                        else:
                            # URL format (not supported in this implementation)
                            parts.append({"text": f"[Image URL: {image_url}]"})
            
            if parts:
                contents.append({
                    "role": "model" if role == "assistant" else "user",
                    "parts": parts,
                })

    system_instruction = "\n".join(system_parts) if system_parts else None
    return system_instruction, contents


def chat(messages, model=None):
    system_instruction, contents = _convert_messages(messages)

    response = _client.models.generate_content(
        model=model or DEFAULT_MODEL,
        contents=contents,
        config={
            "system_instruction": system_instruction,
            "temperature": 0.7,
        },
    )
    return response.text
