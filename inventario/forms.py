import re
from django import forms
from .models import Cliente, Venta, DetalleVenta, Producto

# ModelForm reutiliza la definición del modelo para validar y guardar productos,
# mientras labels y widgets adaptan los controles al lenguaje de la interfaz.
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'stock']
        labels = {
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
    # Este formulario reúne los datos de la boleta, el cliente y sus líneas de productos.
    cliente_rut = forms.CharField(max_length=12, label='RUT del cliente')
    es_habitual = forms.BooleanField(required=False, label='¿Cliente habitual?')
    nombre = forms.CharField(max_length=80, required=False, label='Nombre completo')
    correo = forms.EmailField(required=False, label='Correo electrónico')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        productos_disponibles = Producto.objects.filter(stock__gt=0)
        self.productos_disponibles = productos_disponibles.count()
        indices = {1}
        data = kwargs.get('data')
        if data:
            for key in data:
                match = re.fullmatch(r'(?:producto|cantidad)_(\d+)', key)
                if match:
                    indices.add(int(match.group(1)))

        self.lineas = []
        for index in sorted(indices):
            producto = forms.ModelChoiceField(
                queryset=productos_disponibles,
                label='Producto',
                required=False,
            )
            cantidad = forms.IntegerField(min_value=1, required=False, label='Cantidad')
            self.fields[f'producto_{index}'] = producto
            self.fields[f'cantidad_{index}'] = cantidad
            self.lineas.append({
                'index': index,
                'producto': self[f'producto_{index}'],
                'cantidad': self[f'cantidad_{index}'],
            })

    def clean(self):
        # La validación cruzada evita líneas incompletas y productos repetidos
        # antes de llegar a la vista.
        cleaned_data = super().clean()
        productos_seleccionados = []
        for linea in self.lineas:
            index = linea['index']
            producto = cleaned_data.get(f'producto_{index}')
            cantidad = cleaned_data.get(f'cantidad_{index}')
            if producto and not cantidad:
                self.add_error(f'cantidad_{index}', 'Indique la cantidad.')
            if cantidad and not producto:
                self.add_error(f'producto_{index}', 'Seleccione un producto.')
            if producto:
                if producto.pk in productos_seleccionados:
                    self.add_error(
                        f'producto_{index}',
                        'Este producto ya fue agregado a la venta.',
                    )
                else:
                    productos_seleccionados.append(producto.pk)
        if len(productos_seleccionados) > self.productos_disponibles:
            raise forms.ValidationError(
                'La venta no puede contener más productos que los disponibles.'
            )
        return cleaned_data