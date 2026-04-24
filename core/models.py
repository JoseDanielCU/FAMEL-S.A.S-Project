"""
Modelos del sistema FAMEL S.A.S.
Entidades: PerfilUsuario, Cliente, Producto, MovimientoInventario, Pedido, ItemPedido
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


# ─── HU0: Roles de usuario ──────────────────────────────────────────────────

class PerfilUsuario(models.Model):
    """Extiende User de Django para agregar rol."""

    ROL_CHOICES = [
        ('ADMIN',    'Administrador'),
        ('VENDEDOR', 'Vendedor'),
        ('OPERARIO', 'Operario'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol  = models.CharField(max_length=20, choices=ROL_CHOICES, default='OPERARIO')

    class Meta:
        verbose_name        = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f'{self.user.username} — {self.get_rol_display()}'


# ─── HU5: Clientes ──────────────────────────────────────────────────────────

class Cliente(models.Model):
    """Cliente que realiza pedidos."""

    nombre    = models.CharField(max_length=200, verbose_name='Nombre / Razón social')
    nit       = models.CharField(max_length=30,  verbose_name='NIT / Cédula', blank=True)
    telefono  = models.CharField(max_length=20,  verbose_name='Teléfono',     blank=True)
    email     = models.EmailField(blank=True,     verbose_name='Correo electrónico')
    direccion = models.CharField(max_length=300,  verbose_name='Dirección',   blank=True)
    activo    = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre


# ─── HU1: Productos y materias primas ───────────────────────────────────────

class Producto(models.Model):
    """Producto terminado o materia prima."""

    TIPO_CHOICES = [
        ('PRODUCTO_TERMINADO', 'Producto Terminado'),
        ('MATERIA_PRIMA',      'Materia Prima'),
        ('INSUMO',             'Insumo'),
    ]

    UNIDAD_CHOICES = [
        ('UND', 'Unidad'),
        ('KG',  'Kilogramo'),
        ('MT',  'Metro'),
        ('LT',  'Litro'),
        ('M2',  'Metro cuadrado'),
        ('CJA', 'Caja'),
    ]

    nombre          = models.CharField(max_length=200, unique=True, verbose_name='Nombre')
    tipo            = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo')
    unidad          = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='UND', verbose_name='Unidad de medida')
    stock_actual    = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock actual')
    stock_minimo    = models.DecimalField(max_digits=12, decimal_places=2, default=5,  verbose_name='Stock mínimo')
    descripcion     = models.TextField(blank=True, verbose_name='Descripción')
    activo          = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def bajo_stock(self):
        """True si el stock actual está en o por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo


# ─── HU2: Movimientos de inventario ─────────────────────────────────────────

class MovimientoInventario(models.Model):
    """Registra entradas, salidas y ajustes de stock."""

    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA',  'Salida'),
        ('AJUSTE',  'Ajuste'),
    ]

    producto      = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo          = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo de movimiento')
    cantidad      = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cantidad')
    fecha         = models.DateTimeField(default=timezone.now, verbose_name='Fecha y hora')
    observacion   = models.TextField(blank=True, verbose_name='Observación')
    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='movimientos', verbose_name='Registrado por'
    )

    class Meta:
        verbose_name        = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering            = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.producto.nombre} · {self.cantidad}'

    def clean(self):
        """Validación: no permitir salidas sin stock suficiente."""
        if self.tipo == 'SALIDA' and self.cantidad > self.producto.stock_actual:
            raise ValidationError(
                f'Stock insuficiente. Disponible: {self.producto.stock_actual} {self.producto.unidad}.'
            )
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')

    def save(self, *args, **kwargs):
        """
        Al guardar, actualiza automáticamente el stock del producto.
        - ENTRADA: suma al stock
        - SALIDA:  resta del stock
        - AJUSTE:  fija el stock al valor indicado
        """
        self.full_clean()  # Ejecuta validaciones antes de guardar

        if self.tipo == 'ENTRADA':
            self.producto.stock_actual += self.cantidad
        elif self.tipo == 'SALIDA':
            self.producto.stock_actual -= self.cantidad
        elif self.tipo == 'AJUSTE':
            self.producto.stock_actual = self.cantidad

        self.producto.save()
        super().save(*args, **kwargs)


# ─── HU5: Pedidos ───────────────────────────────────────────────────────────

class Pedido(models.Model):
    """Pedido realizado por un cliente."""

    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('EN_PROCESO',  'En Proceso'),
        ('LISTO',       'Listo'),
        ('ENTREGADO',   'Entregado'),
        ('CANCELADO',   'Cancelado'),
    ]

    numero          = models.CharField(max_length=20, unique=True, verbose_name='N° Pedido', editable=False)
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_pedido    = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de pedido')
    fecha_entrega   = models.DateField(null=True, blank=True, verbose_name='Entrega estimada')
    observaciones   = models.TextField(blank=True, verbose_name='Observaciones')
    registrado_por  = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pedidos', verbose_name='Registrado por'
    )

    class Meta:
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering            = ['-fecha_pedido']

    def __str__(self):
        return f'{self.numero} — {self.cliente.nombre}'

    def save(self, *args, **kwargs):
        """Genera número de pedido automático tipo PED-0001."""
        if not self.numero:
            ultimo = Pedido.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            self.numero = f'PED-{siguiente:04d}'
        super().save(*args, **kwargs)

    @property
    def estado_color(self):
        """Clase CSS según estado para colorear la etiqueta."""
        colores = {
            'PENDIENTE':  'yellow',
            'EN_PROCESO': 'blue',
            'LISTO':      'green',
            'ENTREGADO':  'teal',
            'CANCELADO':  'red',
        }
        return colores.get(self.estado, 'muted')


class ItemPedido(models.Model):
    """Ítem (línea de producto) dentro de un pedido."""

    pedido         = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto       = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad       = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cantidad')
    especificacion = models.CharField(max_length=300, blank=True, verbose_name='Especificación / nota')

    class Meta:
        verbose_name        = 'Ítem de Pedido'
        verbose_name_plural = 'Ítems de Pedido'

    def __str__(self):
        return f'{self.pedido.numero} · {self.producto.nombre} × {self.cantidad}'
