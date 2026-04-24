# FAMEL S.A.S — Sistema de Gestión de Inventario y Pedidos
### Sprint 1 · Sistemas de Información · Universidad EAFIT 2026

> Sistema web desarrollado en **Django 4.2** para gestionar productos, movimientos de inventario, pedidos de clientes y autenticación por roles. Resuelve la desarticulación entre inventario, producción y ventas de la empresa FAMEL S.A.S.

---

## ✅ Historias de Usuario implementadas

| HU | Descripción | Estado |
|----|-------------|--------|
| **HU0** | Autenticación y control de acceso por roles | ✅ Completa |
| **HU1** | Registro, edición y eliminación de productos/materias primas | ✅ Completa |
| **HU2** | Registro de entradas y salidas de inventario con historial | ✅ Completa |
| **HU5** | Registro de pedidos de clientes con múltiples productos | ✅ Completa |

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.9+ · Django 4.2 |
| Base de datos | SQLite (incluido con Django) |
| Frontend | Django Templates · HTML5 · CSS3 (custom) |
| Fuentes | DM Sans · Space Mono (Google Fonts) |
| Autenticación | Django Auth (sesiones, hashing seguro) |

---

## 📋 Requisitos previos

- **Python 3.9 o superior** instalado
- **pip** (incluido con Python)
- Conexión a internet (solo para cargar fuentes de Google Fonts en el navegador)

---

## 🚀 Instalación paso a paso

### 1. Clonar / descomprimir el proyecto

```bash
git clone <url-repositorio>
cd famel_sprint1
```

### 2. Crear entorno virtual (recomendado)

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones (crea la base de datos SQLite)

```bash
python manage.py migrate
```

### 5. Cargar datos de prueba

```bash
python manage.py seed_data
```

Esto crea automáticamente:
- 3 usuarios con roles (admin, vendedor1, operario1)
- 8 productos de ejemplo
- 3 clientes
- Movimientos de inventario de muestra
- 3 pedidos con ítems

### 6. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

### 7. Abrir en el navegador

```
http://127.0.0.1:8000/
```

---

## 🔑 Credenciales de prueba

| Usuario | Contraseña | Rol | Acceso |
|---------|-----------|-----|--------|
| `admin` | `famel2026` | Administrador | Todo el sistema + panel admin Django |
| `vendedor1` | `famel2026` | Vendedor | Pedidos, Clientes, Dashboard |
| `operario1` | `famel2026` | Operario | Productos, Inventario, Dashboard |

**Panel de administración Django:**
```
http://127.0.0.1:8000/admin/
```
*(Accesible con usuario `admin`)*

---

## 🗂️ Estructura del proyecto

```
famel_sprint1/
│
├── manage.py                       # Punto de entrada Django
├── requirements.txt                # Solo Django 4.2.9
├── famel_db.sqlite3                # BD creada al migrar
│
├── famel/                          # Configuración del proyecto
│   ├── settings.py                 # Configuración principal
│   ├── urls.py                     # URLs raíz
│   └── wsgi.py
│
├── core/                           # Aplicación principal
│   ├── models.py                   # PerfilUsuario, Cliente, Producto,
│   │                               # MovimientoInventario, Pedido, ItemPedido
│   ├── views.py                    # Vistas para HU0, HU1, HU2, HU5
│   ├── forms.py                    # Formularios con validaciones de negocio
│   ├── urls.py                     # Rutas de la app
│   ├── admin.py                    # Panel admin configurado
│   ├── decoradores.py              # @rol_requerido — control de acceso
│   └── management/
│       └── commands/
│           └── seed_data.py        # Datos de prueba
│
├── templates/                      # Plantillas HTML
│   ├── base.html                   # Layout con sidebar y navegación
│   ├── auth/
│   │   └── login.html              # Pantalla de login (HU0)
│   ├── dashboard/
│   │   └── dashboard.html          # Dashboard con métricas
│   ├── products/                   # HU1 — Gestión de productos
│   │   ├── lista_productos.html
│   │   ├── form_producto.html
│   │   └── confirmar_eliminar.html
│   ├── inventory/                  # HU2 — Movimientos
│   │   ├── lista_movimientos.html
│   │   └── form_movimiento.html
│   └── orders/                     # HU5 — Pedidos y clientes
│       ├── lista_pedidos.html
│       ├── form_pedido.html
│       ├── detalle_pedido.html
│       ├── lista_clientes.html
│       └── form_cliente.html
│
└── static/
    └── css/
        └── main.css                # Estilos del sistema (dark theme + naranja FAMEL)
```

---

## 🧩 Funcionalidades implementadas

### HU0 — Autenticación
- Login con usuario y contraseña, sesión persistente
- Mensaje de error en credenciales incorrectas
- Logout funcional
- Sidebar y menú adaptado según rol (Admin / Vendedor / Operario)
- Decorador `@rol_requerido` protege cada vista

### HU1 — Productos y Materias Primas
- Crear, editar, eliminar (soft delete) productos
- Campos: nombre, tipo, unidad, cantidad inicial, descripción, stock mínimo
- Validación de nombres duplicados (case-insensitive)
- Alerta visual para productos con bajo stock
- Filtros por tipo y búsqueda por nombre

### HU2 — Movimientos de Inventario
- Registro de Entradas, Salidas y Ajustes
- **Actualización automática del stock** al guardar (`model.save()`)
- Validación: no permite salidas si el stock es insuficiente
- Historial con filtros por tipo y producto
- Registro del usuario responsable

### HU5 — Pedidos de Clientes
- Crear pedidos con uno o varios productos (formset dinámico con JS)
- Gestión de clientes vinculados al pedido
- Estado del pedido: Pendiente → En Proceso → Listo → Entregado
- Número de pedido generado automáticamente (PED-0001, PED-0002…)
- Vista de detalle con todos los ítems y actualización de estado

---

## ⚙️ Comandos útiles

```bash
# Crear superusuario adicional
python manage.py createsuperuser

# Volver a cargar datos de prueba (BD debe estar limpia)
python manage.py seed_data

# Crear nuevas migraciones tras cambios en models.py
python manage.py makemigrations
python manage.py migrate

# Abrir shell interactivo de Django
python manage.py shell
```

---

## 📐 Arquitectura (MTV)

El proyecto sigue el patrón **MTV (Model-Template-View)** de Django:

- **Model** (`models.py`): Entidades de negocio con lógica de stock automático
- **Template** (`templates/`): HTML con herencia de `base.html`, sidebar reactivo al rol
- **View** (`views.py`): Lógica de negocio, validaciones y respuestas HTTP
- **Forms** (`forms.py`): Validación de datos con reglas de negocio
- **Decoradores** (`decoradores.py`): Control de acceso por rol, separado de la lógica de negocio

---

## 🎨 Diseño

- Tema oscuro (`#0f1117`) con acento naranja FAMEL (`#E85D1A`)
- Tipografía: DM Sans (UI) + Space Mono (datos numéricos y códigos)
- Sin dependencias externas de CSS (Bootstrap, etc.) — estilos propios en `main.css`
- Responsive básico para pantallas menores a 768px

---

*FAMEL S.A.S · Castañeda · Echeverri · Caballero · Gallo · Alzate · EAFIT 2026*
