import json
import logging
from django.conf import settings
from .client import generate_llm_response

logger = logging.getLogger(__name__)

# Function to check text for suicidal ideation or self-harm crisis indicators
def check_crisis(text):
    # Keyword list for direct checks
    keywords = ["suicide", "end my life", "hurt myself", "kill myself", "want to die", "self harm", "no reason to live"]
    matched_keyword = None
    lower_text = text.lower() if text else ""

    # Check for direct keyword matches
    for kw in keywords:
        if kw in lower_text:
            matched_keyword = kw
            break

    # If no keyword matches, return early without calling LLM API
    if not matched_keyword:
        return {
            "is_crisis": False,
            "matched_keyword": None,
            "confidence": "low"
        }

    def get_fallback_crisis():
        return {
            "is_crisis": True,
            "matched_keyword": matched_keyword,
            "confidence": "high"
        }

    try:
        prompt = (
            f"The following user text triggered a keyword alert for crisis/self-harm. "
            f"Please verify if the context of the text indicates a real, active personal crisis, self-harm intention, or suicidal ideation.\n\n"
            f"Text: \"{text}\"\n\n"
            f"Respond with a JSON object containing two keys:\n"
            f"1. \"is_crisis\": boolean (true if the text expresses genuine intent, active crisis, or urgent self-harm/suicidal thoughts; false if it is hypothetical, historical, a citation, or benign conversational usage)\n"
            f"2. \"confidence\": string (\"high\", \"medium\", or \"low\") representing your confidence in this decision.\n\n"
            f"Output ONLY valid raw JSON with no other formatting."
        )

        raw_text = generate_llm_response(prompt, max_tokens=150)

        if not raw_text:
            return get_fallback_crisis()

        # Clean possible markdown block formatting
        raw_text = raw_text.strip().replace("```json", "").replace("```", "").strip()

        result = json.loads(raw_text)
        is_crisis = bool(result.get("is_crisis", False))
        confidence = str(result.get("confidence", "medium")).lower()
        if confidence not in ["high", "medium", "low"]:
            confidence = "medium"

        return {
            "is_crisis": is_crisis,
            "matched_keyword": matched_keyword,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Error in check_crisis AI service: {e}")
        return get_fallback_crisis()
