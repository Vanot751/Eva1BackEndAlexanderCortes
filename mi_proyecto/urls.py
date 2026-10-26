from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Branding del Admin
admin.site.site_header = "Panel Interno — Mercado Menta"
admin.site.site_title = "Admin Mercado Menta"
admin.site.index_title = "Operaciones"

# El proyecto delega las rutas de negocio a inventario y conserva /admin/ para Django.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventario.urls')),
    path("api-auth/", include("rest_framework.urls")),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

