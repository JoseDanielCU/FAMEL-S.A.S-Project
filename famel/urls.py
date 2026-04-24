"""URLs raíz del proyecto FAMEL S.A.S."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Todas las rutas de la app principal
]
