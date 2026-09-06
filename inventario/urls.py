from django.urls import path
from . import views

# Estas rutas asignan cada URL pública a una vista y le dan un nombre reutilizable
# por las redirecciones y los enlaces de las plantillas.
urlpatterns = [
    # Productos
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/', views.producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    
    # Ventas
    path('ventas/', views.venta_list, name='venta_list'),
    path('ventas/nuevo/', views.venta_create, name='venta_create'),
]
