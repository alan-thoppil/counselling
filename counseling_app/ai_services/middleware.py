import logging
from django.utils.deprecation import MiddlewareMixin
from .models import CrisisLog

logger = logging.getLogger(__name__)

# Middleware to intercept POST requests and scan for crisis keywords
class CrisisDetectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST':
            # Keywords indicating personal crisis or self-harm intention
            keywords = ["suicide", "end my life", "hurt myself", "kill myself", "want to die", "self harm", "no reason to live"]
            
            try:
                # Read and check request body safely
                body_bytes = request.body
                if body_bytes:
                    body_str = body_bytes.decode('utf-8', errors='ignore')
                    lower_body = body_str.lower()
                    
                    matched_keyword = None
                    for kw in keywords:
                        if kw in lower_body:
                            matched_keyword = kw
                            break
                    
                    if matched_keyword:
                        # Fetch request user if authenticated
                        user = request.user if request.user and request.user.is_authenticated else None
                        
                        # Store a preview/snippet of the request body (up to 500 characters)
                        text_snippet = body_str[:500]
                        
                        # Save to database
                        CrisisLog.objects.create(
                            user=user,
                            text_snippet=text_snippet,
                            detected_keyword=matched_keyword
                        )
                        
                        logger.warning(
                            f"CrisisDetectionMiddleware: flagged '{matched_keyword}' keyword for user '{user}'"
                        )
            except Exception as e:
                # Do not block the request in case of parsing errors
                logger.error(f"Error in CrisisDetectionMiddleware parsing: {e}")
                
        # Return None to continue standard request processing
        return None
