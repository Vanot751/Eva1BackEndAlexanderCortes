from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import ProductoAdmin, RangoStockFilter
from .models import Cliente, DetalleVenta, Producto, Venta
from .views import validar_rut


class InventarioTests(TestCase):
	# Cada prueba obtiene una base temporal y un producto inicial independiente.
	def setUp(self):
		self.producto = Producto.objects.create(
			codigo='TEST-001', nombre='Producto de prueba', precio=500, stock=4
		)

	def test_carga_de_pantallas_principales(self):
		# Comprueba que las URLs GET principales rendericen sin errores de plantilla.
		for nombre_url in ('producto_list', 'venta_create', 'venta_list', 'cliente_list', 'cliente_create'):
			with self.subTest(nombre_url=nombre_url):
				self.assertEqual(self.client.get(reverse(nombre_url)).status_code, 200)

	def test_productos_no_se_pueden_crear_desde_el_sitio_publico(self):
		self.assertEqual(self.client.get('/productos/nuevo/').status_code, 404)

	def test_valida_rut_chileno(self):
		# Contrasta un RUT válido con otro cuyo dígito verificador es incorrecto.
		self.assertTrue(validar_rut('12.345.678-5'))
		self.assertFalse(validar_rut('12.345.678-6'))

	def test_registra_venta_y_descuenta_stock(self):
		# Comprueba que vender crea los registros correctos y reduce las existencias.
		producto = Producto.objects.create(codigo='A-002', nombre='Leche', precio=1200, stock=5)

		response = self.client.post(reverse('venta_create'), {
			'cliente_rut': '12.345.678-5',
			'producto_1': producto.pk,
			'cantidad_1': 2,
		})

		self.assertRedirects(response, reverse('venta_list'))
		producto.refresh_from_db()
		self.assertEqual(producto.stock, 3)
		self.assertEqual(Venta.objects.count(), 1)
		self.assertEqual(DetalleVenta.objects.get().cantidad, 2)
		self.assertEqual(Venta.objects.get().rut_cliente, '12.345.678-5')
		self.assertEqual(Cliente.objects.count(), 0)

	def test_filtro_rango_stock(self):
		# Verifica que el filtro avanzado segmente correctamente los productos por stock.
		Producto.objects.create(codigo='P-SIN', nombre='Sin stock', precio=100, stock=0)
		Producto.objects.create(codigo='P-BAJO', nombre='Stock bajo', precio=100, stock=5)
		Producto.objects.create(codigo='P-MEDIO', nombre='Stock medio', precio=100, stock=20)
		Producto.objects.create(codigo='P-ALTO', nombre='Stock alto', precio=100, stock=60)

		model_admin = ProductoAdmin(Producto, site)

		# Filtro sin stock
		filtro_sin = RangoStockFilter(None, {'stock': ['sin']}, Producto, model_admin)
		qs_sin = filtro_sin.queryset(None, Producto.objects.all())
		self.assertTrue(qs_sin.filter(codigo='P-SIN').exists())
		self.assertFalse(qs_sin.filter(codigo='P-BAJO').exists())

		# Filtro stock bajo
		filtro_bajo = RangoStockFilter(None, {'stock': ['bajo']}, Producto, model_admin)
		qs_bajo = filtro_bajo.queryset(None, Producto.objects.all())
		self.assertTrue(qs_bajo.filter(codigo='P-BAJO').exists())
		self.assertFalse(qs_bajo.filter(codigo='P-SIN').exists())

		# Filtro stock medio
		filtro_medio = RangoStockFilter(None, {'stock': ['medio']}, Producto, model_admin)
		qs_medio = filtro_medio.queryset(None, Producto.objects.all())
		self.assertTrue(qs_medio.filter(codigo='P-MEDIO').exists())
		self.assertFalse(qs_medio.filter(codigo='P-BAJO').exists())

		# Filtro stock alto
		filtro_alto = RangoStockFilter(None, {'stock': ['alto']}, Producto, model_admin)
		qs_alto = filtro_alto.queryset(None, Producto.objects.all())
		self.assertTrue(qs_alto.filter(codigo='P-ALTO').exists())
		self.assertFalse(qs_alto.filter(codigo='P-MEDIO').exists())

	def test_admin_guarda_edicion_de_producto_desde_lista(self):
		# Verifica la edición masiva mediante el formset estándar de list_editable.
		usuario = get_user_model().objects.create_superuser(
			username='admin', email='admin@example.com', password='segura-123'
		)
		self.client.force_login(usuario)
		producto = Producto.objects.create(
			codigo='EDIT-001', nombre='Nombre original', precio=100, stock=2,
			descripcion='Descripción original'
		)

		response = self.client.post(
			reverse('admin:inventario_producto_changelist'),
			{
				'form-TOTAL_FORMS': '1',
				'form-INITIAL_FORMS': '1',
				'form-MIN_NUM_FORMS': '0',
				'form-MAX_NUM_FORMS': '1000',
				'form-0-id': str(producto.pk),
				'form-0-nombre': 'Nombre actualizado',
				'form-0-descripcion': 'Descripción actualizada',
				'form-0-precio': '250',
				'form-0-stock': '8',
				'_save': 'Guardar',
			},
		)

		self.assertEqual(response.status_code, 302)
		producto.refresh_from_db()
		self.assertEqual(producto.nombre, 'Nombre actualizado')
		self.assertEqual(producto.descripcion, 'Descripción actualizada')
		self.assertEqual(producto.precio, 250)
		self.assertEqual(producto.stock, 8)
