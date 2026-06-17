import logging
from django.conf import settings
from .client import generate_llm_response

logger = logging.getLogger(__name__)

# Function to generate a 3-sentence plain summary of session notes
def summarise_session_note(note_text):
    if not note_text or not note_text.strip():
        return "No session note text was provided."

    def get_fallback_summary():
        sentences = [s.strip() for s in note_text.split('.') if s.strip()]
        fallback = " ".join(sentences[:3])
        if not fallback:
            fallback = "No summary could be compiled."
        elif not fallback.endswith('.'):
            fallback += "."
        return fallback

    try:
        prompt = (
            f"Please summarize the following therapist session note. "
            f"The summary must be exactly 3 sentences long and written in plain, clear, empathetic language "
            f"suitable for a patient to read.\n\n"
            f"Note:\n\"{note_text}\"\n\n"
            f"Respond with ONLY the 3-sentence summary, with no other introductory or concluding text."
        )

        response_text = generate_llm_response(prompt, max_tokens=250)

        if response_text:
            return response_text

        return get_fallback_summary()

    except Exception as e:
        logger.error(f"Error in summarise_session_note AI service: {e}")
        return get_fallback_summary()
