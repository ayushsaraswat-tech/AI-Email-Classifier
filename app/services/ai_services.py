import json
import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"


def _unknown_classification():
    return {
        "category": "Unknown",
        "intent": "Unknown",
        "priority": "Unknown",
        "sentiment": "Unknown",
    }


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
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=45,
        )

        logger.info("LLM Status Code: %s", response.status_code)

        if response.status_code != 200:
            logger.error("LLM Error Response: %s", response.text)
            return ""

        data = response.json()
        output = data["choices"][0]["message"].get("content") or ""
        logger.info("LLM Response received successfully")

        return output

    except Exception as exc:
        logger.error("LLM call failed: %s", str(exc))
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

    output = call_llm(prompt) or ""
    output = output.replace("```json", "").replace("```", "").strip()

    if not output:
        logger.error("LLM returned an empty classification response")
        return _unknown_classification()

    try:
        result = json.loads(output)
        logger.info("Email classified successfully")
        return {
            "category": result.get("category") or "Unknown",
            "intent": result.get("intent") or "Unknown",
            "priority": result.get("priority") or "Unknown",
            "sentiment": result.get("sentiment") or "Unknown",
        }

    except json.JSONDecodeError as exc:
        logger.error("JSON parsing failed: %s", str(exc))
        logger.error("RAW OUTPUT: %s", output)
        return _unknown_classification()


def generate_response(text: str, user):
    logger.info("Generating email response...")

    prompt = f"""
    Write a professional email reply for:

    {text}
    """

    draft_response = call_llm(prompt) or (
        "Thank you for your email. I will review this and get back to you shortly."
    )

    signature = ""

    if user.signature_name:
        signature += f"\n\nBest regards,\n{user.signature_name}"

    if user.company_signature:
        signature += f"\n{user.company_signature}"

    return draft_response + signature


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

    return call_llm(prompt) or "The AI service did not return an explanation for this email."


logger.info("API KEY loaded: %s", "YES" if OPENROUTER_API_KEY else "NO")
