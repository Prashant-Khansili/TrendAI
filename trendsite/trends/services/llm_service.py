import os
import requests

HF_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"


def build_prompt(topic, context, preferences):
    tone = preferences.get("tone") or "clear and professional"
    audience = preferences.get("audience") or "general audience"
    length = preferences.get("length") or "short"
    emoji_style = preferences.get("emoji_style") or "light"
    cta = preferences.get("cta") or ""
    hashtags = preferences.get("hashtags") or ""
    platforms = preferences.get("platforms") or "LinkedIn, Instagram, X"

    prompt = (
        "You are a social media content strategist.\n\n"
        f"Topic: {topic}\n\n"
        f"Context: {context}\n\n"
        f"Audience: {audience}\n"
        f"Tone: {tone}\n"
        f"Length: {length}\n"
        f"Emoji style: {emoji_style}\n"
        f"CTA: {cta}\n"
        f"Hashtag preferences: {hashtags}\n"
        f"Platforms: {platforms}\n\n"
        "Generate three platform-specific drafts with headings:\n"
        "LinkedIn:\n"
        "Instagram:\n"
        "X (Twitter):\n"
        "Hashtags:\n"
        "Return clean text only."
    )
    return prompt


def generate_social_posts(topic, context, preferences):
    if not HF_TOKEN:
        raise RuntimeError("Missing HF_API_TOKEN. Set it in your .env or environment variables.")

    prompt = build_prompt(topic, context, preferences)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    result = response.json()

    if isinstance(result, list) and result:
        return result[0].get("generated_text", "").strip()

    return ""
