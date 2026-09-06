from django.db import models

# Create your models here.
class Producto(models.Model): 
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=64) 
    precio = models.IntegerField(default=0) 
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    stock =  models.IntegerField(default=0)

class Cliente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=80)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_habitual = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    rut_cliente = models.CharField(max_length=12)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario