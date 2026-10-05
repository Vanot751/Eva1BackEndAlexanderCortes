import csv
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Producto, Cliente, Venta, DetalleVenta


class RangoStockFilter(SimpleListFilter):
    """
    Filtro avanzado para segmentar los productos del inventario
    según rangos de existencias (stock).
    """
    title = 'Rango de stock'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return (
            ('sin', 'Sin stock (0)'),
            ('bajo', 'Stock bajo (1 a 10)'),
            ('medio', 'Stock medio (11 a 50)'),
            ('alto', 'Stock alto (Más de 50)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sin':
            return queryset.filter(stock=0)
        if self.value() == 'bajo':
            return queryset.filter(stock__gt=0, stock__lte=10)
        if self.value() == 'medio':
            return queryset.filter(stock__gte=11, stock__lte=50)
        if self.value() == 'alto':
            return queryset.filter(stock__gt=50)
        return queryset


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion', 'precio', 'stock')
    list_editable = ('nombre', 'descripcion', 'precio')
    search_fields = ('codigo', 'nombre')
    list_filter = (RangoStockFilter,)
    list_per_page = 25
    fieldsets = (
        ('Datos básicos', {
            'fields': ('codigo', 'nombre', 'descripcion', 'precio')
        }),
        ('Inventario', {
            'fields': ('stock',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Lógica al guardar: Ejemplo de auditoría o ajuste
        super().save_model(request, obj, form, change)
        
    def has_delete_permission(self, request, obj=None):
        # Permisos: limita acciones según rol (solo superusuarios pueden eliminar productos)
        return request.user.is_superuser


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'correo', 'es_habitual')
    search_fields = ('nombre', 'rut', 'correo')
    list_filter = ('es_habitual',)
    list_per_page = 25


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ("producto",)
    readonly_fields = ("subtotal",)

    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            prod = form.cleaned_data.get('producto')
            cant = form.cleaned_data.get('cantidad')
            if prod and cant and cant > prod.stock:
                raise ValidationError(f"Stock insuficiente para {prod.nombre} (disponible: {prod.stock}).")


@admin.action(description="Exportar ventas a CSV")
def exportar_ventas_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Cliente (RUT)", "Fecha", "Total"])
    # Optimizamos listado con select_related y prefetch_related
    for v in queryset.select_related('cliente').prefetch_related('detalles__producto'):
        writer.writerow([v.id, v.rut_cliente, v.fecha.strftime("%Y-%m-%d %H:%M"), v.total])
    return response


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    date_hierarchy = "fecha"
    list_display = ('id', 'rut_cliente', 'cliente', 'fecha', 'total_display')
    search_fields = ('rut_cliente', 'cliente__nombre', 'id')
    inlines = [DetalleVentaInline]
    actions = [exportar_ventas_csv]

    @admin.display(description="Total", ordering="total")
    def total_display(self, obj):
        return f"${obj.total:,.0f}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cliente')
