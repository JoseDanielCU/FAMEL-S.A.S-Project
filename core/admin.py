"""Configuración del panel de administración Django para FAMEL S.A.S."""
from django.contrib import admin
from .models import PerfilUsuario, Cliente, Producto, MovimientoInventario, Pedido, ItemPedido

admin.site.site_header  = 'FAMEL S.A.S — Administración'
admin.site.site_title   = 'FAMEL Admin'
admin.site.index_title  = 'Panel de administración'


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display  = ['user', 'rol']
    list_filter   = ['rol']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'nit', 'telefono', 'email', 'activo']
    list_filter   = ['activo']
    search_fields = ['nombre', 'nit']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'tipo', 'unidad', 'stock_actual', 'stock_minimo', 'activo']
    list_filter   = ['tipo', 'activo']
    search_fields = ['nombre']


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display  = ['producto', 'tipo', 'cantidad', 'fecha', 'registrado_por']
    list_filter   = ['tipo']
    search_fields = ['producto__nombre']
    readonly_fields = ['fecha']


class ItemPedidoInline(admin.TabularInline):
    model  = ItemPedido
    extra  = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display  = ['numero', 'cliente', 'estado', 'fecha_pedido', 'registrado_por']
    list_filter   = ['estado']
    search_fields = ['numero', 'cliente__nombre']
    inlines       = [ItemPedidoInline]
    readonly_fields = ['numero', 'fecha_pedido']
