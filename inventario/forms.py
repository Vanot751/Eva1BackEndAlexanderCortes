from django import forms
from .models import Cliente, Venta, DetalleVenta, Producto

# ModelForm reutiliza la definición del modelo para validar y guardar productos,
# mientras labels y widgets adaptan los controles al lenguaje de la interfaz.
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'precio', 'descripcion', 'stock']
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del producto',
            'precio': 'Precio de venta',
            'descripcion': 'Descripción',
            'stock': 'Stock inicial',
        }
        widgets = {
            'precio': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': 0}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'nombre', 'correo', 'telefono', 'es_habitual']
        labels = {
            'rut': 'RUT',
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono',
            'es_habitual': 'Cliente habitual',
        }

class VentaForm(forms.Form):
    # Este formulario no crea una Venta directamente: reúne los datos de la boleta,
    # el cliente y hasta tres líneas de productos para que venta_create los procese.
    cliente_rut = forms.CharField(max_length=12, label='RUT del cliente')
    es_habitual = forms.BooleanField(required=False, label='¿Cliente habitual?')
    nombre = forms.CharField(max_length=80, required=False, label='Nombre completo')
    correo = forms.EmailField(required=False, label='Correo electrónico')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    
    # Cada pareja producto/cantidad representa una línea opcional de la venta.
    producto_1 = forms.ModelChoiceField(queryset=Producto.objects.all(), label='Producto 1', required=False)
    cantidad_1 = forms.IntegerField(min_value=1, required=False, label='Cantidad 1')
    producto_2 = forms.ModelChoiceField(queryset=Producto.objects.all(), label='Producto 2', required=False)
    cantidad_2 = forms.IntegerField(min_value=1, required=False, label='Cantidad 2')
    producto_3 = forms.ModelChoiceField(queryset=Producto.objects.all(), label='Producto 3', required=False)
    cantidad_3 = forms.IntegerField(min_value=1, required=False, label='Cantidad 3')

    def clean(self):
        # La validación cruzada evita líneas incompletas antes de llegar a la vista:
        # si existe producto debe existir cantidad y viceversa.
        cleaned_data = super().clean()
        for index in range(1, 4):
            producto = cleaned_data.get(f'producto_{index}')
            cantidad = cleaned_data.get(f'cantidad_{index}')
            if producto and not cantidad:
                self.add_error(f'cantidad_{index}', 'Indique la cantidad.')
            if cantidad and not producto:
                self.add_error(f'producto_{index}', 'Seleccione un producto.')
        return cleaned_data