from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Producto


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


# Alias para compatibilidad con la guía de clases
StockBajoFilter = RangoStockFilter


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'stock')
    search_fields = ('codigo', 'nombre')
    list_filter = (RangoStockFilter,)

