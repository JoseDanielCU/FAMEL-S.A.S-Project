"""
Vistas del sistema FAMEL S.A.S.
Organizado por Historia de Usuario: HU0, HU1, HU2, HU5.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    Producto, MovimientoInventario, Pedido, ItemPedido, Cliente
)
from .forms import (
    LoginForm, ProductoForm, MovimientoInventarioForm,
    PedidoForm, ItemPedidoFormSet, ClienteForm, ActualizarEstadoForm
)
from .decoradores import rol_requerido


# ════════════════════════════════════════════════════════════════════════════
# HU0 — Autenticación
# ════════════════════════════════════════════════════════════════════════════

def vista_login(request):
    """Pantalla de login. Redirige al dashboard si ya hay sesión activa."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'auth/login.html', {'form': form})


def vista_logout(request):
    """Cierra la sesión y redirige al login."""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required
def vista_dashboard(request):
    """Dashboard principal con métricas y resúmenes por rol."""
    # Métricas generales
    total_productos   = Producto.objects.filter(activo=True).count()
    bajo_stock        = Producto.objects.filter(activo=True, stock_actual__lte=5)
    total_pedidos     = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
    pedidos_en_proceso = Pedido.objects.filter(estado='EN_PROCESO').count()

    # Últimos movimientos y pedidos para el resumen
    ultimos_movimientos = MovimientoInventario.objects.select_related('producto')[:5]
    ultimos_pedidos     = Pedido.objects.select_related('cliente')[:5]

    ctx = {
        'total_productos':    total_productos,
        'bajo_stock':         bajo_stock,
        'total_pedidos':      total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_proceso': pedidos_en_proceso,
        'ultimos_movimientos': ultimos_movimientos,
        'ultimos_pedidos':    ultimos_pedidos,
    }
    return render(request, 'dashboard/dashboard.html', ctx)


# ════════════════════════════════════════════════════════════════════════════
# HU1 — Productos y Materias Primas
# ════════════════════════════════════════════════════════════════════════════

@rol_requerido('ADMIN', 'OPERARIO')
def lista_productos(request):
    """Lista de productos con búsqueda y filtro por tipo."""
    qs = Producto.objects.filter(activo=True)

    busqueda = request.GET.get('q', '').strip()
    tipo     = request.GET.get('tipo', '')

    if busqueda:
        qs = qs.filter(nombre__icontains=busqueda)
    if tipo:
        qs = qs.filter(tipo=tipo)

    ctx = {
        'productos':    qs,
        'busqueda':     busqueda,
        'tipo_filtro':  tipo,
        'tipo_choices': Producto.TIPO_CHOICES,
    }
    return render(request, 'products/lista_productos.html', ctx)


@rol_requerido('ADMIN', 'OPERARIO')
def crear_producto(request):
    """Formulario para registrar un nuevo producto."""
    form = ProductoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Producto "{form.cleaned_data["nombre"]}" creado correctamente.')
        return redirect('lista_productos')

    return render(request, 'products/form_producto.html', {'form': form, 'accion': 'Crear'})


@rol_requerido('ADMIN', 'OPERARIO')
def editar_producto(request, pk):
    """Formulario para editar un producto existente."""
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    form     = ProductoForm(request.POST or None, instance=producto)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Producto "{producto.nombre}" actualizado.')
        return redirect('lista_productos')

    return render(request, 'products/form_producto.html', {
        'form': form, 'producto': producto, 'accion': 'Editar'
    })


@rol_requerido('ADMIN')
def eliminar_producto(request, pk):
    """Soft delete: marca el producto como inactivo."""
    producto = get_object_or_404(Producto, pk=pk, activo=True)

    if request.method == 'POST':
        producto.activo = False
        producto.save()
        messages.success(request, f'Producto "{producto.nombre}" eliminado.')
        return redirect('lista_productos')

    return render(request, 'products/confirmar_eliminar.html', {'producto': producto})


# ════════════════════════════════════════════════════════════════════════════
# HU2 — Movimientos de Inventario
# ════════════════════════════════════════════════════════════════════════════

@rol_requerido('ADMIN', 'OPERARIO')
def lista_movimientos(request):
    """Historial de movimientos con filtros."""
    qs = MovimientoInventario.objects.select_related('producto', 'registrado_por')

    tipo       = request.GET.get('tipo', '')
    producto_id = request.GET.get('producto', '')

    if tipo:
        qs = qs.filter(tipo=tipo)
    if producto_id:
        qs = qs.filter(producto_id=producto_id)

    ctx = {
        'movimientos':     qs[:100],  # Limitar a 100 registros recientes
        'tipo_filtro':     tipo,
        'producto_filtro': producto_id,
        'tipo_choices':    MovimientoInventario.TIPO_CHOICES,
        'productos':       Producto.objects.filter(activo=True).order_by('nombre'),
    }
    return render(request, 'inventory/lista_movimientos.html', ctx)


@rol_requerido('ADMIN', 'OPERARIO')
def crear_movimiento(request):
    """Registra un nuevo movimiento de inventario."""
    # Preseleccionar producto si viene en query param
    initial = {}
    producto_id = request.GET.get('producto')
    if producto_id:
        initial['producto'] = producto_id

    form = MovimientoInventarioForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        movimiento = form.save(commit=False)
        movimiento.registrado_por = request.user
        try:
            movimiento.save()
            messages.success(
                request,
                f'Movimiento registrado: {movimiento.get_tipo_display()} de '
                f'{movimiento.cantidad} {movimiento.producto.get_unidad_display()} '
                f'— {movimiento.producto.nombre}.'
            )
            return redirect('lista_movimientos')
        except Exception as e:
            messages.error(request, f'Error al registrar: {e}')

    return render(request, 'inventory/form_movimiento.html', {'form': form})


# ════════════════════════════════════════════════════════════════════════════
# HU5 — Pedidos de Clientes
# ════════════════════════════════════════════════════════════════════════════

@rol_requerido('ADMIN', 'VENDEDOR')
def lista_pedidos(request):
    """Lista de pedidos con filtro por estado."""
    qs = Pedido.objects.select_related('cliente', 'registrado_por')

    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    ctx = {
        'pedidos':         qs,
        'estado_filtro':   estado,
        'estado_choices':  Pedido.ESTADO_CHOICES,
    }
    return render(request, 'orders/lista_pedidos.html', ctx)


@rol_requerido('ADMIN', 'VENDEDOR')
def detalle_pedido(request, pk):
    """Vista de detalle de un pedido con posibilidad de actualizar estado."""
    pedido = get_object_or_404(Pedido, pk=pk)
    estado_form = ActualizarEstadoForm(instance=pedido)

    ctx = {
        'pedido':      pedido,
        'items':       pedido.items.select_related('producto'),
        'estado_form': estado_form,
    }
    return render(request, 'orders/detalle_pedido.html', ctx)


@rol_requerido('ADMIN', 'VENDEDOR')
def crear_pedido(request):
    """Crear un pedido con múltiples ítems usando formset."""
    form    = PedidoForm(request.POST or None)
    formset = ItemPedidoFormSet(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            pedido = form.save(commit=False)
            pedido.registrado_por = request.user
            pedido.estado = 'PENDIENTE'
            pedido.save()

            # Asignar el pedido al formset y guardar ítems
            formset.instance = pedido
            formset.save()

            messages.success(request, f'Pedido {pedido.numero} creado correctamente.')
            return redirect('detalle_pedido', pk=pedido.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    ctx = {
        'form':    form,
        'formset': formset,
    }
    return render(request, 'orders/form_pedido.html', ctx)


@rol_requerido('ADMIN', 'VENDEDOR')
def actualizar_estado_pedido(request, pk):
    """Actualiza únicamente el estado de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == 'POST':
        form = ActualizarEstadoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado actualizado a: {pedido.get_estado_display()}.')
        else:
            messages.error(request, 'Estado no válido.')

    return redirect('detalle_pedido', pk=pk)


# ─── Clientes ────────────────────────────────────────────────────────────────

@rol_requerido('ADMIN', 'VENDEDOR')
def lista_clientes(request):
    """Lista de clientes registrados."""
    clientes = Cliente.objects.filter(activo=True)
    q = request.GET.get('q', '').strip()
    if q:
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(nit__icontains=q))
    return render(request, 'orders/lista_clientes.html', {
        'clientes': clientes, 'busqueda': q
    })


@rol_requerido('ADMIN', 'VENDEDOR')
def crear_cliente(request):
    """Formulario para registrar un nuevo cliente."""
    form = ClienteForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Cliente "{form.cleaned_data["nombre"]}" registrado.')
        return redirect('lista_clientes')

    return render(request, 'orders/form_cliente.html', {'form': form, 'accion': 'Crear'})


@rol_requerido('ADMIN', 'VENDEDOR')
def editar_cliente(request, pk):
    """Editar datos de un cliente."""
    cliente = get_object_or_404(Cliente, pk=pk, activo=True)
    form    = ClienteForm(request.POST or None, instance=cliente)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Cliente "{cliente.nombre}" actualizado.')
        return redirect('lista_clientes')

    return render(request, 'orders/form_cliente.html', {
        'form': form, 'cliente': cliente, 'accion': 'Editar'
    })
