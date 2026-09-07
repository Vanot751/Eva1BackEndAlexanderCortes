from django.test import TestCase
from django.urls import reverse

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
		for nombre_url in ('producto_list', 'producto_create', 'venta_create', 'venta_list', 'cliente_list', 'cliente_create'):
			with self.subTest(nombre_url=nombre_url):
				self.assertEqual(self.client.get(reverse(nombre_url)).status_code, 200)

	def test_valida_rut_chileno(self):
		# Contrasta un RUT válido con otro cuyo dígito verificador es incorrecto.
		self.assertTrue(validar_rut('12.345.678-5'))
		self.assertFalse(validar_rut('12.345.678-6'))

	def test_crea_producto_con_codigo(self):
		# Verifica el flujo POST completo de alta y redirección del producto.
		response = self.client.post(reverse('producto_create'), {
			'codigo': 'A-001',
			'nombre': 'Pan',
			'precio': 1000,
			'descripcion': 'Pan corriente',
			'stock': 10,
		})

		self.assertRedirects(response, reverse('producto_list'))
		self.assertEqual(Producto.objects.get(codigo='A-001').stock, 10)

	def test_crea_producto_codigo_automatico(self):
		# Verifica que al registrar sin código se asigne automáticamente (ej: PROD-0001).
		response = self.client.post(reverse('producto_create'), {
			'nombre': 'Jugo de Naranja',
			'precio': 1500,
			'descripcion': 'Jugo natural 1L',
			'stock': 15,
		})

		self.assertRedirects(response, reverse('producto_list'))
		producto = Producto.objects.get(nombre='Jugo de Naranja')
		self.assertEqual(producto.stock, 15)
		self.assertTrue(producto.codigo.startswith('PROD-'))

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
