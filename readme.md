# Eva 1 - Backend de inventario y ventas

Aplicación web desarrollada con **Django** para administrar el inventario de una tienda,
sus clientes y el registro de ventas. El proyecto utiliza PostgreSQL como base de datos
y cuenta con el panel administrativo de Django para las tareas de gestión.

## Funcionalidades principales

- Listar, consultar, editar y eliminar productos.
- Generar códigos de producto automáticamente con el formato `PROD-0001`.
- Administrar clientes habituales con RUT, datos de contacto y estado de habitualidad.
- Registrar ventas asociadas a un cliente habitual o a un comprador ocasional.
- Validar el RUT chileno mediante módulo 11.
- Registrar varias líneas por venta y conservar el precio aplicado en cada detalle.
- Descontar stock automáticamente al confirmar una venta.
- Revertir la operación completa si una validación de la venta falla, mediante
  transacciones de Django.
- Servir archivos estáticos con WhiteNoise.

## Tecnologías

- Python
- Django
- PostgreSQL
- Supabase como servicio de base de datos PostgreSQL utilizado por el proyecto
- `psycopg2-binary`
- `python-dotenv`
- WhiteNoise

Las dependencias se encuentran en [`requirements.txt`](requirements.txt).

## Requisitos previos

- Python 3 instalado.
- Acceso a una base de datos PostgreSQL.
- Git (opcional, para clonar el repositorio).
- Visual Studio Code (opcional, recomendado para desarrollo).

## Instalación y configuración

1. Crear y activar un entorno virtual:

   ```bash
   python -m venv .venv
   ```

   En Windows PowerShell, el entorno puede activarse con:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar las dependencias del proyecto:

   ```bash
   pip install -r requirements.txt
   ```

   > **Nota:** Django ya está incluido en `requirements.txt`. El siguiente comando
   > se conserva por compatibilidad con la configuración original del proyecto:

   ```bash
   pip install django
   ```

3. Configurar la conexión a la instancia de PostgreSQL proporcionada por Supabase
   mediante variables de entorno, según lo indicado en
   [`mi_proyecto/settings.py`](mi_proyecto/settings.py). No se deben publicar
   contraseñas, claves, URLs privadas ni otros datos de conexión en el repositorio.

4. Crear y aplicar las migraciones:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Crear un usuario para acceder al panel administrativo:

   ```bash
   python manage.py createsuperuser
   ```

6. Recopilar los archivos estáticos cuando sea necesario:

   ```bash
   python manage.py collectstatic
   ```

## Ejecución local

Para iniciar el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

> Actualmente este comando **no se utiliza en el flujo habitual**, pero se conserva
> porque forma parte de los comandos originales del proyecto.

Una vez iniciado, las rutas principales estarán disponibles en:

- `http://127.0.0.1:8000/` - listado de productos.
- `http://127.0.0.1:8000/productos/` - administración de productos.
- `http://127.0.0.1:8000/clientes/` - listado de clientes.
- `http://127.0.0.1:8000/ventas/` - listado de ventas.
- `http://127.0.0.1:8000/admin/` - panel administrativo de Django.

## Estructura del proyecto

```text
.
├── inventario/             # Aplicación de productos, clientes y ventas
│   ├── models.py           # Modelos Producto, Cliente, Venta y DetalleVenta
│   ├── views.py            # Vistas y reglas del flujo de ventas
│   ├── forms.py            # Formularios de la aplicación
│   ├── urls.py             # Rutas de inventario
│   ├── templates/          # Plantillas HTML
│   └── migrations/         # Historial de cambios de la base de datos
├── mi_proyecto/            # Configuración principal de Django
├── manage.py               # Utilidad de administración del proyecto
├── requirements.txt        # Dependencias de Python
└── staticfiles/             # Archivos estáticos recopilados
```

## Modelo de datos

- **Producto:** código, nombre, precio, descripción y stock.
- **Cliente:** RUT, nombre, correo, teléfono y si es cliente habitual.
- **Venta:** cliente relacionado opcionalmente, RUT de la boleta, fecha y total.
- **DetalleVenta:** producto vendido, cantidad y precio unitario utilizado.

El precio unitario se guarda en el detalle para conservar el valor histórico de una
venta aunque el precio del producto cambie posteriormente.

## Comandos útiles

### Actualizar Visual Studio Code en equipos de INACAP

El siguiente comando se conserva para los ordenadores de INACAP y debe ejecutarse
desde la CMD cuando se necesite actualizar Visual Studio Code:

```cmd
winget install Microsoft.VisualStudioCode --force
```

### Flujo recomendado después de cambiar modelos

```bash
python manage.py makemigrations
python manage.py migrate
```

## Consideraciones de seguridad

- Mantener las credenciales de PostgreSQL y las claves secretas fuera del control de
  versiones.
- Usar `DEBUG = False` y una lista de hosts autorizados en entornos productivos.
- Ejecutar las operaciones destructivas de productos mediante las vistas protegidas
  con CSRF.
- No exponer el panel `/admin/` públicamente sin autenticación y medidas adicionales
  de protección.
