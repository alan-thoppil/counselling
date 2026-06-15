import json
import logging
from django.conf import settings
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Function to analyze sentiment of a journal entry or text snippet
def analyze_sentiment(text):
    default_response = {"sentiment": "NEUTRAL", "score": 0.5}
    if not text or not text.strip():
        return default_response

    try:
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-6')

        # Heuristic fallback if API key is not configured
        if not api_key or api_key == 'your-key-here':
            lower_text = text.lower()
            positive_words = ['happy', 'good', 'glad', 'wonderful', 'joy', 'excited', 'great', 'peace', 'calm', 'hope']
            negative_words = ['sad', 'bad', 'angry', 'hurt', 'pain', 'anxious', 'scared', 'depressed', 'hate', 'cry', 'lonely']
            pos_count = sum(1 for w in positive_words if w in lower_text)
            neg_count = sum(1 for w in negative_words if w in lower_text)
            
            if pos_count > neg_count:
                return {"sentiment": "POSITIVE", "score": round(min(0.5 + 0.1 * (pos_count - neg_count), 0.95), 2)}
            elif neg_count > pos_count:
                return {"sentiment": "NEGATIVE", "score": round(min(0.5 + 0.1 * (neg_count - pos_count), 0.95), 2)}
            return default_response

        client = Anthropic(api_key=api_key)

        prompt = (
            f"Analyze the sentiment of the following journal entry text:\n\n"
            f"\"{text}\"\n\n"
            f"Return a JSON object with exactly two keys:\n"
            f"1. \"sentiment\": must be exactly one of \"POSITIVE\", \"NEGATIVE\", or \"NEUTRAL\"\n"
            f"2. \"score\": a float value between 0.0 and 1.0 representing the intensity or confidence of the sentiment classification.\n\n"
            f"Output ONLY valid raw JSON, with no other description or markdown formatting wrapper."
        )

        response = client.messages.create(
            model=model,
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        if response.content:
            first_block = response.content[0]
            raw_text = getattr(first_block, 'text', '').strip()
            
            # Clean markdown formatting if present
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if len(lines) > 2:
                    raw_text = "\n".join(lines[1:-1])
            
            # Remove any trailing code block characters
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

            result = json.loads(raw_text)
            sentiment = str(result.get("sentiment", "NEUTRAL")).upper()
            if sentiment not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                sentiment = "NEUTRAL"

            try:
                score = float(result.get("score", 0.5))
                score = max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                score = 0.5

            return {"sentiment": sentiment, "score": round(score, 2)}

        return default_response

    except Exception as e:
        logger.error(f"Error in analyze_sentiment AI service: {e}")
        return default_response
