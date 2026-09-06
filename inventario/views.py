from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import ProductoForm
from django.views.decorators.csrf import csrf_protect

from django.contrib import messages
from .forms import ClienteForm, VentaForm
from .models import Cliente, Venta, DetalleVenta
from django.db import transaction
import re

# Las vistas coordinan la petición HTTP, los formularios, los modelos y las plantillas.
# Reciben datos del navegador, aplican reglas de negocio y devuelven HTML o redirecciones.


# READ (List)
def producto_list(request):
    # Consulta todos los productos y los entrega a la tabla del inventario.
    productos = Producto.objects.all()
    return render(request, 'inventario/producto_list.html', {'object_list': productos})


# READ (Detail)
def producto_detail(request, pk):
    # Busca un producto por clave primaria; si no existe devuelve automáticamente 404.
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'inventario/producto_detail.html', {'object': producto})


# CREATE
@csrf_protect
def producto_create(request):
    # GET muestra el formulario vacío; POST valida y persiste el producto mediante ModelForm.
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {'form': form})


# UPDATE
@csrf_protect
def producto_update(request, pk):
    # Recupera el producto existente y reutiliza el mismo formulario para actualizarlo.
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        
        if form.is_valid():
            form.save()
            return redirect('producto_list')
        
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {'form': form})


# DELETE
@csrf_protect
def producto_delete(request, pk):
    # GET pide confirmación y POST elimina; el token CSRF protege la operación destructiva.
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.delete()
        return redirect('producto_list')
    
    return render(
        request, 'inventario/producto_confirm_delete.html', {'object': producto}
    )

# ========== CLIENTES ==========
def cliente_list(request):
    # Obtiene los clientes habituales para mostrarlos en el directorio.
    clientes = Cliente.objects.all()
    return render(request, 'inventario/cliente_list.html', {'clientes': clientes})

@csrf_protect
def cliente_create(request):
    # Registra datos de un cliente habitual y comunica el resultado con messages de Django.
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'inventario/cliente_form.html', {'form': form})

# ========== VENTAS ==========
@csrf_protect
def venta_create(request):
    # Coordina toda la venta: valida RUT, decide si persiste al cliente, verifica productos,
    # descuenta stock y crea la venta junto con sus detalles dentro de una transacción.
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['cliente_rut']
            es_habitual = form.cleaned_data['es_habitual']
            
            # El RUT se valida antes de crear datos o modificar existencias.
            if not validar_rut(rut):
                messages.error(request, 'RUT inválido. Debe tener formato 12345678-9 o 123456789.')
                return render(request, 'inventario/venta_form.html', {'form': form, 'productos': productos})
            
            # Un habitual se crea o actualiza; un ocasional solo conserva su RUT en la venta.
            if es_habitual:
                nombre = form.cleaned_data.get('nombre')
                correo = form.cleaned_data.get('correo')
                telefono = form.cleaned_data.get('telefono')
                if not nombre or not correo or not telefono:
                    messages.error(request, 'Para clientes habituales debe completar nombre, correo y teléfono.')
                    return render(request, 'inventario/venta_form.html', {'form': form, 'productos': productos})
                cliente, created = Cliente.objects.get_or_create(
                    rut=rut,
                    defaults={'nombre': nombre, 'correo': correo, 'telefono': telefono, 'es_habitual': True}
                )
                if not created:
                    # Actualiza datos por si el cliente habitual los corrigió.
                    cliente.nombre = nombre
                    cliente.correo = correo
                    cliente.telefono = telefono
                    cliente.es_habitual = True
                    cliente.save()
            else:
                # El RUT ocasional queda en la boleta, no crea un cliente persistente.
                cliente = Cliente.objects.filter(rut=rut, es_habitual=True).first()
            
            # Recorre las tres líneas posibles y conserva solo las completas.
            items = []
            for i in range(1, 4):
                prod = form.cleaned_data.get(f'producto_{i}')
                cant = form.cleaned_data.get(f'cantidad_{i}')
                if prod and cant:
                    items.append((prod, cant))
            
            if not items:
                messages.error(request, 'Debe seleccionar al menos un producto con cantidad.')
                return render(request, 'inventario/venta_form.html', {'form': form, 'productos': productos})
            
            # La transacción garantiza que stock, venta y detalles se guarden juntos
            # o se reviertan completamente si una validación falla.
            total = 0
            detalles = []
            with transaction.atomic():
                for producto, cantidad in items:
                    if producto.stock < cantidad:
                        messages.error(request, f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}')
                        return render(request, 'inventario/venta_form.html', {'form': form, 'productos': productos})
                    # Descuenta existencias antes de guardar el detalle vendido.
                    producto.stock -= cantidad
                    producto.save()
                    # Guarda una fotografía del producto y del precio usado en la venta.
                    detalles.append({
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_unitario': producto.precio,
                        'subtotal': cantidad * producto.precio
                    })
                    total += cantidad * producto.precio
                
                # La venta almacena el total y el RUT que aparecerá en la boleta.
                venta = Venta.objects.create(cliente=cliente, rut_cliente=rut, total=total)
                
                # Cada línea se convierte en un DetalleVenta relacionado con la venta.
                for det in detalles:
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=det['producto'],
                        cantidad=det['cantidad'],
                        precio_unitario=det['precio_unitario']
                    )
            
            messages.success(request, f'Venta #{venta.id} registrada con éxito. Total: ${total}')
            return redirect('venta_list')
    
    else:
        form = VentaForm()
    
    return render(request, 'inventario/venta_form.html', {'form': form, 'productos': productos})


def validar_rut(rut):
    # Normaliza puntos y guion, comprueba la estructura chilena y calcula el dígito
    # verificador mediante módulo 11. Devuelve True solo si ambos coinciden.
    rut_limpio = rut.replace('.', '').replace('-', '').strip().upper()
    if not re.fullmatch(r'\d{7,8}[0-9K]', rut_limpio):
        return False

    cuerpo, digito = rut_limpio[:-1], rut_limpio[-1]
    suma = 0
    multiplicador = 2
    for numero in reversed(cuerpo):
        suma += int(numero) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    return digito == esperado

def venta_list(request):
    # Ordena las ventas desde la más reciente para construir el historial de caja.
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'inventario/venta_list.html', {'ventas': ventas})