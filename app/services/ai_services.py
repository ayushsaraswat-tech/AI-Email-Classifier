import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify_email(text: str):

    prompt = f"""
Analyze this email and return JSON only.

Email:
{text}

Return format:
{{
"category": "...",
"intent": "...",
"priority": "...",
"sentiment": "...",
"confidence": "..."
}}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    try:
        cleaned = response.text.replace("```json", "").replace("```", "")
        data = json.loads(cleaned)

        return {
            "category": data.get("category", "General"),
            "intent": data.get("intent", "Inquiry"),
            "priority": data.get("priority", "Low"),
            "sentiment": data.get("sentiment", "Neutral"),
            "confidence": data.get("confidence", "Medium")
        }

    except Exception:

        return {
            "category": "General",
            "intent": "Inquiry",
            "priority": "Low",
            "sentiment": "Neutral",
            "confidence": "Medium"
        }


def generate_response(text: str):

    prompt = f"""
Write a professional email response to the following message.

Email:
{text}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text


def explain_classification(text: str, classification: dict):

    explanation = {
        "reasoning": "",
        "key_phrases": [],
        "confidence": classification.get("confidence", "Medium")
    }

    keywords = ["urgent", "issue", "help", "request", "please", "problem"]

    lower = text.lower()

    explanation["key_phrases"] = [k for k in keywords if k in lower]

    if classification["priority"] == "High":
        explanation["reasoning"] = "Urgency indicators detected in email."
    elif classification["intent"] == "Inquiry":
        explanation["reasoning"] = "User appears to be asking for information."
    else:
        explanation["reasoning"] = "General email communication pattern."

    return explanation