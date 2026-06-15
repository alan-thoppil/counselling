import logging
from django.conf import settings
from anthropic import Anthropic
from anthropic.types import MessageParam
from typing import cast, List

logger = logging.getLogger(__name__)

# Function to query Claude for chat responses with clinical triage rules
def get_chatbot_response(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    try:
        # Load credentials from settings
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-6')

        # Fallback if API key is not set or placeholder
        if not api_key or api_key == 'your-key-here':
            return (
                "Thank you for sharing that with me. I am a triage-only mental health assistant "
                "and cannot provide any diagnoses or clinical assessments. If you are struggling "
                "or need professional guidance, we strongly recommend booking a session with one "
                "of our licensed therapists."
            )

        client = Anthropic(api_key=api_key)

        # Build clean message history adhering to roles supported by Anthropic (user / assistant)
        messages: List[MessageParam] = []
        for msg in conversation_history:
            role = msg.get('role')
            content = msg.get('content')
            if role in ['user', 'assistant'] and content:
                messages.append(cast(MessageParam, {
                    'role': role,
                    'content': content
                }))

        # Append current user message
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Triage rules system prompt
        system_prompt = (
            "You are a triage-only mental health assistant. "
            "You must NEVER diagnose the user or provide medical/clinical treatments or assessments. "
            "Be empathetic, calm, and supportive, but keep boundaries clear. "
            "At the end of your response, you MUST always offer to book a therapist and include "
            "a clear booking call-to-action."
        )

        # Send request to Anthropic API
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        if response.content:
            first_block = response.content[0]
            return getattr(first_block, 'text', '')
        else:
            return (
                "I am here to support you. I cannot diagnose conditions. Please consider "
                "booking a session with one of our licensed therapists."
            )

    except Exception as e:
        logger.error(f"Error in get_chatbot_response AI service: {e}")
        # Fallback in case of API or network failure
        return (
            "I apologize, but I am experiencing issues generating a response right now. "
            "Please note that I am a triage assistant and cannot diagnose conditions. If you need "
            "support, we recommend scheduling an appointment with one of our licensed therapists."
        )
