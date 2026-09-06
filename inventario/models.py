from django.db import models

# Los modelos representan las entidades persistentes del inventario y del proceso
# de venta. Django convierte cada clase en una tabla y cada atributo en una columna.
class Producto(models.Model): 
    # El código identifica el producto de forma única para evitar duplicados.
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=64) 
    precio = models.IntegerField(default=0) 
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    stock =  models.IntegerField(default=0)

class Cliente(models.Model):
    # Un cliente puede ser habitual o quedar sin registro cuando solo compra con RUT.
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=80)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_habitual = models.BooleanField(default=False)

    def __str__(self):
        # Esta representación se usa en el panel de administración y en formularios.
        return f"{self.nombre} ({self.rut})"

class Venta(models.Model):
    # cliente relaciona la venta con un habitual; rut_cliente conserva el RUT de la boleta
    # incluso cuando el comprador ocasional no tiene un registro de Cliente.
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    rut_cliente = models.CharField(max_length=12)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        # Facilita reconocer cada venta en consultas, administración y mensajes.
        return f"Venta #{self.id} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    # Cada detalle conecta una venta con un producto y conserva el precio aplicado
    # en ese momento, aunque el precio del producto cambie después.
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        # Calcula el importe de una línea sin almacenarlo duplicadamente en la base.
        return self.cantidad * self.precio_unitario