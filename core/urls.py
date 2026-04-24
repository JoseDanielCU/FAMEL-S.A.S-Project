"""
Rutas URL de la aplicación principal FAMEL S.A.S.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Raíz ────────────────────────────────────────────────────────────────
    path('', views.vista_login, name='root'),

    # ── HU0: Autenticación ──────────────────────────────────────────────────
    path('login/',     views.vista_login,    name='login'),
    path('logout/',    views.vista_logout,   name='logout'),
    path('dashboard/', views.vista_dashboard, name='dashboard'),

    # ── HU1: Productos ───────────────────────────────────────────────────────
    path('productos/',                    views.lista_productos,   name='lista_productos'),
    path('productos/nuevo/',              views.crear_producto,    name='crear_producto'),
    path('productos/<int:pk>/editar/',    views.editar_producto,   name='editar_producto'),
    path('productos/<int:pk>/eliminar/',  views.eliminar_producto, name='eliminar_producto'),

    # ── HU2: Inventario ──────────────────────────────────────────────────────
    path('inventario/',         views.lista_movimientos, name='lista_movimientos'),
    path('inventario/nuevo/',   views.crear_movimiento,  name='crear_movimiento'),

    # ── HU5: Pedidos ─────────────────────────────────────────────────────────
    path('pedidos/',                              views.lista_pedidos,           name='lista_pedidos'),
    path('pedidos/nuevo/',                        views.crear_pedido,            name='crear_pedido'),
    path('pedidos/<int:pk>/',                     views.detalle_pedido,          name='detalle_pedido'),
    path('pedidos/<int:pk>/estado/',              views.actualizar_estado_pedido, name='actualizar_estado_pedido'),

    # ── Clientes ─────────────────────────────────────────────────────────────
    path('clientes/',                   views.lista_clientes,  name='lista_clientes'),
    path('clientes/nuevo/',             views.crear_cliente,   name='crear_cliente'),
    path('clientes/<int:pk>/editar/',   views.editar_cliente,  name='editar_cliente'),
]
