"""
WSGI config for counseling_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Vercel runs this file from its own directory (counseling_app/counseling_app/).
# Django needs the PARENT directory (counseling_app/) in sys.path so it can
# resolve 'counseling_app.settings', 'counseling_app.urls', etc.
BASE = Path(__file__).resolve().parent.parent  # → .../counseling_app/
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counseling_app.settings')

application = get_wsgi_application()

app = application
