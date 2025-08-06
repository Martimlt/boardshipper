"""
WSGI config for boardshipper_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boardshipper_project.settings')

application = get_wsgi_application()