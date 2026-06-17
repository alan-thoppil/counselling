"""
Vercel WSGI entry point for the counseling_app Django project.

Placed at api/index.py (project root) so @vercel/python resolves
paths cleanly. The Django project lives one level down in counseling_app/.
"""

import sys
import os
from pathlib import Path

# Project root (parent of this file's directory: project_root/api/../ → project_root/)
ROOT = Path(__file__).resolve().parent.parent          # .../counselling/
DJANGO_DIR = ROOT / 'counseling_app'                   # .../counselling/counseling_app/

# Insert the outer counseling_app/ dir so Django can find:
#   counseling_app.settings  → counseling_app/counseling_app/settings.py
#   counseling_app.urls      → counseling_app/counseling_app/urls.py
for path in [str(DJANGO_DIR), str(ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counseling_app.settings')

from django.core.wsgi import get_wsgi_application   # noqa: E402
application = get_wsgi_application()

# Vercel looks for a variable named `app`
app = application
