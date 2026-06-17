import logging
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_llm_response(prompt_or_messages, system_prompt=None, max_tokens=1024, temperature=0.2):
    """
    Centralized helper to call NVIDIA NIM API.
    prompt_or_messages can be a string (user prompt) or a list of dicts (messages history).
    Returns None if NVIDIA_API_KEY is not configured or matches the placeholder 'your-key-here'.
    """
    api_key = getattr(settings, 'NVIDIA_API_KEY', None)
    model = getattr(settings, 'NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')
    
    if not api_key or api_key == 'your-key-here':
        return None

    try:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        if isinstance(prompt_or_messages, str):
            messages.append({"role": "user", "content": prompt_or_messages})
        elif isinstance(prompt_or_messages, list):
            messages.extend(prompt_or_messages)
        else:
            logger.error(f"Invalid prompt_or_messages type: {type(prompt_or_messages)}")
            return None
            
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = httpx.post(url, headers=headers, json=payload, timeout=45.0)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"].strip()
            logger.error(f"Unexpected response format from NVIDIA NIM: {response.text}")
        else:
            logger.error(f"NVIDIA NIM API error status {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Error calling NVIDIA NIM API: {e}")
        
    return None
