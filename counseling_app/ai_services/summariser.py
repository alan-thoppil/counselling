import logging
from django.conf import settings
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Function to generate a 3-sentence plain summary of session notes
def summarise_session_note(note_text):
    if not note_text or not note_text.strip():
        return "No session note text was provided."

    try:
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-6')

        # Heuristic fallback if API key is not configured
        if not api_key or api_key == 'your-key-here':
            sentences = [s.strip() for s in note_text.split('.') if s.strip()]
            fallback = " ".join(sentences[:3])
            if not fallback:
                fallback = "No summary could be compiled."
            elif not fallback.endswith('.'):
                fallback += "."
            return fallback

        client = Anthropic(api_key=api_key)

        prompt = (
            f"Please summarize the following therapist session note. "
            f"The summary must be exactly 3 sentences long and written in plain, clear, empathetic language "
            f"suitable for a patient to read.\n\n"
            f"Note:\n\"{note_text}\"\n\n"
            f"Respond with ONLY the 3-sentence summary, with no other introductory or concluding text."
        )

        response = client.messages.create(
            model=model,
            max_tokens=250,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        if response.content:
            first_block = response.content[0]
            return getattr(first_block, 'text', '').strip()

        return "Could not generate summary."

    except Exception as e:
        logger.error(f"Error in summarise_session_note AI service: {e}")
        # Fallback to taking the first 3 sentences of the note text
        sentences = [s.strip() for s in note_text.split('.') if s.strip()]
        fallback = " ".join(sentences[:3])
        if not fallback:
            fallback = "Error generating summary."
        elif not fallback.endswith('.'):
            fallback += "."
        return fallback
