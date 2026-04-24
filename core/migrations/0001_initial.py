"""Migración inicial — crea todas las tablas del sistema FAMEL S.A.S."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # PerfilUsuario
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(
                    choices=[('ADMIN', 'Administrador'), ('VENDEDOR', 'Vendedor'), ('OPERARIO', 'Operario')],
                    default='OPERARIO', max_length=20
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='perfil',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={'verbose_name': 'Perfil de Usuario', 'verbose_name_plural': 'Perfiles de Usuario'},
        ),

        # Cliente
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre',    models.CharField(max_length=200, verbose_name='Nombre / Razón social')),
                ('nit',       models.CharField(blank=True, max_length=30, verbose_name='NIT / Cédula')),
                ('telefono',  models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('email',     models.EmailField(blank=True, verbose_name='Correo electrónico')),
                ('direccion', models.CharField(blank=True, max_length=300, verbose_name='Dirección')),
                ('activo',    models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes', 'ordering': ['nombre']},
        ),

        # Producto
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True, verbose_name='Nombre')),
                ('tipo', models.CharField(
                    choices=[
                        ('PRODUCTO_TERMINADO', 'Producto Terminado'),
                        ('MATERIA_PRIMA', 'Materia Prima'),
                        ('INSUMO', 'Insumo')
                    ],
                    max_length=30, verbose_name='Tipo'
                )),
                ('unidad', models.CharField(
                    choices=[
                        ('UND', 'Unidad'), ('KG', 'Kilogramo'), ('MT', 'Metro'),
                        ('LT', 'Litro'), ('M2', 'Metro cuadrado'), ('CJA', 'Caja')
                    ],
                    default='UND', max_length=10, verbose_name='Unidad de medida'
                )),
                ('stock_actual',   models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Stock actual')),
                ('stock_minimo',   models.DecimalField(decimal_places=2, default=5, max_digits=12, verbose_name='Stock mínimo')),
                ('descripcion',    models.TextField(blank=True, verbose_name='Descripción')),
                ('activo',         models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Producto', 'verbose_name_plural': 'Productos', 'ordering': ['nombre']},
        ),

        # MovimientoInventario
        migrations.CreateModel(
            name='MovimientoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[('ENTRADA', 'Entrada'), ('SALIDA', 'Salida'), ('AJUSTE', 'Ajuste')],
                    max_length=10, verbose_name='Tipo de movimiento'
                )),
                ('cantidad',    models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Cantidad')),
                ('fecha',       models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha y hora')),
                ('observacion', models.TextField(blank=True, verbose_name='Observación')),
                ('producto', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='movimientos', to='core.producto'
                )),
                ('registrado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='movimientos', to=settings.AUTH_USER_MODEL,
                    verbose_name='Registrado por'
                )),
            ],
            options={
                'verbose_name': 'Movimiento de Inventario',
                'verbose_name_plural': 'Movimientos de Inventario',
                'ordering': ['-fecha']
            },
        ),

        # Pedido
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(editable=False, max_length=20, unique=True, verbose_name='N° Pedido')),
                ('estado', models.CharField(
                    choices=[
                        ('PENDIENTE', 'Pendiente'), ('EN_PROCESO', 'En Proceso'),
                        ('LISTO', 'Listo'), ('ENTREGADO', 'Entregado'), ('CANCELADO', 'Cancelado')
                    ],
                    default='PENDIENTE', max_length=20
                )),
                ('fecha_pedido',   models.DateTimeField(auto_now_add=True, verbose_name='Fecha de pedido')),
                ('fecha_entrega',  models.DateField(blank=True, null=True, verbose_name='Entrega estimada')),
                ('observaciones',  models.TextField(blank=True, verbose_name='Observaciones')),
                ('cliente', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='pedidos', to='core.cliente'
                )),
                ('registrado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pedidos', to=settings.AUTH_USER_MODEL,
                    verbose_name='Registrado por'
                )),
            ],
            options={
                'verbose_name': 'Pedido', 'verbose_name_plural': 'Pedidos',
                'ordering': ['-fecha_pedido']
            },
        ),

        # ItemPedido
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad',       models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Cantidad')),
                ('especificacion', models.CharField(blank=True, max_length=300, verbose_name='Especificación / nota')),
                ('pedido', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='core.pedido'
                )),
                ('producto', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT, to='core.producto'
                )),
            ],
            options={'verbose_name': 'Ítem de Pedido', 'verbose_name_plural': 'Ítems de Pedido'},
        ),
    ]
