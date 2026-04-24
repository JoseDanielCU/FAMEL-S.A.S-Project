"""Configuración WSGI para FAMEL S.A.S."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famel.settings')
application = get_wsgi_application()
