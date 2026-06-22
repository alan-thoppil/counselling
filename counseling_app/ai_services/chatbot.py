import logging
from django.conf import settings
from .client import generate_llm_response, stream_llm_response

logger = logging.getLogger(__name__)

# Function to query LLM for chat responses with clinical triage rules
def get_chatbot_response(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    fallback_text = (
        "Thank you for sharing that with me. I am a triage-only mental health assistant "
        "and cannot provide any diagnoses or clinical assessments. If you are struggling "
        "or need professional guidance, we strongly recommend booking a session with one "
        "of our licensed therapists."
    )

    try:
        # Build clean message history adhering to roles supported by LLM API (user / assistant)
        messages = []
        for i, msg in enumerate(conversation_history):
            if isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content')
                if role in ['user', 'assistant'] and content:
                    messages.append({
                        'role': role,
                        'content': content
                    })
            elif isinstance(msg, str) and msg.strip():
                # Alternate role: even index is user, odd index is assistant
                role = 'user' if i % 2 == 0 else 'assistant'
                messages.append({
                    'role': role,
                    'content': msg.strip()
                })

        # Append current user message
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Triage rules system prompt
        system_prompt = (
            "You are a triage-only mental health assistant. "
            "You must NEVER diagnose the user or provide medical/clinical treatments or assessments. "
            "Be empathetic, calm, and supportive, but keep boundaries clear.\n\n"
            "Formatting Rules:\n"
            "1. Avoid long paragraphs. Keep your responses short, split into concise, separate sentences.\n"
            "2. Present any suggestions, coping techniques, or advice as a list of bullet points.\n"
            "3. At the end of your response, you MUST always offer to book a therapist and include a clear booking call-to-action."
        )

        # Send request to unified LLM API helper
        response_text = generate_llm_response(
            messages,
            system_prompt=system_prompt,
            max_tokens=1000
        )

        if response_text:
            return response_text
        
        return fallback_text

    except Exception as e:
        logger.error(f"Error in get_chatbot_response AI service: {e}")
        # Fallback in case of API or network failure
        return (
            "I apologize, but I am experiencing issues generating a response right now. "
            "Please note that I am a triage assistant and cannot diagnose conditions. If you need "
            "support, we recommend scheduling an appointment with one of our licensed therapists."
        )


def get_chatbot_stream(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    try:
        messages = []
        for i, msg in enumerate(conversation_history):
            if isinstance(msg, dict):
                role = msg.get('role')
                content = msg.get('content')
                if role in ['user', 'assistant'] and content:
                    messages.append({
                        'role': role,
                        'content': content
                    })
            elif isinstance(msg, str) and msg.strip():
                role = 'user' if i % 2 == 0 else 'assistant'
                messages.append({
                    'role': role,
                    'content': msg.strip()
                })

        messages.append({
            'role': 'user',
            'content': user_message
        })

        system_prompt = (
            "You are a triage-only mental health assistant. "
            "You must NEVER diagnose the user or provide medical/clinical treatments or assessments. "
            "Be empathetic, calm, and supportive, but keep boundaries clear.\n\n"
            "Formatting Rules:\n"
            "1. Avoid long paragraphs. Keep your responses short, split into concise, separate sentences.\n"
            "2. Present any suggestions, coping techniques, or advice as a list of bullet points.\n"
            "3. At the end of your response, you MUST always offer to book a therapist and include a clear booking call-to-action."
        )

        for chunk in stream_llm_response(
            messages,
            system_prompt=system_prompt,
            max_tokens=1000
        ):
            yield chunk

    except Exception as e:
        logger.error(f"Error in get_chatbot_stream AI service: {e}")
        yield (
            "I apologize, but I am experiencing issues generating a response right now. "
            "Please note that I am a triage assistant and cannot diagnose conditions. If you need "
            "support, we recommend scheduling an appointment with one of our licensed therapists."
        )


