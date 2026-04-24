"""
Formularios del sistema FAMEL S.A.S.
Incluye validaciones de negocio para cada entidad.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from .models import Producto, MovimientoInventario, Pedido, ItemPedido, Cliente


# ─── HU0: Autenticación ─────────────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión. Extiende el de Django con estilos."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresa tu usuario',
            'autofocus': True,
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
        }),
        label='Contraseña'
    )


# ─── HU1: Productos ──────────────────────────────────────────────────────────

class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos."""

    class Meta:
        model  = Producto
        fields = ['nombre', 'tipo', 'unidad', 'stock_actual', 'stock_minimo', 'descripcion']
        widgets = {
            'nombre':       forms.TextInput(attrs={'placeholder': 'Ej: Tablero 12 circuitos'}),
            'descripcion':  forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional...'}),
            'stock_actual': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_nombre(self):
        """Valida que no existan nombres duplicados (insensible a mayúsculas)."""
        nombre = self.cleaned_data.get('nombre', '').strip()
        qs = Producto.objects.filter(nombre__iexact=nombre, activo=True)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un producto activo con este nombre.')
        return nombre

    def clean_stock_actual(self):
        """Valida que el stock inicial no sea negativo."""
        stock = self.cleaned_data.get('stock_actual', 0)
        if stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock


# ─── HU2: Movimientos de inventario ─────────────────────────────────────────

class MovimientoInventarioForm(forms.ModelForm):
    """Formulario para registrar un movimiento de inventario."""

    class Meta:
        model  = MovimientoInventario
        fields = ['producto', 'tipo', 'cantidad', 'fecha', 'observacion']
        widgets = {
            'fecha':       forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'cantidad':    forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0'}),
            'observacion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ej: Compra proveedor XYZ'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar productos activos en el selector
        self.fields['producto'].queryset = Producto.objects.filter(activo=True).order_by('nombre')
        self.fields['fecha'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        """Valida que las salidas no excedan el stock disponible."""
        cleaned = super().clean()
        tipo     = cleaned.get('tipo')
        cantidad = cleaned.get('cantidad')
        producto = cleaned.get('producto')

        if tipo == 'SALIDA' and cantidad and producto:
            if cantidad > producto.stock_actual:
                raise forms.ValidationError(
                    f'Stock insuficiente. Disponible: {producto.stock_actual} {producto.get_unidad_display()}.'
                )
        return cleaned


# ─── HU5: Clientes ───────────────────────────────────────────────────────────

class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes."""

    class Meta:
        model  = Cliente
        fields = ['nombre', 'nit', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre':    forms.TextInput(attrs={'placeholder': 'Ej: Ferretería El Constructor'}),
            'nit':       forms.TextInput(attrs={'placeholder': 'Ej: 900123456-1'}),
            'telefono':  forms.TextInput(attrs={'placeholder': 'Ej: 3001234567'}),
            'email':     forms.EmailInput(attrs={'placeholder': 'correo@empresa.com'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección o ciudad'}),
        }


# ─── HU5: Pedidos ───────────────────────────────────────────────────────────

class PedidoForm(forms.ModelForm):
    """Formulario para crear un pedido."""

    class Meta:
        model  = Pedido
        fields = ['cliente', 'fecha_entrega', 'observaciones']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej: Entrega en obra, llamar antes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('nombre')
        self.fields['fecha_entrega'].required = False


class ItemPedidoForm(forms.ModelForm):
    """Formulario individual de ítem dentro de un pedido."""

    class Meta:
        model  = ItemPedido
        fields = ['producto', 'cantidad', 'especificacion']
        widgets = {
            'cantidad':       forms.NumberInput(attrs={'step': '1', 'min': '1', 'placeholder': '1'}),
            'especificacion': forms.TextInput(attrs={'placeholder': 'Referencia o nota adicional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True, tipo='PRODUCTO_TERMINADO'
        ).order_by('nombre')
        self.fields['especificacion'].required = False

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad', 0)
        if cantidad and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a cero.')
        return cantidad


# Formset para múltiples ítems en un pedido (mínimo 1, máximo 20)
ItemPedidoFormSet = inlineformset_factory(
    Pedido, ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class ActualizarEstadoForm(forms.ModelForm):
    """Mini-formulario para cambiar el estado de un pedido."""

    class Meta:
        model  = Pedido
        fields = ['estado']
