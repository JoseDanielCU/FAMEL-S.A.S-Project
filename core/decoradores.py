"""
Decoradores de control de acceso por rol para FAMEL S.A.S.
Uso:  @rol_requerido('ADMIN', 'OPERARIO')
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles):
    """
    Protege una vista verificando que el usuario tenga uno de los roles indicados.
    Los superusuarios (admin Django) siempre tienen acceso.
    """
    def decorador(vista):
        @wraps(vista)
        def wrapper(request, *args, **kwargs):
            # 1. Verificar autenticación
            if not request.user.is_authenticated:
                return redirect('login')

            # 2. Superusuario: acceso total
            if request.user.is_superuser:
                return vista(request, *args, **kwargs)

            # 3. Verificar que el usuario tenga perfil con rol
            try:
                perfil = request.user.perfil
            except Exception:
                messages.error(request, 'Tu usuario no tiene un perfil de rol asignado.')
                return redirect('login')

            # 4. Verificar si el rol del usuario está en los roles permitidos
            if perfil.rol in roles:
                return vista(request, *args, **kwargs)

            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')

        return wrapper
    return decorador
