import os
import requests
import json
import logging
from dotenv import load_dotenv
load_dotenv()
# 🔥 Setup logger (only once per file)
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"


def call_llm(prompt: str):
    try:
        logger.info("Calling OpenRouter LLM...")

        response = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        logger.info(f"LLM Status Code: {response.status_code}")
        logger.info(f"LLM Response: {response.text}")

        if response.status_code != 200:
            logger.error(f"LLM Error Response: {response.text}")
            return ""

        data = response.json()

        output = data["choices"][0]["message"]["content"]
        logger.info("LLM Response received successfully")

        return output

    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return ""


def classify_email(text: str):
    prompt = f"""
    You are an API.

    Return ONLY valid JSON.
    Do NOT include any explanation.

    {{
      "category": "...",
      "intent": "...",
      "priority": "...",
      "sentiment": "..."
    }}

    Email:
    {text}
    """

    logger.info("Classifying email...")

    output = call_llm(prompt)

    # 🔥 Clean markdown formatting if present
    output = output.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(output)
        logger.info("Email classified successfully")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        logger.error(f"RAW OUTPUT: {output}")

        return {
            "category": "Unknown",
            "intent": "Unknown",
            "priority": "Unknown",
            "sentiment": "Unknown"
        }


def generate_response(text: str):
    logger.info("Generating email response...")

    prompt = f"""
    Write a professional email reply for:

    {text}
    """

    return call_llm(prompt)


def explain_classification(text: str, classification: dict):
    logger.info("Generating classification explanation...")

    prompt = f"""
    Explain why this email was classified this way.

    Email:
    {text}

    Classification:
    {classification}

    Give a short explanation.
    """

    return call_llm(prompt)


# 🔥 Debug log instead of print
logger.info(f"API KEY loaded: {'YES' if OPENROUTER_API_KEY else 'NO'}")