import json
import logging
from django.conf import settings
from .client import generate_llm_response

logger = logging.getLogger(__name__)

# Function to match user onboarding answers to therapist specialities
def match_therapist(answers):
    if not isinstance(answers, list):
        answers = []

    # Standard fallback specialities
    default_specialities = ["general therapy", "talk therapy", "mindfulness"]

    def get_fallback_match():
        joined_answers = " ".join([str(a) for a in answers]).lower()
        recs = []
        if any(w in joined_answers for w in ["anxious", "anxiety", "panic", "worry"]):
            recs.append("anxiety")
        if any(w in joined_answers for w in ["sad", "depressed", "depression", "unhappy"]):
            recs.append("CBT")
        if any(w in joined_answers for w in ["trauma", "abuse", "ptsd", "past"]):
            recs.append("trauma")
        if any(w in joined_answers for w in ["relationship", "couple", "family", "marriage"]):
            recs.append("relationships")
        
        if not recs:
            recs = default_specialities
        return recs

    try:
        # Format answers for prompting
        formatted_answers = "\n".join([f"Question {i+1}: {ans}" for i, ans in enumerate(answers)])

        prompt = (
            f"Based on the following 5 user onboarding answers, recommend the top 2-4 therapist specialisations "
            f"or treatment modalities (e.g. \"anxiety\", \"CBT\", \"trauma\", \"relationships\", \"grief\", \"depression\", \"mindfulness\") "
            f"that would fit the user's needs.\n\n"
            f"{formatted_answers}\n\n"
            f"Return a JSON array containing only the string values of the recommended specialisations.\n"
            f"Example output: [\"anxiety\", \"CBT\", \"trauma\"]\n\n"
            f"Respond with ONLY the JSON array, with no other description or markdown formatting wrapper."
        )

        raw_text = generate_llm_response(prompt, max_tokens=150)

        if not raw_text:
            return get_fallback_match()

        # Clean markdown JSON block formatting if present
        raw_text = raw_text.strip().replace("```json", "").replace("```", "").strip()

        result = json.loads(raw_text)
        if isinstance(result, list):
            return [str(item) for item in result]

        return default_specialities

    except Exception as e:
        logger.error(f"Error in match_therapist AI service: {e}")
        return get_fallback_match()
