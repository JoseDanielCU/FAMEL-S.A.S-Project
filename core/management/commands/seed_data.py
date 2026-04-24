"""
Comando de gestión: carga datos de prueba para FAMEL S.A.S.
Uso: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import PerfilUsuario, Cliente, Producto, MovimientoInventario, Pedido, ItemPedido


class Command(BaseCommand):
    help = 'Carga usuarios, productos, clientes y pedidos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write('⚙️  Cargando datos de prueba...\n')

        # ── Usuarios ──────────────────────────────────────────────────────────
        usuarios = [
            ('admin',     'famel2026', 'Admin',    'FAMEL',      'ADMIN',    True),
            ('vendedor1', 'famel2026', 'Carlos',   'Gómez',      'VENDEDOR', False),
            ('operario1', 'famel2026', 'Ana',      'Martínez',   'OPERARIO', False),
        ]

        for username, password, first, last, rol, is_staff in usuarios:
            user, created = User.objects.get_or_create(username=username)
            if created or not hasattr(user, 'perfil'):
                user.set_password(password)
                user.first_name = first
                user.last_name  = last
                user.is_staff   = is_staff
                user.save()
                PerfilUsuario.objects.get_or_create(user=user, defaults={'rol': rol})
                self.stdout.write(f'  ✅ Usuario creado: {username} ({rol})')
            else:
                self.stdout.write(f'  ↩️  Usuario ya existe: {username}')

        # ── Productos ─────────────────────────────────────────────────────────
        productos_data = [
            ('Tablero 12 circuitos',  'PRODUCTO_TERMINADO', 'UND', 12, 3, 'Tablero monofásico certificado RETIE'),
            ('Tablero 24 circuitos',  'PRODUCTO_TERMINADO', 'UND',  6, 3, 'Tablero trifásico'),
            ('Caja metálica 20x30',   'PRODUCTO_TERMINADO', 'UND', 20, 5, 'Caja de empalme galvanizada'),
            ('Lámina calibre 16',     'MATERIA_PRIMA',      'KG', 600, 50, 'Lámina de acero cold rolled'),
            ('Cable AWG #12',         'MATERIA_PRIMA',      'MT',   4, 10, 'Cable eléctrico calibre 12'),
            ('Pintura epóxica gris',  'INSUMO',             'LT',  30, 10, 'Pintura para acabado interior'),
            ('Tornillo M4x10',        'INSUMO',             'CJA', 80, 20, 'Tornillos autorroscantes'),
            ('Riel DIN 35mm',         'MATERIA_PRIMA',      'MT',  50, 10, 'Riel para montaje de breakers'),
        ]

        for nombre, tipo, unidad, stock, minimo, desc in productos_data:
            p, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'tipo': tipo, 'unidad': unidad,
                    'stock_actual': stock, 'stock_minimo': minimo,
                    'descripcion': desc
                }
            )
            if created:
                self.stdout.write(f'  ✅ Producto: {nombre}')

        # ── Clientes ──────────────────────────────────────────────────────────
        clientes_data = [
            ('Ferretería El Constructor', '900123456-1', '3001234567', 'compras@elconstructor.com', 'Medellín'),
            ('Electro Obras S.A.S',       '811456789-2', '3109876543', 'pedidos@electroobras.co',   'Bogotá'),
            ('Construmax Ltda.',          '700654321-0', '6044567890', 'info@construmax.com',        'Cali'),
        ]

        for nombre, nit, tel, email, dir_ in clientes_data:
            c, created = Cliente.objects.get_or_create(
                nombre=nombre,
                defaults={'nit': nit, 'telefono': tel, 'email': email, 'direccion': dir_}
            )
            if created:
                self.stdout.write(f'  ✅ Cliente: {nombre}')

        # ── Movimientos de inventario ─────────────────────────────────────────
        admin_user = User.objects.get(username='admin')
        tablero12  = Producto.objects.get(nombre='Tablero 12 circuitos')
        lamina     = Producto.objects.get(nombre='Lámina calibre 16')

        if not MovimientoInventario.objects.exists():
            MovimientoInventario.objects.create(
                producto=tablero12, tipo='ENTRADA', cantidad=5,
                observacion='Producción semanal', registrado_por=admin_user
            )
            MovimientoInventario.objects.create(
                producto=lamina, tipo='ENTRADA', cantidad=200,
                observacion='Compra proveedor Aceros del Norte', registrado_por=admin_user
            )
            MovimientoInventario.objects.create(
                producto=tablero12, tipo='SALIDA', cantidad=3,
                observacion='Despacho cliente Ferretería', registrado_por=admin_user
            )
            self.stdout.write('  ✅ Movimientos de inventario creados')

        # ── Pedidos ───────────────────────────────────────────────────────────
        vendedor = User.objects.get(username='vendedor1')
        cliente1 = Cliente.objects.get(nombre='Ferretería El Constructor')
        cliente2 = Cliente.objects.get(nombre='Electro Obras S.A.S')
        caja     = Producto.objects.get(nombre='Caja metálica 20x30')

        if not Pedido.objects.exists():
            from django.utils import timezone
            from datetime import timedelta

            p1 = Pedido.objects.create(
                cliente=cliente1, estado='PENDIENTE',
                fecha_entrega=(timezone.now() + timedelta(days=21)).date(),
                observaciones='Entrega en obra, llamar antes',
                registrado_por=vendedor
            )
            ItemPedido.objects.create(pedido=p1, producto=tablero12, cantidad=5)
            ItemPedido.objects.create(pedido=p1, producto=caja,      cantidad=10)

            p2 = Pedido.objects.create(
                cliente=cliente2, estado='EN_PROCESO',
                fecha_entrega=(timezone.now() + timedelta(days=10)).date(),
                observaciones='Urgente',
                registrado_por=vendedor
            )
            ItemPedido.objects.create(pedido=p2, producto=tablero12, cantidad=2)

            p3 = Pedido.objects.create(
                cliente=cliente1, estado='ENTREGADO',
                registrado_por=vendedor
            )
            ItemPedido.objects.create(pedido=p3, producto=caja, cantidad=15)

            self.stdout.write('  ✅ Pedidos de prueba creados')

        self.stdout.write(self.style.SUCCESS(
            '\n🎉 Datos de prueba cargados correctamente.\n'
            '   Servidor: python manage.py runserver\n'
            '   URL:      http://127.0.0.1:8000/\n'
        ))
